"""
flarex.timeseries
=================

Combustion-state detection from the morphology time series.

TWO-TIER BY DESIGN
------------------
Tier 1 (this module, always run): a transparent, fully specified baseline
made of change-point detection plus explicit physical rules. It has no
learned parameters, so it cannot silently memorise a dataset, and every
state boundary it produces can be traced to an inequality a reviewer can
check by hand.

Tier 2 (flarex.models, optional): a supervised classifier trained on
hand-labelled frames. It is only justified if it *beats* Tier 1 on held-out
labels. If it does not, the project reports that and ships Tier 1. Running
a neural network because it sounds impressive, on a dataset of a few
hundred labelled frames, would be indefensible.

WHY CHANGE-POINT DETECTION IS THE RIGHT PRIMITIVE HERE
------------------------------------------------------
The BASS-II opposed-flow protocol is not a free-running burn. Link et al.
(2018) describe igniting at a relatively high opposed flow, letting spread
reach steady state, then *stepping the flow velocity down* with a dwell at
each step long enough for quasi-steady spread, until extinction. The
experiment is therefore a piecewise-stationary staircase by construction,
and each riser is an externally imposed, independently documented event.

That makes change points falsifiable rather than decorative: the detected
boundaries should coincide with the fan-voltage / anemometer steps that
are burned into the video overlay and tabulated in the test record. A
change point that does not correspond to a flow step is either a real
combustion transition or a detector error, and the analyst must say which.

ALGORITHM
---------
Binary segmentation with a Gaussian negative-log-likelihood cost and a
BIC-style penalty, implemented here rather than imported so that the
penalty is visible and tunable:

    cost(segment) = n/2 * log(var(segment) + eps)
    accept a split only if cost_before - cost_after > penalty
    penalty = beta * n_dims * log(N)

Multivariate input is supported: change points found jointly on
(area, aspect ratio, standoff, radiance) are far more stable than on area
alone, because a flow step changes several features at once.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

import numpy as np

__all__ = [
    "CombustionState",
    "StateSegment",
    "StateRules",
    "detect_change_points",
    "label_states",
    "align_to_reference_events",
    "confusion_matrix",
    "classification_report_from_labels",
]

EPS = 1e-12


class CombustionState(str, Enum):
    PRE_IGNITION = "PRE_IGNITION"
    IGNITION = "IGNITION"
    GROWTH = "GROWTH"
    QUASI_STEADY = "QUASI_STEADY"
    TRANSITION = "TRANSITION"
    WEAKENING = "WEAKENING"
    EXTINCTION = "EXTINCTION"
    RE_IGNITION = "RE_IGNITION"
    POST_EXTINCTION = "POST_EXTINCTION"


@dataclass
class StateSegment:
    start_index: int
    end_index: int                 # inclusive
    state: CombustionState
    evidence: dict[str, float] = field(default_factory=dict)
    note: str = ""

    @property
    def length(self) -> int:
        return self.end_index - self.start_index + 1


# --------------------------------------------------------------------------
# change points
# --------------------------------------------------------------------------

def _standardise(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x[:, None]
    out = np.empty_like(x)
    for j in range(x.shape[1]):
        col = x[:, j]
        finite = np.isfinite(col)
        if finite.sum() < 2:
            out[:, j] = 0.0
            continue
        med = np.median(col[finite])
        col = np.where(finite, col, med)
        sd = col.std()
        out[:, j] = (col - col.mean()) / (sd if sd > EPS else 1.0)
    return out


def _segment_cost(x: np.ndarray) -> float:
    """Gaussian NLL cost of modelling a segment by its own mean and variance."""
    n = x.shape[0]
    if n < 2:
        return 0.0
    var = x.var(axis=0) + EPS
    return float(0.5 * n * np.log(var).sum())


def detect_change_points(series: np.ndarray,
                         min_segment: int = 8,
                         beta: float = 2.0,
                         max_change_points: int = 30) -> list[int]:
    """Binary segmentation on a 1-D or multivariate series.

    Returns sorted interior split indices (each is the first index of a new
    segment). `beta` scales the BIC penalty: raise it to demand stronger
    evidence per split.
    """
    x = _standardise(series)
    n, d = x.shape
    if n < 2 * min_segment:
        return []

    penalty = beta * d * float(np.log(max(n, 2)))
    bounds = [(0, n)]
    cps: list[int] = []

    while bounds and len(cps) < max_change_points:
        best = None
        for bi, (lo, hi) in enumerate(bounds):
            if hi - lo < 2 * min_segment:
                continue
            base = _segment_cost(x[lo:hi])
            for t in range(lo + min_segment, hi - min_segment + 1):
                gain = base - (_segment_cost(x[lo:t]) + _segment_cost(x[t:hi]))
                if gain > penalty and (best is None or gain > best[0]):
                    best = (gain, t, bi, lo, hi)
        if best is None:
            break
        _, t, bi, lo, hi = best
        cps.append(t)
        bounds.pop(bi)
        bounds.extend([(lo, t), (t, hi)])

    return sorted(cps)


# --------------------------------------------------------------------------
# state rules
# --------------------------------------------------------------------------

@dataclass
class StateRules:
    """Thresholds for the rule-based labeller.

    These are the only free parameters of Tier 1 and they are reported in
    full in MODEL_CARD.md. Defaults are chosen on dimensionless, normalised
    quantities so they are not tied to one camera or one scale.
    """

    growth_slope: float = 0.02        # d(area)/dt normalised by median area, per s
    steady_slope: float = 0.008
    steady_cv: float = 0.10           # coefficient of variation within a segment
    ignition_rise_fraction: float = 0.15
    extinction_area_fraction: float = 0.05   # of the run's median area
    extinction_persist: int = 5              # frames below threshold to call it out


def _normalised_slope(values: np.ndarray, times: np.ndarray) -> float:
    ok = np.isfinite(values) & np.isfinite(times)
    if ok.sum() < 3:
        return 0.0
    v, t = values[ok], times[ok]
    scale = np.median(np.abs(v))
    if scale <= EPS:
        return 0.0
    return float(np.polyfit(t, v, 1)[0] / scale)


def label_states(area: Sequence[float],
                 time_s: Sequence[float],
                 change_points: Sequence[int] | None = None,
                 present: Sequence[bool] | None = None,
                 rules: StateRules | None = None) -> list[StateSegment]:
    """Assign a combustion state to every inter-change-point segment.

    `present[i]` is False where segmentation found no flame. Those frames are
    PRE_IGNITION before the first flame and POST_EXTINCTION / EXTINCTION after,
    which is how a genuine gap is distinguished from a zero-area flame.
    """
    r = rules or StateRules()
    a = np.asarray(area, dtype=float)
    t = np.asarray(time_s, dtype=float)
    n = len(a)
    if n == 0:
        return []
    if present is None:
        present = np.isfinite(a) & (a > 0)
    present = np.asarray(present, dtype=bool)

    cps = sorted(set(int(c) for c in (change_points or []) if 0 < c < n))
    edges = [0, *cps, n]
    segments: list[StateSegment] = []

    live = np.where(present)[0]
    first_live = int(live[0]) if live.size else None
    last_live = int(live[-1]) if live.size else None
    median_area = float(np.median(a[present])) if live.size else 0.0
    ext_threshold = r.extinction_area_fraction * median_area

    for lo, hi in zip(edges[:-1], edges[1:]):
        if hi <= lo:
            continue
        idx = np.arange(lo, hi)
        seg_present = present[idx]
        frac_present = float(seg_present.mean())

        if frac_present < 0.5:
            if first_live is None or hi <= first_live:
                state, note = CombustionState.PRE_IGNITION, "no flame detected yet"
            else:
                state, note = CombustionState.POST_EXTINCTION, "no flame detected"
            segments.append(StateSegment(lo, hi - 1, state,
                                         {"fraction_frames_with_flame": frac_present},
                                         note))
            continue

        seg_a, seg_t = a[idx], t[idx]
        slope = _normalised_slope(seg_a, seg_t)
        finite = seg_a[np.isfinite(seg_a)]
        cv = float(finite.std() / finite.mean()) if finite.size > 1 and finite.mean() > EPS else 0.0
        evid = {"normalised_area_slope_per_s": slope,
                "coefficient_of_variation": cv,
                "fraction_frames_with_flame": frac_present,
                "mean_area": float(np.nanmean(seg_a))}

        is_first_live_segment = first_live is not None and lo <= first_live < hi
        ends_dark = last_live is not None and hi - 1 >= last_live and not present[hi - 1]

        if is_first_live_segment and slope > r.ignition_rise_fraction:
            state, note = CombustionState.IGNITION, "first flame with steep area rise"
        elif ends_dark or (float(np.nanmean(seg_a)) < ext_threshold and slope < 0):
            state, note = CombustionState.EXTINCTION, "area collapses toward loss of flame"
        elif slope > r.growth_slope:
            state, note = CombustionState.GROWTH, "sustained positive area trend"
        elif slope < -r.growth_slope:
            state, note = CombustionState.WEAKENING, "sustained negative area trend"
        elif abs(slope) <= r.steady_slope and cv <= r.steady_cv:
            state, note = CombustionState.QUASI_STEADY, "flat trend, low dispersion"
        else:
            state, note = CombustionState.TRANSITION, "trend or dispersion between regimes"

        # re-ignition: flame returns after a dark stretch that followed a live one
        if present[lo] and lo > 0 and not present[lo - 1] and first_live is not None and lo > first_live:
            state, note = CombustionState.RE_IGNITION, "flame returns after a dark interval"

        segments.append(StateSegment(lo, hi - 1, state, evid, note))

    return segments


def align_to_reference_events(detected: Sequence[int],
                              reference: Sequence[int],
                              tolerance: int) -> dict[str, float]:
    """Score detected change points against independently known events.

    For BASS-II the reference list is the frame indices of the commanded flow
    steps, read from the video's burned-in telemetry overlay or from the test
    record. Matching is greedy nearest-neighbour within `tolerance` frames,
    one-to-one.
    """
    det = sorted(int(d) for d in detected)
    ref = sorted(int(r) for r in reference)
    used: set[int] = set()
    offsets: list[int] = []

    for rv in ref:
        best_j, best_d = None, None
        for j, dv in enumerate(det):
            if j in used:
                continue
            dist = abs(dv - rv)
            if dist <= tolerance and (best_d is None or dist < best_d):
                best_j, best_d = j, dist
        if best_j is not None:
            used.add(best_j)
            offsets.append(det[best_j] - rv)

    tp = len(offsets)
    fp = len(det) - tp
    fn = len(ref) - tp
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    f1 = (2 * precision * recall / (precision + recall)
          if np.isfinite(precision) and np.isfinite(recall) and (precision + recall) > 0
          else float("nan"))

    return {
        "n_reference_events": len(ref),
        "n_detected": len(det),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "median_offset_frames": float(np.median(offsets)) if offsets else float("nan"),
        "mean_abs_offset_frames": float(np.mean(np.abs(offsets))) if offsets else float("nan"),
        "tolerance_frames": tolerance,
    }


# --------------------------------------------------------------------------
# classification metrics (no wrappers around fabricated numbers)
# --------------------------------------------------------------------------

def confusion_matrix(y_true: Sequence[str], y_pred: Sequence[str],
                     labels: Sequence[str] | None = None
                     ) -> tuple[np.ndarray, list[str]]:
    labs = list(labels) if labels is not None else sorted(set(y_true) | set(y_pred))
    index = {l: i for i, l in enumerate(labs)}
    cm = np.zeros((len(labs), len(labs)), dtype=int)
    for t, p in zip(y_true, y_pred):
        if t in index and p in index:
            cm[index[t], index[p]] += 1
    return cm, labs


def classification_report_from_labels(y_true: Sequence[str], y_pred: Sequence[str]
                                      ) -> dict[str, dict[str, float]]:
    """Per-class precision / recall / F1 / support, computed from real labels.

    If `y_true` is empty this returns an empty dict. It never returns a
    default or an assumed score.
    """
    cm, labs = confusion_matrix(y_true, y_pred)
    out: dict[str, dict[str, float]] = {}
    for i, lab in enumerate(labs):
        tp = int(cm[i, i])
        fp = int(cm[:, i].sum() - tp)
        fn = int(cm[i, :].sum() - tp)
        p = tp / (tp + fp) if (tp + fp) else float("nan")
        r = tp / (tp + fn) if (tp + fn) else float("nan")
        f = (2 * p * r / (p + r)) if np.isfinite(p) and np.isfinite(r) and (p + r) > 0 else float("nan")
        out[lab] = {"precision": float(p), "recall": float(r),
                    "f1": float(f), "support": int(cm[i, :].sum())}
    total = int(cm.sum())
    if total:
        out["__overall__"] = {"accuracy": float(np.trace(cm) / total), "support": total}
    return out
