"""
flarex.extinction
=================

THE EXTINCTION PROXIMITY INDEX (EPI)

WHAT THIS IS
    A transparent, monotone, unit-free composite of image-derived flame
    features that quantifies how far a flame's *appearance* has moved
    toward the appearance reported for near-limit microgravity flames.

WHAT THIS IS NOT
    Not a probability. Not a fire risk. Not a spacecraft hazard score.
    Not NASA-endorsed, NASA-validated or NASA-certified. It does not
    predict whether a real fire will occur or when a real flame will go
    out. Calling it any of those things would be a misrepresentation of
    what the underlying measurements can support.

    Label it exactly as: "Research prototype — data-derived indicator."

WHY EACH TERM IS IN THE INDEX
-----------------------------
Every term is a *quantification of a qualitative observation already
published for these experiments*, not a free parameter chosen to make a
curve look good. For BASS-II opposed-flow PMMA rods, Link, Huang,
Fernandez-Pello, Olson & Ferkul (Sci. Rep. 8:120, 2018,
doi:10.1038/s41598-017-18398-4) report, as the opposed flow is reduced
toward the low-velocity limit:

  T1 elongation       the flame becomes longer and its shape more spherical
                      -> we track flow-axis length and the length/width ratio
  T2 standoff         the boundary layer thickens, the flame sits further
                      from the surface, and heat transfer to the solid falls
                      -> we track minimum flame-to-surface distance
  T3 sootiness fall   colour shifts yellow -> blue, inferred as reduced soot
                      production and reduced flame temperature
                      -> we track the colour index chi = (R-B)/(R+B)
  T4 radiance fall    the flame becomes visibly dim
                      -> we track uncalibrated relative radiance
  T5 area decline     shrinking flame area as the limit is approached
                      -> we track the normalised area trend

The extinction mechanism these terms describe is the radiative /
oxygen-transport-limited regime: as the flame stands off, heat feedback to
the fuel falls, surface re-radiation dominates the energy balance and the
flame quenches at a limiting low flow velocity. That mechanism is the
published interpretation, not ours; what FLARE-X adds is the per-frame
quantification of it with an uncertainty attached.

MONOTONICITY IS A REQUIREMENT, NOT AN OUTCOME
---------------------------------------------
Each term is mapped to [0, 1] by a *fixed-direction* normalisation against
that run's own observed range, so the index cannot be tuned per run by
flipping a sign. `validate_monotonicity` checks the index against the
commanded flow schedule using Spearman rank correlation; if the index does
not decrease with flow velocity on a run, the honest reporting is that the
index failed on that run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np

__all__ = [
    "EPITerm",
    "EPIConfig",
    "EPIResult",
    "compute_epi",
    "validate_monotonicity",
    "DEFAULT_TERMS",
    "DISCLAIMER",
]

DISCLAIMER = (
    "Research prototype - data-derived indicator. Computed by FLARE-X from "
    "archived imagery. Not a probability, not a risk score, not a NASA "
    "product, and not validated against any spacecraft fire event."
)

EPS = 1e-12


@dataclass(frozen=True)
class EPITerm:
    """One contributing feature.

    direction = +1 : the feature *increases* toward extinction
    direction = -1 : the feature *decreases* toward extinction
    """

    feature: str
    direction: int
    weight: float
    rationale: str
    source: str


DEFAULT_TERMS: tuple[EPITerm, ...] = (
    EPITerm("aspect_ratio", +1, 0.25,
            "Flame elongates along the flow axis as the low-velocity limit is approached.",
            "Link et al. 2018, doi:10.1038/s41598-017-18398-4"),
    EPITerm("standoff", +1, 0.25,
            "Thickening boundary layer moves the flame off the surface, cutting heat "
            "feedback to the fuel; the published extinction mechanism in this regime.",
            "Link et al. 2018, doi:10.1038/s41598-017-18398-4"),
    EPITerm("sootiness_index", -1, 0.20,
            "Yellow-to-blue colour shift, reported as reduced soot production and "
            "reduced flame temperature near the limit.",
            "Link et al. 2018, doi:10.1038/s41598-017-18398-4"),
    EPITerm("radiance_mean", -1, 0.15,
            "Near-limit flames are reported as visibly dim. Uncalibrated relative "
            "radiance only; never interpreted as temperature.",
            "Link et al. 2018, doi:10.1038/s41598-017-18398-4"),
    EPITerm("area", -1, 0.15,
            "Declining projected flame area accompanies the weakening flame.",
            "Link et al. 2018, doi:10.1038/s41598-017-18398-4"),
)


@dataclass
class EPIConfig:
    terms: tuple[EPITerm, ...] = DEFAULT_TERMS
    smoothing_window: int = 5          # rolling median, in frames
    robust_percentiles: tuple[float, float] = (5.0, 95.0)
    min_valid_fraction: float = 0.6    # per term, before it is dropped

    def normalised_weights(self, active: Sequence[str]) -> dict[str, float]:
        total = sum(t.weight for t in self.terms if t.feature in active)
        if total <= EPS:
            return {}
        return {t.feature: t.weight / total for t in self.terms if t.feature in active}


@dataclass
class EPIResult:
    epi: np.ndarray                          # [0,1], higher = nearer the limit
    per_term: dict[str, np.ndarray]          # normalised contributions
    weights: dict[str, float]
    dropped_terms: dict[str, str]            # feature -> why it was dropped
    disclaimer: str = DISCLAIMER
    provenance_note: str = field(default="")

    def explain_frame(self, i: int, top_k: int = 3) -> list[tuple[str, float]]:
        """Per-frame attribution: which terms carry this frame's index value.

        This is the interpretability guarantee. Because EPI is a weighted sum
        of normalised terms, the attribution is exact, not an approximation
        such as SHAP on an opaque model.
        """
        contrib = [(f, float(self.weights[f] * self.per_term[f][i]))
                   for f in self.per_term if np.isfinite(self.per_term[f][i])]
        contrib.sort(key=lambda kv: kv[1], reverse=True)
        return contrib[:top_k]


def _rolling_median(x: np.ndarray, w: int) -> np.ndarray:
    if w <= 1 or x.size < w:
        return x.copy()
    pad = w // 2
    xp = np.pad(x, (pad, pad), mode="edge")
    out = np.empty(x.size, dtype=float)
    for i in range(x.size):
        win = xp[i:i + w]
        ok = win[np.isfinite(win)]
        # An all-NaN window means the flame was absent across the whole window.
        # That is a genuine gap, so it stays NaN rather than being interpolated.
        out[i] = np.median(ok) if ok.size else np.nan
    return out


def _robust_unit_scale(x: np.ndarray, lo_p: float, hi_p: float,
                       direction: int) -> np.ndarray:
    ok = np.isfinite(x)
    if ok.sum() < 3:
        return np.full_like(x, np.nan, dtype=float)
    lo, hi = np.percentile(x[ok], [lo_p, hi_p])
    if hi - lo <= EPS:
        return np.full_like(x, np.nan, dtype=float)
    u = (x - lo) / (hi - lo)
    u = np.clip(u, 0.0, 1.0)
    return u if direction > 0 else 1.0 - u


def compute_epi(features: Mapping[str, Sequence[float]],
                config: EPIConfig | None = None,
                provenance_note: str = "") -> EPIResult:
    """Compute the index from a dict of feature time series.

    A term that is missing, constant, or too sparse is *dropped and
    reported*, and the remaining weights renormalise. The index is never
    silently completed with a substituted value.
    """
    cfg = config or EPIConfig()
    n = max((len(v) for v in features.values()), default=0)
    if n == 0:
        return EPIResult(np.zeros(0), {}, {}, {"__all__": "no features supplied"},
                         provenance_note=provenance_note)

    per_term: dict[str, np.ndarray] = {}
    dropped: dict[str, str] = {}

    for term in cfg.terms:
        raw = features.get(term.feature)
        if raw is None:
            dropped[term.feature] = "feature not present in the extracted time series"
            continue
        x = np.asarray(raw, dtype=float)
        if x.size != n:
            dropped[term.feature] = f"length {x.size} does not match series length {n}"
            continue
        valid = np.isfinite(x).mean()
        if valid < cfg.min_valid_fraction:
            dropped[term.feature] = (f"only {valid:.0%} of frames finite, below the "
                                     f"{cfg.min_valid_fraction:.0%} minimum")
            continue
        sm = _rolling_median(x, cfg.smoothing_window)
        u = _robust_unit_scale(sm, *cfg.robust_percentiles, direction=term.direction)
        if not np.isfinite(u).any():
            dropped[term.feature] = "feature is constant over the run; carries no information"
            continue
        per_term[term.feature] = u

    weights = cfg.normalised_weights(list(per_term))
    if not weights:
        return EPIResult(np.full(n, np.nan), per_term, {}, dropped,
                         provenance_note=provenance_note)

    epi = np.zeros(n, dtype=float)
    wsum = np.zeros(n, dtype=float)
    for f, u in per_term.items():
        ok = np.isfinite(u)
        epi[ok] += weights[f] * u[ok]
        wsum[ok] += weights[f]
    epi = np.where(wsum > EPS, epi / np.maximum(wsum, EPS), np.nan)

    return EPIResult(epi=epi, per_term=per_term, weights=weights,
                     dropped_terms=dropped, provenance_note=provenance_note)


def validate_monotonicity(epi: Sequence[float],
                          flow_velocity: Sequence[float]) -> dict[str, float]:
    """Does the index actually rise as the commanded flow falls toward the limit?

    Spearman rank correlation between EPI and the *commanded* opposed flow
    velocity. The index is intended to be negatively correlated with flow in
    the low-velocity branch. A positive or near-zero correlation is a
    falsification on that run and must be reported as such.

    Note the physics caveat that keeps this honest: Link et al. report the
    flame spread rate is *non-monotonic* in opposed flow velocity, rising
    then falling as flow increases. EPI is therefore only expected to be
    monotone on the low-velocity branch below the turning point. Applying
    this check across the full flow range without splitting at the turning
    point would be a misuse of it.
    """
    e = np.asarray(epi, dtype=float)
    v = np.asarray(flow_velocity, dtype=float)
    ok = np.isfinite(e) & np.isfinite(v)
    if ok.sum() < 5:
        return {"spearman_rho": float("nan"), "n": int(ok.sum()),
                "status": "INSUFFICIENT_DATA"}

    def _rank(a: np.ndarray) -> np.ndarray:
        order = a.argsort()
        ranks = np.empty(len(a), dtype=float)
        ranks[order] = np.arange(len(a), dtype=float)
        # average ties
        _, inv, counts = np.unique(a, return_inverse=True, return_counts=True)
        sums = np.zeros(len(counts))
        np.add.at(sums, inv, ranks)
        return (sums / counts)[inv]

    re_, rv = _rank(e[ok]), _rank(v[ok])
    rho = float(np.corrcoef(re_, rv)[0, 1])
    return {
        "spearman_rho": rho,
        "n": int(ok.sum()),
        "status": "CONSISTENT_WITH_EXPECTATION" if rho < -0.3 else "NOT_SUPPORTED",
        "expectation": "EPI should be negatively rank-correlated with opposed flow "
                       "velocity on the low-velocity branch (rho < -0.3 taken as "
                       "consistent; this threshold is a reporting convention, not a "
                       "significance test).",
    }
