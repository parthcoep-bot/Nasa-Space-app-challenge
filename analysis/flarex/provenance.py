"""
flarex.provenance
=================

Provenance is not decoration in FLARE-X: it is the mechanism that keeps
Level-3/Level-4 results (our measurements and derivations) from being
mistaken for Level-1/Level-2 claims (NASA-documented fact and published
findings).

Every quantity that leaves the pipeline is wrapped in a `Measurement`
carrying:

  * the value and its unit
  * a `ClaimLevel` (see CLAIM LEVELS below)
  * an uncertainty estimate and how it was obtained
  * a `ProvenanceChain` of `ProvenanceNode`s back to an archived source

CLAIM LEVELS (project-wide, see README "Claim hierarchy"):
  L1_NASA_FACT       NASA-documented fact (hardware, protocol, metadata)
  L2_PUBLISHED       Peer-reviewed published finding
  L3_MEASURED        Measured by FLARE-X from archived NASA data
  L4_DERIVED         Derived analytically by FLARE-X from L3 quantities
  L5_CONCEPT         FLARE-X forward-looking concept; not an observation

Nothing in this module fabricates values. A `Measurement` with
`value=None` and `status="NOT_VERIFIED"` is a legitimate, expected output
when a source could not be confirmed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable, Sequence

__all__ = [
    "ClaimLevel",
    "ProvenanceNode",
    "ProvenanceChain",
    "Measurement",
    "not_verified",
    "file_digest",
    "PIPELINE_VERSION",
]

PIPELINE_VERSION = "flarex-0.3.0"


class ClaimLevel(str, Enum):
    L1_NASA_FACT = "L1_NASA_FACT"
    L2_PUBLISHED = "L2_PUBLISHED"
    L3_MEASURED = "L3_MEASURED"
    L4_DERIVED = "L4_DERIVED"
    L5_CONCEPT = "L5_CONCEPT"

    @property
    def is_nasa_attributable(self) -> bool:
        """True only for levels that may be presented as NASA's own statement."""
        return self is ClaimLevel.L1_NASA_FACT


@dataclass(frozen=True)
class ProvenanceNode:
    """One hop in the chain from an archived artefact to a number."""

    kind: str          # "repository" | "investigation" | "test" | "file" |
                       # "frame" | "method" | "model" | "result"
    identifier: str    # e.g. "NASA PSI", "BASS-II", "frame_000234"
    detail: str = ""
    uri: str | None = None
    digest: str | None = None   # sha256 of the artefact, when it is a file

    def render(self) -> str:
        head = f"{self.kind}:{self.identifier}"
        return f"{head} ({self.detail})" if self.detail else head


@dataclass
class ProvenanceChain:
    nodes: list[ProvenanceNode] = field(default_factory=list)

    def then(self, node: ProvenanceNode) -> "ProvenanceChain":
        return ProvenanceChain(nodes=[*self.nodes, node])

    def render(self) -> str:
        return "\n  -> ".join(n.render() for n in self.nodes)

    @property
    def root_repository(self) -> str | None:
        for n in self.nodes:
            if n.kind == "repository":
                return n.identifier
        return None

    def to_dict(self) -> dict[str, Any]:
        return {"nodes": [asdict(n) for n in self.nodes]}


@dataclass
class Measurement:
    """A single traceable quantity.

    `value is None` together with `status != "OK"` is how FLARE-X records
    'we looked and could not confirm this'. That is a valid result and is
    rendered as such in the interface; it is never back-filled.
    """

    name: str
    value: float | int | str | None
    unit: str
    level: ClaimLevel
    provenance: ProvenanceChain
    uncertainty: float | None = None
    uncertainty_kind: str = "unspecified"   # "type_A_repeat" | "type_B_instrument"
                                            # | "segmentation_threshold_sweep"
                                            # | "quantization" | "unspecified"
    status: str = "OK"                      # "OK" | "NOT_VERIFIED" | "OUT_OF_SCOPE"
    note: str = ""
    created_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    pipeline_version: str = PIPELINE_VERSION

    def __post_init__(self) -> None:
        if self.status == "OK" and self.value is None:
            raise ValueError(
                f"Measurement {self.name!r} has status OK but no value. "
                "Use not_verified() instead of inventing a number."
            )
        if self.level is ClaimLevel.L1_NASA_FACT and self.provenance.root_repository is None:
            raise ValueError(
                f"Measurement {self.name!r} is claimed as NASA fact but its "
                "provenance chain has no repository root. Refusing to emit."
            )

    def render_line(self) -> str:
        if self.status != "OK":
            return f"{self.name}: {self.status} — {self.note}"
        if self.uncertainty is not None and isinstance(self.value, (int, float)):
            return (f"{self.name} = {self.value:.4g} ± {self.uncertainty:.2g} "
                    f"{self.unit}  [{self.level.value}]")
        return f"{self.name} = {self.value} {self.unit}  [{self.level.value}]"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["level"] = self.level.value
        d["provenance"] = self.provenance.to_dict()
        return d


def not_verified(name: str, unit: str, why: str,
                 provenance: ProvenanceChain | None = None) -> Measurement:
    """Explicit placeholder for a quantity we could not confirm.

    Using this instead of a plausible-looking number is a hard project rule.
    """
    return Measurement(
        name=name, value=None, unit=unit,
        level=ClaimLevel.L3_MEASURED,
        provenance=provenance or ProvenanceChain(),
        status="NOT_VERIFIED", note=why,
    )


def file_digest(path: str, chunk: int = 1 << 20) -> str:
    """sha256 of a local file, so a result can be pinned to the exact bytes."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()


def bundle(measurements: Sequence[Measurement]) -> str:
    """Serialise a set of measurements to JSON for the provenance viewer."""
    return json.dumps([m.to_dict() for m in measurements], indent=2)


def assert_no_level_inflation(measurements: Iterable[Measurement]) -> None:
    """Guard used in tests: nothing derived may masquerade as NASA fact."""
    for m in measurements:
        if m.level is ClaimLevel.L1_NASA_FACT:
            kinds = {n.kind for n in m.provenance.nodes}
            if "method" in kinds or "model" in kinds:
                raise AssertionError(
                    f"{m.name!r} passed through a FLARE-X method or model but is "
                    "labelled as a NASA-documented fact."
                )
