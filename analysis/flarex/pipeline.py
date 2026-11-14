"""
flarex.pipeline
===============

End-to-end orchestration: frames in, traceable analysis out.

    frames
      -> background estimate
      -> per-frame segmentation            (flarex.segmentation)
      -> per-frame morphology              (flarex.morphology)
      -> multivariate change points        (flarex.timeseries)
      -> combustion states                 (flarex.timeseries)
      -> extinction proximity index        (flarex.extinction)
      -> uncertainty budget                (flarex.uncertainty)
      -> provenance chain on every output  (flarex.provenance)

The orchestrator is deliberately thin. All science lives in the modules
above, each of which can be imported and used on its own; removing the
web application, the API and any language model leaves the analysis fully
intact and runnable from a script. That is a design requirement, not an
accident.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from .extinction import EPIConfig, EPIResult, compute_epi
from .morphology import DuctGeometry, FlameFeatures, extract_features
from .provenance import (ClaimLevel, Measurement, ProvenanceChain,
                         ProvenanceNode, PIPELINE_VERSION)
from .segmentation import (SegmentationConfig, estimate_background,
                           segment_flame, sweep_threshold_sensitivity)
from .timeseries import (StateRules, detect_change_points, label_states,
                         align_to_reference_events)
from .uncertainty import area_budget

__all__ = ["RunMetadata", "RunResult", "analyse_run"]


@dataclass
class RunMetadata:
    """Everything known about the source of these frames, before analysis.

    Fields left as None are reported as unknown in the provenance viewer.
    They are never filled with plausible-looking defaults.
    """

    repository: str = "UNKNOWN"
    investigation: str = "UNKNOWN"
    test_id: str = "UNKNOWN"
    source_file: str | None = None
    source_digest: str | None = None
    doi: str | None = None
    landing_page: str | None = None
    fuel: str | None = None
    fuel_geometry: str | None = None
    oxygen_volume_fraction: float | None = None
    oxygen_uncertainty: float | None = None
    pressure_kpa: float | None = None
    gravity_condition: str | None = None
    fps: float | None = None
    mm_per_px: float | None = None
    mm_per_px_relative_uncertainty: float | None = None
    commanded_flow_cm_s: Sequence[float] | None = None
    reference_step_frames: Sequence[int] | None = None
    is_synthetic: bool = False
    notes: str = ""

    def base_chain(self) -> ProvenanceChain:
        nodes = [ProvenanceNode("repository", self.repository,
                                detail="synthetic phantom" if self.is_synthetic else "",
                                uri=self.landing_page),
                 ProvenanceNode("investigation", self.investigation, uri=self.doi),
                 ProvenanceNode("test", self.test_id)]
        if self.source_file:
            nodes.append(ProvenanceNode("file", Path(self.source_file).name,
                                        digest=self.source_digest))
        return ProvenanceChain(nodes)


@dataclass
class RunResult:
    metadata: RunMetadata
    features: list[FlameFeatures | None]
    present: np.ndarray
    time_s: np.ndarray
    change_points: list[int]
    states: list
    epi: EPIResult
    segmentation_uncertainty: dict[str, float]
    measurements: list[Measurement] = field(default_factory=list)
    step_alignment: dict[str, float] | None = None
    warnings: list[str] = field(default_factory=list)

    def feature_series(self, name: str) -> np.ndarray:
        out = np.full(len(self.features), np.nan)
        for i, f in enumerate(self.features):
            if f is not None:
                v = getattr(f, name, None)
                if v is not None:
                    out[i] = float(v)
        return out

    def to_json(self) -> str:
        return json.dumps(self.summary(), indent=2, default=str)

    def summary(self) -> dict[str, Any]:
        return {
            "pipeline_version": PIPELINE_VERSION,
            "metadata": self.metadata.__dict__,
            "n_frames": len(self.features),
            "n_frames_with_flame": int(self.present.sum()),
            "change_points": self.change_points,
            "states": [{"start": s.start_index, "end": s.end_index,
                        "state": s.state.value, "evidence": s.evidence,
                        "note": s.note} for s in self.states],
            "epi_weights": self.epi.weights,
            "epi_dropped_terms": self.epi.dropped_terms,
            "epi_disclaimer": self.epi.disclaimer,
            "segmentation_uncertainty": self.segmentation_uncertainty,
            "step_alignment": self.step_alignment,
            "measurements": [m.to_dict() for m in self.measurements],
            "warnings": self.warnings,
        }


def analyse_run(frames: Sequence[np.ndarray],
                metadata: RunMetadata,
                geometry: DuctGeometry | None = None,
                seg_config: SegmentationConfig | None = None,
                epi_config: EPIConfig | None = None,
                state_rules: StateRules | None = None,
                change_point_beta: float = 2.0,
                alignment_tolerance_frames: int = 6) -> RunResult:
    """Run the full analysis over a frame sequence."""
    warnings: list[str] = []
    fps = metadata.fps or 15.0
    if metadata.fps is None:
        warnings.append("Frame rate not supplied; assumed 15 fps for the time axis. "
                        "All times and rates are therefore provisional.")

    geo = geometry or DuctGeometry(mm_per_px=metadata.mm_per_px)
    if geo.mm_per_px is None:
        warnings.append("Image scale (mm/px) unknown: all lengths and areas are "
                        "reported in pixels and are not physical measurements.")

    background = estimate_background(frames,
                                     percentile=(seg_config or SegmentationConfig()
                                                 ).background_percentile)

    features: list[FlameFeatures | None] = []
    for i, frame in enumerate(frames):
        seg = segment_flame(frame, background=background, config=seg_config)
        if seg.is_empty:
            features.append(None)
            continue
        features.append(extract_features(seg.mask, seg.radiance, frame_rgb=frame,
                                         geometry=geo, frame_index=i,
                                         time_s=i / fps))

    present = np.array([f is not None for f in features], dtype=bool)
    time_s = np.arange(len(frames)) / fps

    def series(name: str) -> np.ndarray:
        out = np.full(len(features), np.nan)
        for i, f in enumerate(features):
            if f is not None:
                v = getattr(f, name, None)
                if v is not None:
                    out[i] = float(v)
        return out

    area = series("area")
    aspect = series("aspect_ratio")
    standoff = series("standoff")
    radiance = series("radiance_mean")
    chi = series("sootiness_index")

    # Joint change-point detection. Using several features together is what
    # makes the detected boundaries stable enough to compare against the
    # commanded flow steps.
    cp_stack = np.column_stack([
        np.nan_to_num(area, nan=np.nanmedian(area) if np.isfinite(area).any() else 0.0),
        np.nan_to_num(aspect, nan=np.nanmedian(aspect) if np.isfinite(aspect).any() else 0.0),
        np.nan_to_num(radiance, nan=np.nanmedian(radiance) if np.isfinite(radiance).any() else 0.0),
    ])
    change_points = detect_change_points(cp_stack, beta=change_point_beta)

    states = label_states(area, time_s, change_points=change_points,
                          present=present, rules=state_rules)

    epi = compute_epi(
        {"area": area, "aspect_ratio": aspect, "standoff": standoff,
         "radiance_mean": radiance, "sootiness_index": chi},
        config=epi_config,
        provenance_note=f"{metadata.investigation} / {metadata.test_id}",
    )

    # segmentation uncertainty from a real sweep on a representative live frame
    live = np.where(present)[0]
    if live.size:
        probe = int(live[len(live) // 2])
        seg_unc = sweep_threshold_sensitivity(frames[probe], background=background,
                                              config=seg_config)
    else:
        seg_unc = {"status": "no frame with a detected flame"}
        warnings.append("No flame detected in any frame; check exclusion regions "
                        "and thresholds before interpreting this run.")

    step_alignment = None
    if metadata.reference_step_frames:
        step_alignment = align_to_reference_events(
            change_points, metadata.reference_step_frames,
            tolerance=alignment_tolerance_frames)

    measurements: list[Measurement] = []
    chain = metadata.base_chain()
    if live.size:
        f = features[probe]
        rel = seg_unc.get("area_relative_cv", float("nan"))
        budget = area_budget(
            area_value=f.area, area_px=float(f.n_pixels),
            seg_relative=rel if np.isfinite(rel) else 0.0,
            mm_per_px_relative=metadata.mm_per_px_relative_uncertainty,
            single_view=True)
        measurements.append(Measurement(
            name=f"projected flame area at frame {probe}",
            value=float(f.area),
            unit="mm^2" if f.scaled else "px^2",
            level=ClaimLevel.L3_MEASURED,
            provenance=chain.then(ProvenanceNode("frame", f"frame_{probe:06d}"))
                            .then(ProvenanceNode("method", "segmentation",
                                                 detail="hysteresis on max-RGB radiance proxy"))
                            .then(ProvenanceNode("method", "morphology",
                                                 detail="regionprops + flow-axis extents")),
            uncertainty=budget.combined_absolute,
            uncertainty_kind="segmentation_threshold_sweep",
            note=budget.render(),
        ))

    if metadata.is_synthetic:
        warnings.insert(0, "SYNTHETIC RUN: these outputs measure pipeline accuracy "
                           "only and carry no combustion findings.")

    return RunResult(metadata=metadata, features=features, present=present,
                     time_s=time_s, change_points=change_points, states=states,
                     epi=epi, segmentation_uncertainty=seg_unc,
                     measurements=measurements, step_alignment=step_alignment,
                     warnings=warnings)
