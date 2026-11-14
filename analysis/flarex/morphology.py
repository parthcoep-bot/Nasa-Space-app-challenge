"""
flarex.morphology
=================

Physical feature extraction from a segmented flame.

DESIGN RULE: every feature is defined in the frame of the *experiment*,
not the frame of the *image*. In an opposed-flow duct the meaningful axes
are along-flow and cross-flow, and the meaningful origin is the fuel
surface. A naive bounding box in image coordinates is meaningless if the
camera is rotated or the rod is mounted diagonally, so the caller supplies
a `DuctGeometry` and every directional feature is resolved against it.

Units. Features are computed in pixels and converted with an explicit
mm/px scale. For BASS-II the still camera resolution is documented as
34 pixels/mm in the sample plane (Link et al. 2018), but the *video*
camera is a separate 760x480 device whose scale must be recovered from the
in-duct moveable scale visible in the frame. FLARE-X will not guess it:
if `mm_per_px` is None, every physical-length feature is returned in
pixels and flagged, rather than silently mis-scaled.

WHAT IS DELIBERATELY NOT COMPUTED
---------------------------------
  * temperature            (requires calibrated radiometry)
  * heat release rate      (requires calorimetry)
  * soot volume fraction   (requires a calibrated extinction/emission model)
  * absolute irradiance    (the in-duct radiometer was uncalibrated)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Literal

import numpy as np
from skimage.measure import regionprops, label, find_contours

__all__ = ["DuctGeometry", "FlameFeatures", "extract_features", "FEATURE_UNITS"]


@dataclass
class DuctGeometry:
    """Where the flow goes and where the fuel is, in image coordinates.

    flow_angle_deg : direction the oxidiser travels, measured counter-clockwise
                     from the image +x axis. For BASS-II opposed-flow rod tests
                     the flame spreads *into* this flow.
    surface_point  : any point (x, y) on the fuel surface line.
    surface_angle_deg : orientation of the fuel surface line.
    mm_per_px      : image scale. None means "unknown"; lengths stay in px.
    """

    flow_angle_deg: float = 180.0
    surface_point: tuple[float, float] | None = None
    surface_angle_deg: float | None = None
    mm_per_px: float | None = None

    @property
    def flow_unit(self) -> np.ndarray:
        a = math.radians(self.flow_angle_deg)
        return np.array([math.cos(a), math.sin(a)])

    @property
    def cross_unit(self) -> np.ndarray:
        f = self.flow_unit
        return np.array([-f[1], f[0]])

    @property
    def spread_unit(self) -> np.ndarray:
        """Opposed-flow spread is anti-parallel to the oxidiser flow."""
        return -self.flow_unit


FEATURE_UNITS: dict[str, str] = {
    "area": "mm^2 or px^2",
    "perimeter": "mm or px",
    "equivalent_diameter": "mm or px",
    "centroid_x": "mm or px",
    "centroid_y": "mm or px",
    "flame_length": "mm or px",
    "flame_width": "mm or px",
    "aspect_ratio": "dimensionless",
    "circularity": "dimensionless",
    "solidity": "dimensionless",
    "extent": "dimensionless",
    "eccentricity": "dimensionless",
    "orientation_deg": "degrees",
    "standoff": "mm or px",
    "leading_edge_position": "mm or px",
    "radiance_mean": "arbitrary (uncalibrated)",
    "radiance_p95": "arbitrary (uncalibrated)",
    "radiance_integral": "arbitrary (uncalibrated)",
    "sootiness_index": "dimensionless in [-1, 1]",
}


@dataclass
class FlameFeatures:
    """One row of the morphology time series."""

    frame_index: int
    time_s: float | None
    scaled: bool                  # True when mm_per_px was supplied

    area: float
    perimeter: float
    equivalent_diameter: float
    centroid_x: float
    centroid_y: float
    flame_length: float           # extent along the flow axis
    flame_width: float            # extent across the flow axis
    aspect_ratio: float           # length / width  (flow-aligned, not image-aligned)
    circularity: float            # 4*pi*A / P^2, 1.0 for a disc
    solidity: float
    extent: float
    eccentricity: float
    orientation_deg: float        # principal axis vs the flow axis
    standoff: float | None        # min distance flame->fuel surface, None if no geometry
    leading_edge_position: float  # projection of the upstream-most flame point
                                  # onto the spread axis
    radiance_mean: float
    radiance_p95: float
    radiance_integral: float
    sootiness_index: float
    n_pixels: int

    def to_dict(self) -> dict:
        return asdict(self)


def _principal_extent(coords_xy: np.ndarray, axis: np.ndarray) -> tuple[float, float]:
    """Projected extent of a point cloud onto a unit axis: (span, min_projection)."""
    proj = coords_xy @ axis
    return float(proj.max() - proj.min()), float(proj.min())


def _point_line_distance(points_xy: np.ndarray,
                         point_on_line: tuple[float, float],
                         angle_deg: float) -> np.ndarray:
    a = math.radians(angle_deg)
    d = np.array([math.cos(a), math.sin(a)])
    n = np.array([-d[1], d[0]])
    rel = points_xy - np.asarray(point_on_line, dtype=float)
    return np.abs(rel @ n)


def extract_features(mask: np.ndarray,
                     radiance: np.ndarray,
                     frame_rgb: np.ndarray | None = None,
                     geometry: DuctGeometry | None = None,
                     frame_index: int = 0,
                     time_s: float | None = None) -> FlameFeatures | None:
    """Compute the morphology row for one segmented frame.

    Returns None when the mask is empty — an extinguished or pre-ignition
    frame is a real observation, not a failure, and the caller records it
    as a gap in the time series rather than as a zero-area flame.
    """
    if mask is None or not mask.any():
        return None

    geo = geometry or DuctGeometry()
    s = geo.mm_per_px
    scaled = s is not None
    k_len = s if scaled else 1.0
    k_area = (s * s) if scaled else 1.0

    lab = label(mask.astype(np.uint8))
    props = regionprops(lab)
    if not props:
        return None
    rp = max(props, key=lambda p: p.area)

    ys, xs = np.nonzero(mask)
    coords_xy = np.column_stack([xs.astype(float), ys.astype(float)])

    area_px = float(rp.area)
    perim_px = float(rp.perimeter) if rp.perimeter > 0 else float("nan")
    circularity = (4.0 * math.pi * area_px / (perim_px ** 2)
                   if np.isfinite(perim_px) and perim_px > 0 else float("nan"))
    circularity = float(min(circularity, 1.0)) if np.isfinite(circularity) else circularity

    length_px, _ = _principal_extent(coords_xy, geo.flow_unit)
    width_px, _ = _principal_extent(coords_xy, geo.cross_unit)
    aspect = float(length_px / width_px) if width_px > 0 else float("nan")

    # regionprops.orientation is measured from the row axis; convert to an
    # angle relative to the flow axis so the number means something physical.
    orient_img_deg = math.degrees(rp.orientation)
    orientation_vs_flow = float((orient_img_deg - geo.flow_angle_deg + 90.0) % 180.0)

    standoff = None
    if geo.surface_point is not None and geo.surface_angle_deg is not None:
        contours = find_contours(mask.astype(float), 0.5)
        if contours:
            pts = np.vstack([c[:, ::-1] for c in contours])  # (row,col)->(x,y)
        else:
            pts = coords_xy
        standoff = float(_point_line_distance(
            pts, geo.surface_point, geo.surface_angle_deg).min() * k_len)

    spread_span, spread_min = _principal_extent(coords_xy, geo.spread_unit)
    leading_edge = float((spread_min + spread_span) * k_len)

    rad = np.asarray(radiance, dtype=float)
    vals = rad[mask]
    if vals.size == 0:
        r_mean = r_p95 = r_int = float("nan")
    else:
        r_mean = float(vals.mean())
        r_p95 = float(np.percentile(vals, 95))
        r_int = float(vals.sum())

    if frame_rgb is not None:
        from .segmentation import sootiness_index as _chi
        chi = _chi(frame_rgb, mask)
    else:
        chi = float("nan")

    cy, cx = rp.centroid

    return FlameFeatures(
        frame_index=frame_index,
        time_s=time_s,
        scaled=scaled,
        area=area_px * k_area,
        perimeter=perim_px * k_len,
        equivalent_diameter=float(getattr(rp, "equivalent_diameter_area", None) or rp.equivalent_diameter) * k_len,
        centroid_x=float(cx) * k_len,
        centroid_y=float(cy) * k_len,
        flame_length=float(length_px) * k_len,
        flame_width=float(width_px) * k_len,
        aspect_ratio=aspect,
        circularity=circularity,
        solidity=float(rp.solidity),
        extent=float(rp.extent),
        eccentricity=float(rp.eccentricity),
        orientation_deg=orientation_vs_flow,
        standoff=standoff,
        leading_edge_position=leading_edge,
        radiance_mean=r_mean,
        radiance_p95=r_p95,
        radiance_integral=r_int,
        sootiness_index=chi,
        n_pixels=int(mask.sum()),
    )
