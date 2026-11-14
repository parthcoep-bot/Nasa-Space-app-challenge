#!/usr/bin/env python3
"""
Build the JSON payload the FLARE-X web interface reads.

The interface contains no science. It renders what this script computes, so
that anyone can regenerate the displayed numbers from the pipeline and check
them. Running it on the phantom produces a payload labelled SYNTHETIC
throughout; running it on archived video (via run_analysis.py) produces the
same structure with real provenance.

Usage:
    python scripts/build_webapp_payload.py --out frontend/payload.json
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

from flarex import (DuctGeometry, RunMetadata, SegmentationConfig,  # noqa: E402
                    analyse_run, validate_monotonicity, DEFAULT_TERMS)
from flarex.phantom import (PhantomConfig, generate_phantom_run,  # noqa: E402
                            SYNTHETIC_LABEL, iou, dice)
from flarex.segmentation import estimate_background, segment_flame  # noqa: E402
from flarex import physics  # noqa: E402


def _png_b64(rgb: np.ndarray, scale: float = 0.5) -> str:
    from PIL import Image
    img = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
    if scale != 1.0:
        img = img.resize((int(img.width * scale), int(img.height * scale)),
                         Image.BILINEAR)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def _contour_overlay(rgb: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Draw the segmentation boundary onto a copy of the frame."""
    from skimage.segmentation import find_boundaries
    out = np.clip(rgb.copy(), 0, 1)
    b = find_boundaries(mask, mode="outer")
    out[b] = [0.42, 0.64, 0.91]          # --chemi, the segmentation accent
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "frontend" / "payload.json"))
    ap.add_argument("--seed", type=int, default=20261114)
    ap.add_argument("--n-keyframes", type=int, default=8)
    args = ap.parse_args()

    cfg = PhantomConfig(seed=args.seed)
    run = generate_phantom_run(cfg)
    seg_cfg = SegmentationConfig(exclude_regions=(cfg.overlay_box,), min_object_px=60)

    meta = RunMetadata(
        repository="SYNTHETIC PHANTOM (flarex.phantom)",
        investigation="PHANTOM-OPPOSED-FLOW-STAIRCASE",
        test_id=f"phantom-seed-{args.seed}",
        gravity_condition="n/a (synthetic)",
        fps=cfg.fps,
        commanded_flow_cm_s=run.commanded_flow_cm_s.tolist(),
        reference_step_frames=run.step_change_frames,
        is_synthetic=True,
        notes=SYNTHETIC_LABEL,
    )
    geo = DuctGeometry(flow_angle_deg=0.0,
                       surface_point=(float(cfg.flame_anchor_x),
                                      float(cfg.rod_y - cfg.rod_half_thickness)),
                       surface_angle_deg=0.0, mm_per_px=None)

    result = analyse_run(run.frames, meta, geometry=geo, seg_config=seg_cfg)
    background = estimate_background(run.frames, percentile=seg_cfg.background_percentile)

    def series(name):
        return [None if not np.isfinite(v) else round(float(v), 5)
                for v in result.feature_series(name)]

    # keyframes spread across the live portion, plus one after extinction
    live = np.where(result.present)[0]
    picks = list(np.linspace(live[0], live[-1], args.n_keyframes - 1).astype(int))
    picks.append(int(min(run.extinction_frame + 10, run.n_frames - 1)))

    keyframes = []
    for i in picks:
        segres = segment_flame(run.frames[i], background=background, config=seg_cfg)
        truth = run.truth_masks[i]
        f = result.features[i]
        keyframes.append({
            "frame": int(i),
            "time_s": round(float(i / cfg.fps), 3),
            "commanded_flow_cm_s": float(run.commanded_flow_cm_s[i]),
            "image": _png_b64(run.frames[i]),
            "overlay": _png_b64(_contour_overlay(run.frames[i], segres.mask)),
            "detected": bool(segres.mask.any()),
            "empty_reason": segres.empty_reason,
            "iou_vs_truth": None if not truth.any() else round(iou(segres.mask, truth), 4),
            "dice_vs_truth": None if not truth.any() else round(dice(segres.mask, truth), 4),
            "features": None if f is None else {
                "area_px": round(f.area, 1),
                "flame_length_px": round(f.flame_length, 1),
                "flame_width_px": round(f.flame_width, 1),
                "aspect_ratio": round(f.aspect_ratio, 3),
                "circularity": round(f.circularity, 3),
                "standoff_px": None if f.standoff is None else round(f.standoff, 1),
                "sootiness_index": round(f.sootiness_index, 3),
                "radiance_mean": round(f.radiance_mean, 4),
            },
            "epi": None if not np.isfinite(result.epi.epi[i]) else round(float(result.epi.epi[i]), 3),
            "epi_attribution": ([] if not np.isfinite(result.epi.epi[i])
                                else [{"term": t, "contribution": round(v, 4)}
                                      for t, v in result.epi.explain_frame(i, top_k=5)]),
        })

    # Physics Lab: two worked cases with every input stated
    props = {"beta_1_K": 1.0 / 300.0, "delta_T_K": 1200.0,
             "length_m": 0.0064, "kinematic_viscosity_m2_s": 1.5e-5}
    assump = ["Property values are order-of-magnitude inputs entered by the user for "
              "illustration, not measurements from the experiment. They are displayed "
              "so the reader can change them and see what changes."]
    gr_1g = physics.grashof(g_m_s2=physics.G_EARTH, assumptions=assump, **props)
    gr_ug = physics.grashof(g_m_s2=physics.G_EARTH * 1e-6, assumptions=assump, **props)
    ub_1g = physics.buoyant_velocity_scale(g_m_s2=physics.G_EARTH,
                                           beta_1_K=props["beta_1_K"],
                                           delta_T_K=props["delta_T_K"],
                                           length_m=props["length_m"])
    ub_ug = physics.buoyant_velocity_scale(g_m_s2=physics.G_EARTH * 1e-6,
                                           beta_1_K=props["beta_1_K"],
                                           delta_T_K=props["delta_T_K"],
                                           length_m=props["length_m"])
    re_2 = physics.reynolds(velocity_m_s=0.02, length_m=props["length_m"],
                            kinematic_viscosity_m2_s=props["kinematic_viscosity_m2_s"])

    try:
        physics.grashof(g_m_s2=physics.G_EARTH, beta_1_K=props["beta_1_K"])
        refusal = "no exception raised (unexpected)"
    except physics.MissingInput as e:
        refusal = str(e)

    validation = json.loads((ROOT / "reports" / "validation_phantom.json").read_text())
    registry = json.loads((ROOT / "data" / "registry" / "investigations.json").read_text())

    payload = {
        "banner": SYNTHETIC_LABEL,
        "status": {
            "instrument": "VALIDATED against exact synthetic ground truth",
            "scientific_result": "NONE YET - Stage 2 requires archived NASA video "
                                 "and an individual PSI registration",
            "pipeline_version": result.summary()["pipeline_version"],
        },
        "run": {
            "n_frames": run.n_frames,
            "fps": cfg.fps,
            "frame_size": [cfg.height, cfg.width],
            "commanded_flow_cm_s": run.commanded_flow_cm_s.tolist(),
            "flow_steps": list(cfg.flow_steps_cm_s),
            "true_step_frames": run.step_change_frames,
            "true_extinction_frame": run.extinction_frame,
            "detected_change_points": result.change_points,
            "time_s": [round(t, 3) for t in result.time_s.tolist()],
            "present": result.present.tolist(),
        },
        "series": {
            "area": series("area"),
            "aspect_ratio": series("aspect_ratio"),
            "standoff": series("standoff"),
            "radiance_mean": series("radiance_mean"),
            "sootiness_index": series("sootiness_index"),
            "flame_length": series("flame_length"),
            "flame_width": series("flame_width"),
            "circularity": series("circularity"),
            "epi": [None if not np.isfinite(v) else round(float(v), 4)
                    for v in result.epi.epi],
        },
        "states": [{"start": s.start_index, "end": s.end_index, "state": s.state.value,
                    "note": s.note, "evidence": {k: round(float(v), 5)
                                                 for k, v in s.evidence.items()}}
                   for s in result.states],
        "epi": {
            "weights": result.epi.weights,
            "dropped_terms": result.epi.dropped_terms,
            "disclaimer": result.epi.disclaimer,
            "terms": [{"feature": t.feature, "direction": t.direction,
                       "weight": t.weight, "rationale": t.rationale,
                       "source": t.source} for t in DEFAULT_TERMS],
            "monotonicity": validate_monotonicity(result.epi.epi,
                                                  run.commanded_flow_cm_s),
        },
        "keyframes": keyframes,
        "validation": validation,
        "uncertainty": {
            "segmentation_sweep": result.segmentation_uncertainty,
            "budget_example": result.measurements[0].note if result.measurements else None,
        },
        "physics": {
            "cases": [
                {"label": "Grashof, 1 g", **{"value": gr_1g.value, "formula": gr_1g.formula,
                                             "inputs": gr_1g.inputs,
                                             "interpretation": gr_1g.interpretation,
                                             "assumptions": gr_1g.assumptions}},
                {"label": "Grashof, 1e-6 g", "value": gr_ug.value, "formula": gr_ug.formula,
                 "inputs": gr_ug.inputs, "interpretation": gr_ug.interpretation,
                 "assumptions": gr_ug.assumptions},
                {"label": "Buoyant velocity scale, 1 g", "value": ub_1g.value,
                 "formula": ub_1g.formula, "inputs": ub_1g.inputs,
                 "interpretation": ub_1g.interpretation, "assumptions": ub_1g.assumptions},
                {"label": "Buoyant velocity scale, 1e-6 g", "value": ub_ug.value,
                 "formula": ub_ug.formula, "inputs": ub_ug.inputs,
                 "interpretation": ub_ug.interpretation, "assumptions": ub_ug.assumptions},
                {"label": "Reynolds at 2 cm/s over a 6.4 mm rod", "value": re_2.value,
                 "formula": re_2.formula, "inputs": re_2.inputs,
                 "interpretation": re_2.interpretation, "assumptions": re_2.assumptions},
            ],
            "ratios": {
                "grashof_1g_over_ug": gr_1g.value / gr_ug.value,
                "buoyant_velocity_1g_over_ug": ub_1g.value / ub_ug.value,
            },
            "refusal_demo": refusal,
            "published_buoyant_flow_cm_s": 30.0,
            "published_buoyant_flow_source":
                "Link et al. 2018, doi:10.1038/s41598-017-18398-4 (L2)",
        },
        "registry": registry,
        "provenance_example": ([m.to_dict() for m in result.measurements][0]
                               if result.measurements else None),
        "warnings": result.warnings,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, separators=(",", ":")))
    print(f"Payload written: {out} ({out.stat().st_size/1e6:.2f} MB)")
    print(f"  {len(keyframes)} keyframes, {run.n_frames} frames of series data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
