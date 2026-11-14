"""
flarex.uncertainty
==================

An explicit uncertainty budget, in the GUM sense: named components,
each classified Type A (evaluated from repeated observations) or Type B
(evaluated from other information such as an instrument specification),
combined in quadrature only where the components are independent.

The purpose is to stop FLARE-X from displaying false precision. A flame
area quoted as 41.83 mm^2 from a 760x480 video, segmented by a threshold
that a human chose, scaled by a factor read off an in-duct ruler, is not
known to four figures. `report_significant` exists to round results to
what the budget actually supports.

COMPONENTS MODELLED
-------------------
u_seg    segmentation threshold sensitivity, from a real threshold sweep
         (flarex.segmentation.sweep_threshold_sensitivity). Type B.
u_quant  pixel quantisation of a boundary: a region of area A px has a
         boundary of order sqrt(A) px, each of which is uncertain by about
         half a pixel. Type B.
u_scale  mm-per-pixel calibration. Propagates as 2*u_rel for an area.
         Type B.
u_time   frame timing. At 15 fps a single-frame ambiguity is 67 ms, which
         matters for spread-rate and for aligning change points to
         commanded flow steps. Type B.
u_persp  out-of-plane geometry: a three-dimensional flame imaged by one
         camera gives a projected area, not a surface area. This term is
         NOT estimated numerically here because a single view does not
         constrain it. It is carried as a named, unquantified bias and
         reported as such. Pretending to a number would be worse than
         admitting the gap.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import math

__all__ = ["UncertaintyComponent", "UncertaintyBudget", "area_budget",
           "spread_rate_budget", "report_significant"]


@dataclass
class UncertaintyComponent:
    name: str
    relative: float | None          # relative standard uncertainty, or None if unquantified
    kind: str                       # "A" or "B"
    basis: str
    quantified: bool = True

    def __post_init__(self) -> None:
        if self.relative is None:
            self.quantified = False


@dataclass
class UncertaintyBudget:
    quantity: str
    value: float
    components: list[UncertaintyComponent] = field(default_factory=list)
    unquantified_biases: list[str] = field(default_factory=list)

    @property
    def combined_relative(self) -> float:
        q = [c.relative for c in self.components if c.quantified and c.relative is not None]
        return math.sqrt(sum(r * r for r in q)) if q else float("nan")

    @property
    def combined_absolute(self) -> float:
        return abs(self.value) * self.combined_relative

    def render(self) -> str:
        lines = [f"{self.quantity} = {self.value:.4g} "
                 f"+/- {self.combined_absolute:.3g} (k=1, combined standard)"]
        lines.append(f"  relative combined standard uncertainty: "
                     f"{self.combined_relative:.1%}")
        for c in self.components:
            if c.quantified:
                lines.append(f"  [{c.kind}] {c.name}: {c.relative:.2%} — {c.basis}")
            else:
                lines.append(f"  [{c.kind}] {c.name}: NOT QUANTIFIED — {c.basis}")
        for b in self.unquantified_biases:
            lines.append(f"  bias, not in the budget: {b}")
        return "\n".join(lines)


def area_budget(area_value: float,
                area_px: float,
                seg_relative: float,
                mm_per_px_relative: float | None = None,
                single_view: bool = True) -> UncertaintyBudget:
    """Uncertainty on one flame-area measurement."""
    comps = [
        UncertaintyComponent(
            "segmentation threshold", seg_relative, "B",
            "half-range of area over a +/-15% sweep of the Otsu multiplier, "
            "converted to a relative standard uncertainty"),
    ]
    if area_px > 0:
        perim_px = 2.0 * math.sqrt(math.pi * area_px)
        u_quant_abs = 0.5 * perim_px
        comps.append(UncertaintyComponent(
            "boundary quantisation", u_quant_abs / area_px, "B",
            "half-pixel positional uncertainty applied along an equivalent-"
            "circle boundary of the measured region"))
    if mm_per_px_relative is not None:
        comps.append(UncertaintyComponent(
            "scale calibration (area, x2)", 2.0 * mm_per_px_relative, "B",
            "relative uncertainty in mm/px, doubled because area scales as "
            "the square of a length"))
    else:
        comps.append(UncertaintyComponent(
            "scale calibration", None, "B",
            "mm/px not supplied; the value is in pixels and cannot be "
            "converted to a physical area"))

    biases = []
    if single_view:
        biases.append(
            "Single-camera projection: the reported area is the projected area "
            "of a three-dimensional flame onto the image plane. The projection "
            "bias is not estimable from one view and is not included above.")
    biases.append(
        "Visible-band detection: the segmented region is the part of the flame "
        "emitting enough in the camera's visible response to exceed threshold. "
        "A dim blue near-limit flame has a smaller visible footprint than its "
        "reaction zone.")
    return UncertaintyBudget("flame area", area_value, comps, biases)


def spread_rate_budget(rate_value: float,
                       position_relative: float,
                       fps: float,
                       delta_t_s: float) -> UncertaintyBudget:
    """Uncertainty on a spread rate obtained as d(leading edge)/dt."""
    timing_rel = (1.0 / fps) / delta_t_s if delta_t_s > 0 else float("nan")
    comps = [
        UncertaintyComponent("leading-edge position", position_relative, "B",
                             "propagated from segmentation and quantisation on "
                             "the upstream-most flame pixel"),
        UncertaintyComponent("frame timing", timing_rel, "B",
                             f"one frame interval at {fps:g} fps over a "
                             f"{delta_t_s:g} s measurement baseline"),
    ]
    return UncertaintyBudget(
        "flame spread rate", rate_value, comps,
        ["Leading-edge definition: the upstream-most *visible* pixel is not "
         "the pyrolysis front. The offset between them is a systematic bias "
         "that cannot be removed without a surface-temperature measurement."])


def report_significant(value: float, absolute_uncertainty: float) -> str:
    """Format a value to the precision its uncertainty supports.

    Convention: one significant figure on the uncertainty (two if its leading
    digit is 1), and the value rounded to the same decimal place.
    """
    if not (absolute_uncertainty > 0) or not math.isfinite(absolute_uncertainty):
        return f"{value:.4g} (uncertainty not quantified)"
    exp = math.floor(math.log10(absolute_uncertainty))
    lead = absolute_uncertainty / (10 ** exp)
    digits = 2 if lead < 2.0 else 1
    place = exp - (digits - 1)
    factor = 10 ** place
    v = round(value / factor) * factor
    u = round(absolute_uncertainty / factor) * factor
    dec = max(0, -place)
    return f"{v:.{dec}f} +/- {u:.{dec}f}"
