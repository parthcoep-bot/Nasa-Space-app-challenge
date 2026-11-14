# Model card

**System:** FLARE-X analysis pipeline v0.3.0
**Date:** 2026-09-19
**Type:** Rule-based / statistical. **No trained machine-learning model is shipped.**

---

## Why there is no trained model, and why that is the right call

A supervised classifier would be easy to add and would be **indefensible right now**.

Training data would be a few hundred hand-labelled frames from a handful of tests
within a single investigation. Frames within one test are strongly autocorrelated, so
a naïve random train/test split leaks almost perfectly — neighbouring frames are
nearly identical images. A correct split would be *by test*, leaving a handful of
independent units. A cross-validation score computed on that would be a number with a
confidence interval wide enough to be meaningless, presented with a precision it does
not have.

So FLARE-X ships **Tier 1**: change-point detection plus explicit rules, with no
learned parameters. Tier 2 becomes justified when there are hand labels from enough
independent tests to split by test and still have units left over — and only if it
**beats Tier 1 on held-out labels**. If it does not, the honest outcome is to report
that and keep Tier 1.

**No ML metric appears anywhere in this repository, because none would be meaningful.**

---

## Intended use

- Extracting per-frame morphology time series from archived microgravity combustion
  video, with uncertainty and provenance.
- Locating combustion-regime transitions and checking them against an independently
  known event schedule.
- Comparing a flame's measured appearance trajectory against published qualitative
  descriptions of near-limit behaviour.
- Teaching: a worked, auditable example of measurement from scientific imagery.

## Out-of-scope use

- Predicting whether a fire will occur, or when a real flame will go out.
- Any operational or safety-critical decision.
- Certification or screening against NASA-STD-6001 or any standard.
- Declaring a material safe or unsafe.
- Inferring temperature, heat release, soot volume fraction or absolute irradiance
  from imagery. The code has no path to these and will not acquire one without
  calibrated instrumentation.
- Real-time onboard use. Nothing here has been tested for latency, robustness or
  flight qualification.

---

## Every free parameter

These are **all** of them. Nothing is hidden in a config file.

### Segmentation — `SegmentationConfig`

| Parameter | Default | What it does | How it was chosen |
|---|---|---|---|
| `high_multiplier` | 1.00 | × Otsu level for seed pixels | Otsu level as-is; no thumb on the scale |
| `low_multiplier` | 0.55 | × Otsu level for hysteresis growth | Standard hysteresis practice (~½ the high level) |
| `snr_floor` | 6.0 | Minimum peak, in noise σ | Conventional detection floor |
| `extreme_value_margin` | 1.25 | × the expected noise maximum σ√(2 ln N) | 25 % headroom above the statistical noise ceiling |
| `low_threshold_sigmas` | 3.0 | Noise floor on the growth threshold | Prevents hysteresis flooding; see VALIDATION §1 |
| `min_object_px` | 40 (60 in validation) | Detection size limit | **Reported as a limit, not a tuned value**; frames below it are counted separately |
| `min_hole_px` | 40 | Pinhole fill | Cosmetic; does not affect area materially |
| `open_radius` / `close_radius` | 1 / 2 | Morphological cleanup | Smallest values that remove single-pixel speckle |
| `keep_largest_only` | True | One flame per frame | Matches the single-sample BASS-II geometry. **Would need changing for multi-sample configurations such as Saffire-II.** |
| `background_percentile` | 5.0 | Temporal background estimate | A percentile, not a mean, so a flame dwelling on a pixel does not contaminate it |
| `exclude_regions` | () | Zeroed rectangles | **Must be set to the telemetry overlay for real BASS-II video.** Cost of omitting it: IoU 0.843 → 0.654 |

### State rules — `StateRules`

| Parameter | Default | Note |
|---|---|---|
| `growth_slope` | 0.02 /s | Normalised area slope above which a segment is GROWTH |
| `steady_slope` | 0.008 /s | Below which a segment may be QUASI_STEADY |
| `steady_cv` | 0.10 | Dispersion ceiling for QUASI_STEADY |
| `ignition_rise_fraction` | 0.15 | Steepness required to call the first live segment IGNITION |
| `extinction_area_fraction` | 0.05 | × run median area, below which collapse is called |
| `extinction_persist` | 5 frames | Persistence before extinction is declared |

All are defined on **dimensionless, normalised** quantities so they are not tied to
one camera, one scale or one flame size. They are **reporting conventions**, not
significance tests.

### Change points

| Parameter | Default | Note |
|---|---|---|
| `min_segment` | 8 frames | Shortest admissible segment |
| `beta` | 2.0 | BIC penalty scale; raise to demand stronger evidence per split |
| `max_change_points` | 30 | Safety ceiling |

Cost function is Gaussian negative log-likelihood, implemented in-repository rather
than imported, **specifically so the penalty is visible and arguable**.

### Extinction Proximity Index

| Term | Direction | Weight | Published observation it quantifies |
|---|---|---|---|
| `aspect_ratio` | +1 | 0.25 | Flame elongates toward the limit |
| `standoff` | +1 | 0.25 | Boundary layer thickens, flame lifts off, heat feedback falls |
| `sootiness_index` | −1 | 0.20 | Yellow → blue shift |
| `radiance_mean` | −1 | 0.15 | Near-limit flames are visibly dim |
| `area` | −1 | 0.15 | Projected area declines |

**Weights are chosen by reasoning, not fitted.** Fitting would require labelled
extinction-proximity ground truth, which does not exist. Standoff and elongation carry
the most weight because they are the terms most directly tied to the published
mechanism. A weight-sensitivity analysis is outstanding.

Other EPI settings: `smoothing_window` 5 frames (rolling median);
`robust_percentiles` (5, 95); `min_valid_fraction` 0.60 — below which a term is
**dropped and reported**, with remaining weights renormalising. A term is never
silently completed with a substituted value.

---

## Behaviour under failure

The design principle is that the system should **fail loudly and specifically**.

| Situation | Behaviour |
|---|---|
| Frame is pure noise | Returns empty with the reason, including the measured σ and the gate value |
| Flame smaller than `min_object_px` | Not detected; counted against the declared size limit |
| No flame in any frame | Warns explicitly and tells the user to check exclusion regions and thresholds |
| EPI term unusable | Dropped, reason recorded, weights renormalise |
| Scale unknown | Lengths in pixels, `scaled=False`, warning emitted |
| Frame rate unknown | 15 fps assumed, warning emitted, rates flagged provisional |
| Value unconfirmable | `Measurement` with `status="NOT_VERIFIED"` and a reason — never a plausible number |
| Derived value labelled as NASA fact | **Raises `ValueError`** |
| `status="OK"` with no value | **Raises `ValueError`** |

---

## Known biases

Inherited from the measurement, not the model: single-view projection, visible-band
undersizing of dim blue flames, visible edge ≠ pyrolysis front. All three are named in
the uncertainty budget; the first is deliberately left **unquantified** because one
view does not constrain it. See [LIMITATIONS.md §2](LIMITATIONS.md).

## Environmental cost

Negligible. The full validation runs in a few seconds of CPU on a laptop. No GPU, no
training, no inference service.

## Maintenance

Every number in [VALIDATION.md](VALIDATION.md) regenerates from
`python scripts/validate_pipeline.py --seed 20261114`. The 24-test suite locks the
behavioural guarantees, including the blue-flame detection property and the two
provenance-layer exceptions.
