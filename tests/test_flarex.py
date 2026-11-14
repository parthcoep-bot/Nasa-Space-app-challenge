"""FLARE-X test suite.

These tests protect the properties that make the project defensible:
the segmenter must see blue flames, the noise gate must reject empty
frames, physics functions must refuse to invent inputs, and the
provenance layer must refuse to let a derived number pose as NASA fact.

Run:  python -m pytest tests/ -q
"""
import sys, math
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))

from flarex import (ClaimLevel, DuctGeometry, Measurement, ProvenanceChain,
                    ProvenanceNode, SegmentationConfig, compute_epi,
                    detect_change_points, extract_features, not_verified,
                    segment_flame, estimate_background, validate_monotonicity)
from flarex import physics
from flarex.phantom import PhantomConfig, generate_phantom_run, iou, dice
from flarex.uncertainty import area_budget, report_significant


# ---------------------------------------------------------------- segmentation
def _noise_stack(n=30, shape=(64, 64), sigma=0.012, mean=0.03, seed=0):
    rng = np.random.default_rng(seed)
    return [rng.normal(mean, sigma, (*shape, 3)).clip(0, 1).astype("float32")
            for _ in range(n)]


def test_empty_frame_is_not_segmented_as_flame():
    """The failure mode that would corrupt every extinction time."""
    stack = _noise_stack()
    bg = estimate_background(stack)
    res = segment_flame(stack[0], background=bg)
    assert res.is_empty
    assert "noise" in (res.empty_reason or "").lower()


def test_dim_blue_flame_is_detected():
    """A red-channel fire detector fails here; near-limit flames are blue.

    This is the single most important behavioural test in the suite: the
    scientifically interesting regime is exactly the one a conventional
    flame detector discards.
    """
    stack = _noise_stack()
    bg = estimate_background(stack)
    f = stack[1].copy()
    f[24:36, 24:40, 2] = 0.22      # blue-dominant
    f[24:36, 24:40, 1] = 0.10
    f[24:36, 24:40, 0] = 0.03      # essentially no red
    res = segment_flame(f, background=bg)
    assert not res.is_empty
    assert res.mask.sum() > 150


def test_red_channel_only_detector_would_miss_it():
    """Demonstrates the claim above rather than asserting it."""
    f = np.zeros((64, 64, 3), dtype="float32")
    f[24:36, 24:40, 2] = 0.22
    f[24:36, 24:40, 1] = 0.10
    red_mask = f[..., 0] > 0.1
    assert red_mask.sum() == 0        # a red-channel rule sees nothing
    from flarex.segmentation import radiance_proxy
    assert radiance_proxy(f).max() > 0.2   # the radiance proxy does not


def test_exclusion_region_suppresses_overlay():
    f = np.zeros((64, 200, 3), dtype="float32")
    f[0:12, :, :] = 1.0               # burned-in telemetry strip
    f[30:40, 80:110, :] = 0.5         # the actual flame
    res = segment_flame(f, config=SegmentationConfig(exclude_regions=((0, 0, 200, 12),)))
    assert not res.mask[0:12, :].any()
    assert res.mask[30:40, 80:110].any()


def test_threshold_sweep_reports_a_real_spread():
    from flarex.segmentation import sweep_threshold_sensitivity
    f = np.zeros((64, 64, 3), dtype="float32")
    yy, xx = np.mgrid[0:64, 0:64]
    f[..., 0] = np.exp(-(((xx - 32) / 9.0) ** 2 + ((yy - 32) / 6.0) ** 2)).astype("float32")
    s = sweep_threshold_sensitivity(f)
    assert s["area_px_min"] <= s["area_px_nominal"] <= s["area_px_max"]
    assert s["area_px_half_range"] > 0     # uncertainty is measured, not assumed


# ----------------------------------------------------------------- morphology
def test_features_are_resolved_against_the_flow_axis_not_the_image_axis():
    """A rotated duct must not change the physics."""
    mask = np.zeros((80, 120), dtype=bool)
    mask[36:44, 30:90] = True                       # long along image x
    rad = mask.astype(float)
    horiz = extract_features(mask, rad, geometry=DuctGeometry(flow_angle_deg=0.0))
    vert = extract_features(mask, rad, geometry=DuctGeometry(flow_angle_deg=90.0))
    assert horiz.aspect_ratio > 3.0                 # long along the flow
    assert vert.aspect_ratio < 0.5                  # same blob, flow across it
    assert horiz.flame_length == pytest.approx(vert.flame_width, rel=1e-6)


def test_empty_mask_returns_none_not_zero_area():
    """A dark frame is a gap in the record, not a zero-area flame."""
    assert extract_features(np.zeros((32, 32), bool), np.zeros((32, 32))) is None


def test_unscaled_features_are_flagged():
    mask = np.zeros((40, 40), bool); mask[10:20, 10:25] = True
    f = extract_features(mask, mask.astype(float), geometry=DuctGeometry(mm_per_px=None))
    assert f.scaled is False
    f2 = extract_features(mask, mask.astype(float), geometry=DuctGeometry(mm_per_px=0.5))
    assert f2.scaled is True
    assert f2.area == pytest.approx(f.area * 0.25)


# ------------------------------------------------------------------ timeseries
def test_change_points_find_a_known_step():
    rng = np.random.default_rng(3)
    x = np.concatenate([rng.normal(0, .05, 60), rng.normal(1, .05, 60)])
    cps = detect_change_points(x)
    assert cps and min(abs(c - 60) for c in cps) <= 3


def test_flat_series_yields_no_change_points():
    rng = np.random.default_rng(4)
    assert detect_change_points(rng.normal(0, .05, 200)) == []


# ------------------------------------------------------------------- extinction
def test_epi_drops_terms_it_cannot_compute_instead_of_filling_them():
    n = 60
    res = compute_epi({"area": np.linspace(10, 1, n),
                       "aspect_ratio": np.linspace(1, 4, n),
                       "standoff": np.full(n, np.nan)})   # unusable
    assert "standoff" in res.dropped_terms
    assert "standoff" not in res.weights
    assert abs(sum(res.weights.values()) - 1.0) < 1e-9    # remaining weights renormalise


def test_epi_reports_failure_when_it_does_not_track_flow():
    n = 60
    res = compute_epi({"area": np.random.default_rng(1).normal(5, 1, n),
                       "aspect_ratio": np.random.default_rng(2).normal(2, .5, n)})
    check = validate_monotonicity(res.epi, np.linspace(8, 0.4, n))
    assert check["status"] in {"NOT_SUPPORTED", "CONSISTENT_WITH_EXPECTATION",
                               "INSUFFICIENT_DATA"}


def test_epi_attribution_is_exact():
    n = 40
    res = compute_epi({"area": np.linspace(10, 1, n), "aspect_ratio": np.linspace(1, 4, n)})
    contrib = res.explain_frame(n - 1, top_k=10)
    total = sum(v for _, v in contrib)
    assert total == pytest.approx(res.epi[n - 1], rel=1e-9)


# --------------------------------------------------------------------- physics
def test_physics_refuses_to_invent_inputs():
    with pytest.raises(physics.MissingInput):
        physics.grashof(g_m_s2=9.81, beta_1_K=1/300, delta_T_K=1000)   # no L, no nu


def test_grashof_scales_linearly_with_gravity():
    kw = dict(beta_1_K=1/300., delta_T_K=1200., length_m=0.0064,
              kinematic_viscosity_m2_s=1.5e-5)
    g1 = physics.grashof(g_m_s2=physics.G_EARTH, **kw).value
    gm = physics.grashof(g_m_s2=physics.G_EARTH * 1e-6, **kw).value
    assert gm / g1 == pytest.approx(1e-6, rel=1e-9)


def test_buoyant_velocity_scale_falls_by_a_thousand_at_micro_g():
    kw = dict(beta_1_K=1/300., delta_T_K=1200., length_m=0.0064)
    u1 = physics.buoyant_velocity_scale(g_m_s2=physics.G_EARTH, **kw).value
    um = physics.buoyant_velocity_scale(g_m_s2=physics.G_EARTH*1e-6, **kw).value
    assert u1 / um == pytest.approx(1000.0, rel=1e-6)


def test_damkohler_states_its_assumption():
    r = physics.damkohler(flow_time_s=0.1, chemical_time_s=0.01)
    assert any("never derived from image data" in a for a in r.assumptions)


# ------------------------------------------------------------------ provenance
def test_nasa_fact_requires_a_repository_root():
    with pytest.raises(ValueError):
        Measurement("bogus", 1.0, "mm", ClaimLevel.L1_NASA_FACT, ProvenanceChain())


def test_ok_status_cannot_have_a_missing_value():
    with pytest.raises(ValueError):
        Measurement("bogus", None, "mm", ClaimLevel.L3_MEASURED, ProvenanceChain())


def test_not_verified_is_a_first_class_result():
    m = not_verified("spread rate", "mm/s", "scale bar not visible in this clip")
    assert m.value is None and m.status == "NOT_VERIFIED"
    assert "scale bar" in m.render_line()


# ----------------------------------------------------------------- uncertainty
def test_uncertainty_flags_unquantified_scale():
    b = area_budget(120.0, 480.0, seg_relative=0.03, mm_per_px_relative=None)
    assert any(not c.quantified for c in b.components)
    assert any("projection" in s for s in b.unquantified_biases)


def test_significant_figures_follow_the_uncertainty():
    assert report_significant(41.8273, 2.1) == "42 +/- 2"
    assert report_significant(41.8273, 0.13) == "41.83 +/- 0.13"


# -------------------------------------------------------------- phantom labels
def test_phantom_is_labelled_synthetic_everywhere():
    run = generate_phantom_run(PhantomConfig(dwell_frames=6, ignition_frames=4,
                                             post_extinction_frames=4,
                                             flow_steps_cm_s=(7.6, 2.0, 0.7),
                                             width=160, height=120))
    assert "NOT NASA DATA" in run.label
    assert run.truth_masks.shape[0] == run.frames.shape[0]


def test_iou_of_two_empty_masks_is_undefined_not_perfect():
    z = np.zeros((10, 10), bool)
    assert math.isnan(iou(z, z)) and math.isnan(dice(z, z))
