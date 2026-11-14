#!/usr/bin/env python3
"""
Validate the FLARE-X measurement pipeline against exact ground truth.

WHAT THIS SCRIPT MEASURES
    Whether the code does what it says: segmentation agreement (IoU, Dice),
    change-point detection against known commanded step frames, and whether
    the extinction proximity index responds in the expected direction.

WHAT THIS SCRIPT DOES NOT MEASURE
    Anything about real flames. The input is a synthetic phantom with an
    invented appearance model. Every metric below is a property of the
    software, not of microgravity combustion.

    Validation on archived NASA imagery is a separate, scripted step that
    requires a PSI account: see scripts/acquire_psi.py and VALIDATION.md
    section "Stage 2".

Usage:
    python scripts/validate_pipeline.py [--out reports/validation_phantom.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

from flarex import (DuctGeometry, RunMetadata, SegmentationConfig,  # noqa: E402
                    align_to_reference_events, analyse_run,
                    validate_monotonicity)
from flarex.phantom import (PhantomConfig, dice, generate_phantom_run,  # noqa: E402
                            iou, SYNTHETIC_LABEL)
from flarex.segmentation import estimate_background, segment_flame  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "reports" / "validation_phantom.json"))
    ap.add_argument("--seed", type=int, default=20261114)
    args = ap.parse_args()

    cfg = PhantomConfig(seed=args.seed)
    run = generate_phantom_run(cfg)
    print(f"Phantom: {run.n_frames} frames, "
          f"{len(run.step_change_frames)} commanded flow steps, "
          f"extinction at frame {run.extinction_frame}")

    seg_cfg = SegmentationConfig(
        exclude_regions=(cfg.overlay_box,),   # the burned-in telemetry strip
        min_object_px=60,
    )

    # ---- Stage 1a: segmentation agreement, per frame -----------------------
    background = estimate_background(run.frames, percentile=seg_cfg.background_percentile)
    ious, dices, fp_on_empty = [], [], 0
    below_limit = []          # true flames smaller than the detector can resolve
    missed_above_limit = []   # true flames above the limit that were still missed
    for i in range(run.n_frames):
        res = segment_flame(run.frames[i], background=background, config=seg_cfg)
        truth = run.truth_masks[i]
        true_px = int(truth.sum())
        if true_px:
            if true_px < seg_cfg.min_object_px:
                # Honest accounting: a flame smaller than min_object_px is below
                # the detector's stated size limit. Scoring it as a segmentation
                # failure would misattribute a declared detection limit to an
                # algorithm error. It is counted and reported separately.
                below_limit.append((i, true_px))
                continue
            if not res.mask.any():
                missed_above_limit.append((i, true_px))
            ious.append(iou(res.mask, truth))
            dices.append(dice(res.mask, truth))
        elif res.mask.any():
            fp_on_empty += 1

    ious_a = np.array(ious) if ious else np.array([np.nan])
    dices_a = np.array(dices) if dices else np.array([np.nan])

    # ---- Stage 1b: the overlay trap ---------------------------------------
    # Re-run without the exclusion region to show what the burned-in telemetry
    # strip does to a segmenter that has not been told about it.
    naive_cfg = SegmentationConfig(min_object_px=60)
    naive_ious = []
    for i in range(0, run.n_frames, 5):
        if not run.truth_masks[i].any():
            continue
        res = segment_flame(run.frames[i], background=background, config=naive_cfg)
        naive_ious.append(iou(res.mask, run.truth_masks[i]))
    naive_a = np.array(naive_ious) if naive_ious else np.array([np.nan])

    # ---- Stage 1c: full pipeline, change points and EPI --------------------
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
    geo = DuctGeometry(
        flow_angle_deg=0.0,
        surface_point=(float(cfg.flame_anchor_x),
                       float(cfg.rod_y - cfg.rod_half_thickness)),
        surface_angle_deg=0.0,
        mm_per_px=None,
    )
    result = analyse_run(run.frames, meta, geometry=geo, seg_config=seg_cfg)

    epi_check = validate_monotonicity(result.epi.epi, run.commanded_flow_cm_s)

    # ---- Stage 1d: does the index lead the loss of flame? ------------------
    live = np.where(result.present)[0]
    last_live = int(live[-1]) if live.size else None
    epi_at_last_live = (float(result.epi.epi[last_live])
                        if last_live is not None and np.isfinite(result.epi.epi[last_live])
                        else float("nan"))
    epi_early = (float(np.nanmedian(result.epi.epi[:cfg.dwell_frames]))
                 if result.epi.epi.size else float("nan"))

    # Reference events: the commanded flow steps PLUS the two physical events
    # that a flow-step list does not contain. Scoring change points against the
    # flow steps alone would charge the detector with false positives for
    # correctly finding ignition and extinction.
    physical_events = [cfg.ignition_frames, run.extinction_frame]
    all_events = sorted(set(run.step_change_frames) | set(physical_events))
    alignment_all = align_to_reference_events(result.change_points, all_events,
                                              tolerance=6)

    report = {
        "WARNING": SYNTHETIC_LABEL,
        "what_these_numbers_are": (
            "Software accuracy against an exactly known synthetic target. "
            "They are not combustion results and must never be presented as "
            "measurements of microgravity flames."),
        "phantom": {
            "n_frames": run.n_frames,
            "fps": cfg.fps,
            "frame_size": [cfg.height, cfg.width],
            "commanded_flow_steps_cm_s": list(cfg.flow_steps_cm_s),
            "true_step_frames": run.step_change_frames,
            "true_extinction_frame": run.extinction_frame,
            "seed": args.seed,
        },
        "segmentation": {
            "detection_size_limit_px": seg_cfg.min_object_px,
            "frames_below_detection_size_limit": [
                {"frame": i, "true_area_px": a} for i, a in below_limit],
            "frames_missed_above_size_limit": [
                {"frame": i, "true_area_px": a} for i, a in missed_above_limit],
            "n_frames_scored": int(ious_a.size),
            "iou_mean": float(np.nanmean(ious_a)),
            "iou_median": float(np.nanmedian(ious_a)),
            "iou_p05": float(np.nanpercentile(ious_a, 5)),
            "iou_min": float(np.nanmin(ious_a)),
            "dice_mean": float(np.nanmean(dices_a)),
            "dice_median": float(np.nanmedian(dices_a)),
            "false_positive_frames_when_no_flame": int(fp_on_empty),
            "ablation_no_overlay_exclusion": {
                "n_frames_scored": int(naive_a.size),
                "iou_mean": float(np.nanmean(naive_a)),
                "interpretation": (
                    "Segmentation with the burned-in telemetry strip left in the "
                    "field of view. The gap against the masked result is the cost "
                    "of ignoring an artefact that is present in the real archived "
                    "video."),
            },
        },
        "change_point_detection": {
            "detected": result.change_points,
            "alignment_to_commanded_flow_steps_only": result.step_alignment,
            "alignment_to_all_known_events": alignment_all,
            "known_physical_events_added": {
                "ignition_frame": cfg.ignition_frames,
                "extinction_frame": run.extinction_frame},
            "note": ("Reference events are the exact frames at which the phantom's "
                     "commanded flow changed. On archived BASS-II video the "
                     "equivalent reference comes from the burned-in anemometer and "
                     "fan-voltage overlay and from the test record."),
        },
        "states": [{"start": s.start_index, "end": s.end_index,
                    "state": s.state.value, "note": s.note} for s in result.states],
        "extinction_proximity_index": {
            "weights": result.epi.weights,
            "dropped_terms": result.epi.dropped_terms,
            "monotonicity_check_vs_commanded_flow": epi_check,
            "epi_median_first_dwell": epi_early,
            "epi_at_last_frame_with_flame": epi_at_last_live,
            "disclaimer": result.epi.disclaimer,
        },
        "segmentation_uncertainty_sweep": result.segmentation_uncertainty,
        "pipeline_warnings": result.warnings,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))

    print("\n--- SEGMENTATION (synthetic ground truth) ---")
    print(f"  frames scored     : {ious_a.size}")
    print(f"  IoU  mean/median  : {np.nanmean(ious_a):.4f} / {np.nanmedian(ious_a):.4f}")
    print(f"  IoU  5th pct/min  : {np.nanpercentile(ious_a,5):.4f} / {np.nanmin(ious_a):.4f}")
    print(f"  Dice mean/median  : {np.nanmean(dices_a):.4f} / {np.nanmedian(dices_a):.4f}")
    print(f"  false positives on empty frames: {fp_on_empty}")
    print(f"  IoU without overlay masking    : {np.nanmean(naive_a):.4f}")
    print(f"  frames below the {seg_cfg.min_object_px}px detection size limit: "
          f"{len(below_limit)} (excluded from IoU, reported separately)")
    print(f"  frames missed despite being above the limit: {len(missed_above_limit)}")
    print("\n--- CHANGE POINTS vs FLOW STEPS ONLY ---")
    for k, v in (result.step_alignment or {}).items():
        print(f"  {k}: {v}")
    print("--- CHANGE POINTS vs FLOW STEPS + IGNITION + EXTINCTION ---")
    for k, v in alignment_all.items():
        print(f"  {k}: {v}")
    print("\n--- EPI ---")
    print(f"  weights: {result.epi.weights}")
    print(f"  monotonicity vs flow: rho={epi_check['spearman_rho']:.3f} "
          f"({epi_check['status']})")
    print(f"  EPI first dwell -> last live frame: {epi_early:.3f} -> {epi_at_last_live:.3f}")
    print(f"\nWritten: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
