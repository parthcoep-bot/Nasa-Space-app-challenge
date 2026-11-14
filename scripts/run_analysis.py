#!/usr/bin/env python3
"""
Run the FLARE-X pipeline on archived NASA video.

This is the real-data entry point. It refuses to guess: if the image scale,
frame rate, flow schedule or overlay geometry are unknown, it says so, reports
in pixels and frames, and flags every affected quantity.

Usage:
  python scripts/run_analysis.py --investigation BASS-II --video data/raw/BASS-II/<file> \
      --fps 30 --overlay 0,0,760,34 --flow-angle 180 \
      --surface 470,300 --surface-angle 0 \
      --steps steps.csv --out reports/bass2_test.json

  --steps is a CSV with columns: frame,flow_cm_s   (from the burned-in telemetry
  overlay or the test record). Supplying it is what turns the change-point
  output from a description into a scored, falsifiable measurement.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))

from flarex import (DuctGeometry, RunMetadata, SegmentationConfig,  # noqa: E402
                    analyse_run, validate_monotonicity)
from flarex.provenance import file_digest  # noqa: E402

REGISTRY = ROOT / "data" / "registry" / "investigations.json"


def read_frames(path: Path, max_frames: int | None, stride: int) -> tuple[list, float | None]:
    import cv2
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise SystemExit(f"Could not open {path}. Supported by your OpenCV build?")
    fps = cap.get(cv2.CAP_PROP_FPS) or None
    if fps is not None and (fps <= 0 or fps > 1000):
        fps = None
    frames, i = [], 0
    while True:
        ok, bgr = cap.read()
        if not ok:
            break
        if i % stride == 0:
            frames.append(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
            if max_frames and len(frames) >= max_frames:
                break
        i += 1
    cap.release()
    return frames, fps


def parse_rect(s: str | None):
    if not s:
        return None
    v = [int(x) for x in s.split(",")]
    if len(v) != 4:
        raise SystemExit("--overlay expects x0,y0,x1,y1")
    return tuple(v)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--investigation", default="BASS-II")
    ap.add_argument("--video", required=True)
    ap.add_argument("--test-id", default=None)
    ap.add_argument("--fps", type=float, default=None,
                    help="Override the container frame rate. Omit to read it from the "
                         "file; if neither is available the run is flagged provisional.")
    ap.add_argument("--mm-per-px", type=float, default=None,
                    help="VIDEO camera scale. Do NOT pass the still camera's 34 px/mm: "
                         "they are different cameras. Omit and lengths stay in pixels.")
    ap.add_argument("--mm-per-px-rel-unc", type=float, default=None)
    ap.add_argument("--overlay", default=None, help="x0,y0,x1,y1 telemetry strip to mask")
    ap.add_argument("--igniter", default=None, help="x0,y0,x1,y1 igniter coil to mask")
    ap.add_argument("--flow-angle", type=float, default=180.0)
    ap.add_argument("--surface", default=None, help="x,y point on the fuel surface line")
    ap.add_argument("--surface-angle", type=float, default=None)
    ap.add_argument("--steps", default=None, help="CSV: frame,flow_cm_s")
    ap.add_argument("--oxygen", type=float, default=None, help="O2 volume fraction")
    ap.add_argument("--fuel", default=None)
    ap.add_argument("--max-frames", type=int, default=None)
    ap.add_argument("--stride", type=int, default=1)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    video = Path(args.video)
    if not video.exists():
        raise SystemExit(f"{video} not found. FLARE-X ships no NASA data; see "
                         "scripts/acquire_psi.py and DATA_SOURCES.md.")

    reg = json.loads(REGISTRY.read_text())
    inv = next((i for i in reg["investigations"]
                if i["id"].upper() == args.investigation.upper()), None)
    if inv is None:
        raise SystemExit(f"Unknown investigation {args.investigation!r}")

    frames, container_fps = read_frames(video, args.max_frames, args.stride)
    if not frames:
        raise SystemExit("No frames decoded.")
    print(f"Decoded {len(frames)} frames at stride {args.stride}, "
          f"size {frames[0].shape[1]}x{frames[0].shape[0]}")

    fps = args.fps or (container_fps / args.stride if container_fps else None)
    if args.fps is None and container_fps:
        print(f"Frame rate {container_fps:g} read from the container.")
    elif fps is None:
        print("Frame rate UNKNOWN. Time axis will be provisional and flagged.")

    ref_frames, flows = None, None
    if args.steps:
        rows = list(csv.DictReader(open(args.steps)))
        ref_frames = [int(r["frame"]) // args.stride for r in rows]
        flows = [float(r["flow_cm_s"]) for r in rows]
        print(f"Loaded {len(ref_frames)} commanded flow steps as an independent "
              "reference for change-point scoring.")
    else:
        print("No --steps supplied. Change points will be reported but NOT SCORED. "
              "Without an independent reference they are a description, not a "
              "falsifiable measurement.")

    exclusions = tuple(r for r in (parse_rect(args.overlay), parse_rect(args.igniter)) if r)
    if not exclusions:
        print("WARNING: no exclusion region given. The BASS-II video carries a "
              "burned-in telemetry overlay; leaving it in cost 22% of IoU on the "
              "validation phantom.")

    surface = None
    if args.surface:
        x, y = (float(v) for v in args.surface.split(","))
        surface = (x, y)

    meta = RunMetadata(
        repository="NASA Physical Sciences Informatics (PSI)",
        investigation=inv["id"],
        test_id=args.test_id or video.stem,
        source_file=str(video),
        source_digest=file_digest(str(video)),
        landing_page=reg["_repository"]["landing_page"],
        fuel=args.fuel,
        oxygen_volume_fraction=args.oxygen,
        oxygen_uncertainty=inv.get("conditions", {}).get("oxygen_uncertainty"),
        gravity_condition=inv.get("gravity_condition"),
        fps=fps,
        mm_per_px=args.mm_per_px,
        mm_per_px_relative_uncertainty=args.mm_per_px_rel_unc,
        commanded_flow_cm_s=flows,
        reference_step_frames=ref_frames,
        is_synthetic=False,
    )
    geo = DuctGeometry(flow_angle_deg=args.flow_angle, surface_point=surface,
                       surface_angle_deg=args.surface_angle,
                       mm_per_px=args.mm_per_px)
    seg_cfg = SegmentationConfig(exclude_regions=exclusions)

    result = analyse_run(frames, meta, geometry=geo, seg_config=seg_cfg)
    summary = result.summary()

    if flows is not None and len(flows) == len(ref_frames):
        per_frame_flow = np.full(len(frames), np.nan)
        for k, f0 in enumerate(ref_frames):
            per_frame_flow[f0:] = flows[k]
        summary["epi_monotonicity"] = validate_monotonicity(result.epi.epi, per_frame_flow)

    out = Path(args.out or ROOT / "reports" / f"{meta.investigation}_{meta.test_id}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, default=str))

    print(f"\nFrames with a detected flame: {int(result.present.sum())}/{len(frames)}")
    print(f"Change points: {result.change_points}")
    if result.step_alignment:
        a = result.step_alignment
        print(f"  vs commanded steps: precision {a['precision']:.3f}, "
              f"recall {a['recall']:.3f}, F1 {a['f1']:.3f}, "
              f"mean |offset| {a['mean_abs_offset_frames']:.2f} frames")
    for s in result.states:
        print(f"  [{s.start_index:>5}-{s.end_index:<5}] {s.state.value}")
    for m in result.measurements:
        print("\n" + m.render_line())
    for w in result.warnings:
        print(f"\nWARNING: {w}")
    print(f"\nWritten: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
