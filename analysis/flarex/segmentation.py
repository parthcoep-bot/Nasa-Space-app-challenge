"""
flarex.segmentation
===================

Flame segmentation for archived microgravity combustion video.

WHY A GENERIC FIRE DETECTOR DOES NOT WORK HERE
----------------------------------------------
Almost every off-the-shelf "flame detector" keys on the red channel or on
a fire-coloured hue range. That is a reasonable prior for terrestrial
sooting fires. It fails on exactly the flames this project cares about.

Link, Huang, Fernandez-Pello, Olson & Ferkul (Sci. Rep. 8:120, 2018,
doi:10.1038/s41598-017-18398-4) report for BASS-II opposed-flow PMMA rods
that as the opposed flow velocity is reduced toward the extinction limit
the flame colour changes from yellow to blue, and infer that soot
production and flame temperature drop as flow falls below ~1 cm/s. The
same paper reports that flames can be sustained below 1 cm/s where they
become dim and blue.

So the near-limit flame -- the scientifically interesting one -- is dim
and blue, and a red-channel detector suppresses it precisely when the
measurement matters most. FLARE-X therefore segments on a
soot-independent radiance proxy and treats colour as a *separate*
measured feature rather than as the detection cue.

CHANNELS USED
-------------
  V(x)      = max over {R,G,B} of the background-subtracted frame.
              Responds to soot continuum (yellow) and to CH*/C2
              chemiluminescence (blue) alike.
  chi(x)    = (R - B) / (R + B + eps), a *sootiness proxy* in [-1, 1].
              NOT a temperature. Reported as a colour index only.

Segmentation is hysteresis thresholding on V: seeds above a high
threshold, grown through pixels above a low threshold. Thresholds are
placed by Otsu on the seed distribution with a configurable multiplier so
that the whole decision is a small number of auditable scalars, and so
that sweeping the multiplier gives a direct, honest segmentation
uncertainty (see `sweep_threshold_sensitivity`).

CALIBRATION WARNING (enforced, not just documented)
---------------------------------------------------
The BASS-II video camera (Panasonic WV-CP654, 760x480) carried a burned-in
digital overlay and was not radiometrically calibrated for absolute
intensity; the in-duct Oriel 71768 thermopile radiometer was explicitly
reported as uncalibrated and used only as a measure of flame dynamics and
steadiness. Nothing in this module converts pixel brightness to
temperature or to heat release, and `radiance_proxy` is named to make
that impossible to forget.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np

try:  # OpenCV is the runtime dependency; skimage is used for hysteresis.
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

from skimage.filters import threshold_otsu
from skimage.filters import apply_hysteresis_threshold
from skimage.morphology import (remove_small_objects, remove_small_holes, disk,
                                opening as morph_opening,
                                closing as morph_closing)
from skimage.measure import label

__all__ = [
    "SegmentationConfig",
    "SegmentationResult",
    "radiance_proxy",
    "sootiness_index",
    "estimate_background",
    "segment_flame",
    "sweep_threshold_sensitivity",
]

EPS = 1e-6


@dataclass
class SegmentationConfig:
    """Every knob that can change a segmentation result, in one auditable place."""

    high_multiplier: float = 1.00     # x Otsu level for seed pixels
    low_multiplier: float = 0.55      # x Otsu level for growth pixels
    min_object_px: int = 40           # discard specks below this area
    min_hole_px: int = 40             # fill pinholes below this area
    open_radius: int = 1              # morphological cleanup
    close_radius: int = 2
    keep_largest_only: bool = True    # a single flame per frame is expected
    background_percentile: float = 5.0
    snr_floor: float = 6.0            # peak must exceed this many noise sigmas
    extreme_value_margin: float = 1.25  # x the expected noise maximum
    low_threshold_sigmas: float = 3.0   # hysteresis growth floor, in sigmas
    exclude_regions: tuple[tuple[int, int, int, int], ...] = ()
    # exclude_regions are (x0, y0, x1, y1) rectangles zeroed before
    # thresholding. Used for the burned-in telemetry overlay and for the
    # glowing igniter coil, which is not flame.

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        d["exclude_regions"] = [list(r) for r in self.exclude_regions]
        return d


@dataclass
class SegmentationResult:
    mask: np.ndarray               # bool, HxW
    radiance: np.ndarray           # float32, HxW background-subtracted V
    threshold_high: float
    threshold_low: float
    n_components_before_selection: int
    config: SegmentationConfig
    empty_reason: str | None = None   # set when no flame was found

    @property
    def is_empty(self) -> bool:
        return not self.mask.any()


def _as_float_rgb(frame: np.ndarray) -> np.ndarray:
    """Accept uint8 or float, BGR (OpenCV) or RGB, return float32 RGB in [0,1]."""
    arr = np.asarray(frame)
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)
    if arr.dtype == np.uint8:
        arr = arr.astype(np.float32) / 255.0
    else:
        arr = arr.astype(np.float32)
        if arr.max() > 1.5:
            arr = arr / 255.0
    return arr


def radiance_proxy(frame: np.ndarray) -> np.ndarray:
    """Soot-independent brightness channel V = max(R, G, B).

    This is an *uncalibrated relative radiance proxy*. It is not a
    temperature, not an irradiance, and not comparable between different
    cameras, gain settings or exposure settings.
    """
    rgb = _as_float_rgb(frame)
    return rgb.max(axis=-1).astype(np.float32)


def sootiness_index(frame: np.ndarray, mask: np.ndarray | None = None) -> float:
    """Mean chi = (R-B)/(R+B) over the flame. Positive = yellow/sooty,
    negative = blue.

    Interpretation is restricted to: higher chi indicates a relatively
    greater soot-continuum contribution to the visible emission, following
    the qualitative yellow-to-blue transition reported for BASS-II
    near-limit flames. It is a colour index, not a soot volume fraction.
    """
    rgb = _as_float_rgb(frame)
    r, b = rgb[..., 0], rgb[..., 2]
    chi = (r - b) / (r + b + EPS)
    if mask is None:
        return float(np.mean(chi))
    if not mask.any():
        return float("nan")
    return float(np.mean(chi[mask]))


def estimate_background(frames: Sequence[np.ndarray],
                        percentile: float = 5.0) -> np.ndarray:
    """Per-pixel low percentile of the radiance proxy across a frame stack.

    A percentile (not a mean) is used so that a flame dwelling over a pixel
    for part of the sequence does not contaminate that pixel's background.
    Pre-ignition frames are the ideal input; the percentile makes the
    estimate robust when they are unavailable.
    """
    stack = np.stack([radiance_proxy(f) for f in frames], axis=0)
    return np.percentile(stack, percentile, axis=0).astype(np.float32)


def _noise_scale(v: np.ndarray) -> float:
    """Robust noise sigma of a background-subtracted radiance field.

    Standard robust estimator: sigma = 1.4826 * MAD over the whole field.
    MAD is insensitive to a minority of extreme values, so a flame occupying
    a modest fraction of the frame does not inflate it, while the dark duct
    background that fills most of the frame sets the scale.

    An earlier version of this function computed the MAD over the lower half
    of the distribution. That truncation biases sigma low by roughly a third,
    which let pure-noise frames through the gate. Kept as a comment because
    it is an easy mistake to repeat.
    """
    x = v[np.isfinite(v)]
    if x.size < 32:
        return 0.0
    mad = float(np.median(np.abs(x - np.median(x))))
    return 1.4826 * mad


def _apply_exclusions(img: np.ndarray,
                      regions: Sequence[tuple[int, int, int, int]]) -> np.ndarray:
    out = img.copy()
    h, w = out.shape[:2]
    for x0, y0, x1, y1 in regions:
        x0, x1 = max(0, min(x0, x1)), min(w, max(x0, x1))
        y0, y1 = max(0, min(y0, y1)), min(h, max(y0, y1))
        out[y0:y1, x0:x1] = 0.0
    return out


def segment_flame(frame: np.ndarray,
                  background: np.ndarray | None = None,
                  config: SegmentationConfig | None = None) -> SegmentationResult:
    """Segment one frame. Returns a mask plus every threshold that produced it."""
    cfg = config or SegmentationConfig()
    v_raw = radiance_proxy(frame)
    # The sensor noise scale is measured on the RAW field. After background
    # subtraction the field is clipped at zero, which collapses any robust
    # dispersion estimate toward zero and would silently disable the gate.
    noise_sigma = _noise_scale(v_raw)
    n_pixels_eff = int(v_raw.size)
    if background is not None:
        resid = v_raw - background
        # A low-percentile background sits below the true background level by
        # construction (that is what makes it robust to a flame dwelling on a
        # pixel). Re-centre on the residual's own median, which is background
        # wherever the flame covers less than half the frame, so the residual
        # is zero-mean in the dark region and the noise gate below compares
        # like with like. Without this the residual carries a ~1.6 sigma
        # positive offset and empty frames leak through the gate.
        resid = resid - float(np.median(resid))
        v = np.clip(resid, 0.0, None)
    else:
        v = v_raw
    v = _apply_exclusions(v, cfg.exclude_regions)
    # Expected maximum of N independent Gaussian noise samples grows as
    # sigma*sqrt(2 ln N). Over a 760x480 frame that is about 5 sigma, so a
    # fixed "6 sigma" rule is barely above the noise ceiling and lets empty
    # frames through. The detection gate is therefore set relative to the
    # extreme-value scale, not to a bare multiple of sigma.
    noise_max_expected = noise_sigma * math.sqrt(2.0 * math.log(max(n_pixels_eff, 2)))
    detect_gate = max(cfg.snr_floor * noise_sigma,
                      cfg.extreme_value_margin * noise_max_expected)

    finite = v[np.isfinite(v)]
    if finite.size == 0 or float(finite.max()) <= EPS:
        return SegmentationResult(
            mask=np.zeros(v.shape, dtype=bool), radiance=v,
            threshold_high=float("nan"), threshold_low=float("nan"),
            n_components_before_selection=0, config=cfg,
            empty_reason="frame carries no signal above background",
        )

    # ABSOLUTE SIGNAL GATE.
    # Otsu always returns a threshold, including on a frame containing nothing
    # but sensor noise. Without this gate the segmenter happily reports a
    # "flame" after extinction, which is exactly the failure mode that would
    # corrupt an extinction-time measurement. The gate is a signal-to-noise
    # test against a robust noise scale (MAD of the low half of the
    # background-subtracted frame), not a hand-tuned brightness constant.
    peak = float(finite.max())
    if noise_sigma > 0 and peak < detect_gate:
        return SegmentationResult(
            mask=np.zeros(v.shape, dtype=bool), radiance=v,
            threshold_high=float(detect_gate), threshold_low=float("nan"),
            n_components_before_selection=0, config=cfg,
            empty_reason=(f"peak signal {peak:.4g} is below the detection gate "
                          f"{detect_gate:.4g} (noise sigma {noise_sigma:.4g}, "
                          f"expected noise maximum over {n_pixels_eff} px "
                          f"{noise_max_expected:.4g}); frame is consistent with "
                          "background noise alone"),
        )

    # Otsu on the non-zero support: including the large empty background
    # would drag the threshold toward zero and inflate the flame.
    support = finite[finite > EPS]
    if support.size < 16 or np.allclose(support, support[0]):
        base = float(finite.max()) * 0.5
    else:
        base = float(threshold_otsu(support))

    t_high = max(base * cfg.high_multiplier, detect_gate)
    # The hysteresis growth threshold needs its own noise floor. Without one,
    # a legitimate seed grows through the noise field and floods the frame -
    # observed as a 5186-px "flame" on an 80x80 pure-noise test.
    t_low = max(base * cfg.low_multiplier,
                cfg.low_threshold_sigmas * noise_sigma)
    if t_low >= t_high:
        t_low = t_high * 0.9

    mask = apply_hysteresis_threshold(v, t_low, t_high)

    if cfg.open_radius > 0:
        mask = morph_opening(mask, disk(cfg.open_radius))
    if cfg.close_radius > 0:
        mask = morph_closing(mask, disk(cfg.close_radius))
    if cfg.min_hole_px > 0:
        mask = remove_small_holes(mask, max_size=cfg.min_hole_px)
    if cfg.min_object_px > 0:
        mask = remove_small_objects(mask, max_size=cfg.min_object_px)

    lab = label(mask)
    n_components = int(lab.max())

    if n_components == 0:
        return SegmentationResult(
            mask=np.zeros(v.shape, dtype=bool), radiance=v,
            threshold_high=t_high, threshold_low=t_low,
            n_components_before_selection=0, config=cfg,
            empty_reason="no connected component survived cleanup",
        )

    if cfg.keep_largest_only and n_components > 1:
        sizes = np.bincount(lab.ravel())
        sizes[0] = 0
        mask = lab == int(sizes.argmax())

    return SegmentationResult(
        mask=mask, radiance=v,
        threshold_high=t_high, threshold_low=t_low,
        n_components_before_selection=n_components, config=cfg,
    )


def sweep_threshold_sensitivity(frame: np.ndarray,
                                background: np.ndarray | None = None,
                                config: SegmentationConfig | None = None,
                                multipliers: Sequence[float] = (0.80, 0.90, 1.0,
                                                                1.10, 1.20),
                                ) -> dict[str, float]:
    """Segmentation uncertainty by re-thresholding, not by assertion.

    The high-threshold multiplier is swept over `multipliers` and the
    resulting flame areas recorded. The half-range and the coefficient of
    variation are reported as a Type-B segmentation uncertainty on area.
    This is the number FLARE-X quotes as the area error bar; it deliberately
    does not include camera, perspective or motion-blur terms, which are
    accounted separately in flarex.uncertainty.
    """
    cfg = config or SegmentationConfig()
    areas: list[float] = []
    gate_bound = False
    for m in multipliers:
        swept = SegmentationConfig(**{
            **cfg.__dict__,
            "high_multiplier": cfg.high_multiplier * m,
            # both hysteresis levels move together: the grown region is set by
            # the low threshold, so sweeping the high one alone is nearly a
            # no-op and would report a falsely tiny uncertainty
            "low_multiplier": cfg.low_multiplier * m,
        })
        res = segment_flame(frame, background=background, config=swept)
        areas.append(float(res.mask.sum()))
        if res.empty_reason and "detection gate" in res.empty_reason:
            gate_bound = True

    a = np.asarray(areas, dtype=float)
    nominal = float(a[len(a) // 2])
    return {
        "area_px_nominal": nominal,
        "area_px_min": float(a.min()),
        "area_px_max": float(a.max()),
        "area_px_half_range": float((a.max() - a.min()) / 2.0),
        "area_relative_cv": float(a.std(ddof=1) / a.mean()) if a.mean() > 0 else float("nan"),
        "n_multipliers": len(multipliers),
        "multipliers": list(multipliers),
        "detection_gate_bound_during_sweep": gate_bound,
    }
