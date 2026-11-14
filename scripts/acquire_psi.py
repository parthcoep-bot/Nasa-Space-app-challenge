#!/usr/bin/env python3
"""
NASA PSI data acquisition workflow for FLARE-X.

READ THIS FIRST
---------------
This script does NOT download NASA data, and that is deliberate on two
grounds rather than one.

1. It cannot. The NASA Physical Sciences Informatics repository is behind
   an individual user registration (psiuserregistration.ndc.nasa.gov).
   There is no anonymous bulk endpoint to script against, and attempting
   to work around a registration gate would be both unreliable and wrong.

2. It should not. FLARE-X does not redistribute NASA data. Each user
   obtains it under their own registration, which keeps attribution and
   terms of use intact.

WHAT IT DOES INSTEAD
--------------------
It makes a manual acquisition reproducible, which is the part that
normally gets lost:

  init      writes an acquisition manifest naming exactly which
            investigation and which file classes are needed, with the
            landing pages to visit
  verify    hashes whatever the user has placed in data/raw/, records
            sha256 for every file, and writes an inventory that later
            analysis pins its results to
  check     confirms the inventory still matches the files on disk, so a
            result can never silently drift onto different bytes

Usage:
    python scripts/acquire_psi.py init  --investigation BASS-II
    python scripts/acquire_psi.py verify --investigation BASS-II
    python scripts/acquire_psi.py check  --investigation BASS-II
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis"))
from flarex.provenance import file_digest  # noqa: E402

REGISTRY = ROOT / "data" / "registry" / "investigations.json"
RAW = ROOT / "data" / "raw"

MEDIA_SUFFIXES = {".avi", ".mp4", ".mov", ".mpg", ".mpeg", ".mkv", ".wmv",
                  ".tif", ".tiff", ".png", ".jpg", ".jpeg", ".bmp",
                  ".csv", ".txt", ".dat", ".xls", ".xlsx", ".pdf"}


def _registry() -> dict:
    return json.loads(REGISTRY.read_text())


def _investigation(reg: dict, name: str) -> dict:
    for inv in reg["investigations"]:
        if inv["id"].upper() == name.upper():
            return inv
    raise SystemExit(f"Unknown investigation {name!r}. Known: "
                     + ", ".join(i["id"] for i in reg["investigations"]))


def cmd_init(args: argparse.Namespace) -> int:
    reg = _registry()
    inv = _investigation(reg, args.investigation)
    target = RAW / args.investigation
    target.mkdir(parents=True, exist_ok=True)

    manifest = {
        "investigation": inv["id"],
        "name": inv["name"],
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repository": reg["_repository"]["name"],
        "access_portal": reg["_repository"]["data_access"],
        "investigations_index": reg["_repository"]["investigations_index"],
        "redistribution_policy": reg["_repository"]["redistribution_by_flarex"],
        "place_files_in": str(target),
        "what_to_request": [
            "Video of opposed-flow tests over PMMA rods, including the full "
            "flow-step sequence through to extinction.",
            "The test record or run log giving, per test: fuel identity and "
            "diameter, oxygen volume fraction, the commanded flow velocities "
            "and the times at which they were changed.",
            "Any still-camera sequence for the same tests (the still camera "
            "has a documented 34 px/mm scale and can be used to calibrate the "
            "video scale, which is not documented).",
            "Any file documenting the video frame rate and the layout of the "
            "burned-in telemetry overlay.",
        ],
        "why_each_item_matters": {
            "video": "the morphology time series is extracted from it",
            "flow schedule": "it is the independent reference against which "
                             "detected change points are scored; without it the "
                             "change points cannot be falsified",
            "still sequence": "supplies the mm/px scale, without which every "
                              "length in the analysis stays in pixels",
            "frame rate": "sets the time axis; without it all rates are provisional",
        },
        "after_download": "run: python scripts/acquire_psi.py verify "
                          f"--investigation {inv['id']}",
        "next_steps_note": "FLARE-X will report lengths in pixels and times in "
                           "frames if the scale or frame rate is missing. It "
                           "will not assume a value.",
    }
    out = target / "ACQUISITION_MANIFEST.json"
    out.write_text(json.dumps(manifest, indent=2))

    print(f"Acquisition manifest written: {out}\n")
    print(f"  1. Register for PSI access: {reg['_repository']['data_access']}")
    print(f"  2. Locate the {inv['id']} investigation in the Combustion Science area.")
    print(f"  3. Download into: {target}")
    print(f"  4. Run: python scripts/acquire_psi.py verify --investigation {inv['id']}")
    if str(inv.get("dataset_doi", "")).startswith("NOT_VERIFIED"):
        print("\n  Note: no dataset-level DOI was confirmed for this investigation.")
        print("  Cite the PSI investigation identifier plus your accession date.")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    target = RAW / args.investigation
    if not target.exists():
        raise SystemExit(f"{target} does not exist. Run `init` first.")

    files = sorted(p for p in target.rglob("*")
                   if p.is_file() and p.name != "FILE_INVENTORY.json")
    media = [p for p in files if p.suffix.lower() in MEDIA_SUFFIXES]

    if not media:
        print(f"No data files found in {target}.")
        print("This is the expected state for a fresh clone: FLARE-X ships no "
              "NASA data. Download under your own PSI registration first.")
        return 1

    inventory = {
        "investigation": args.investigation,
        "verified_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_files": len(media),
        "total_bytes": sum(p.stat().st_size for p in media),
        "files": [{"relative_path": str(p.relative_to(target)),
                   "bytes": p.stat().st_size,
                   "sha256": file_digest(str(p))} for p in media],
        "note": "Every FLARE-X result derived from these files records the "
                "matching sha256 in its provenance chain.",
    }
    out = target / "FILE_INVENTORY.json"
    out.write_text(json.dumps(inventory, indent=2))
    print(f"Inventoried {len(media)} files ({inventory['total_bytes']/1e6:.1f} MB)")
    print(f"Written: {out}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    target = RAW / args.investigation
    inv_path = target / "FILE_INVENTORY.json"
    if not inv_path.exists():
        raise SystemExit(f"No inventory at {inv_path}. Run `verify` first.")
    inventory = json.loads(inv_path.read_text())

    drift, missing = [], []
    for rec in inventory["files"]:
        p = target / rec["relative_path"]
        if not p.exists():
            missing.append(rec["relative_path"])
        elif file_digest(str(p)) != rec["sha256"]:
            drift.append(rec["relative_path"])

    if not drift and not missing:
        print(f"OK: all {len(inventory['files'])} files match the inventory "
              f"recorded {inventory['verified_utc']}.")
        return 0
    for m in missing:
        print(f"MISSING: {m}")
    for d in drift:
        print(f"CHANGED: {d}  <-- results pinned to the old hash are now invalid")
    return 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("init", cmd_init), ("verify", cmd_verify), ("check", cmd_check)):
        s = sub.add_parser(name)
        s.add_argument("--investigation", default="BASS-II")
        s.set_defaults(func=fn)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
