# Validation

Every number on this page was produced by
`python scripts/validate_pipeline.py` and is reproducible with
`--seed 20261114`. Nothing here was typed in by hand; the raw output is
[`reports/validation_phantom.json`](reports/validation_phantom.json).

---

## The two-stage structure, and why Stage 1 is not enough

**Stage 1 (complete, below): does the software measure correctly?**
Validated against a synthetic phantom whose true masks, true flow schedule and true
extinction frame are known exactly. This answers *"is my instrument working?"*

**Stage 2 (scripted, not yet run): does it measure real flames correctly?**
Requires archived BASS-II video, which requires an individual NASA PSI registration.
The procedure is written and scripted; see §5. **Until Stage 2 is run, FLARE-X has
no validated scientific result — only a validated instrument.**

We state this plainly because the alternative — presenting Stage 1 numbers as if
they said something about microgravity combustion — is the single most likely way
this project could mislead someone.

> ⚠ **Every metric in §§1–4 is a property of the software, measured against an
> invented target. None is a measurement of a flame.** The phantom's
> flow→appearance relationships are smooth monotone curves chosen to have the right
> *structure*; they are not fits to data and they encode no physical claim.

---

## 1. Segmentation accuracy

Scored per frame against the exact generating mask. *n* = **332** scored frames.

| Metric | Value |
|---|---|
| IoU, mean | **0.843** |
| IoU, median | 0.844 |
| IoU, 5th percentile | 0.829 |
| IoU, minimum | 0.798 |
| Dice, mean | **0.915** |
| Dice, median | 0.915 |
| False positives on frames with no flame | **0** |

The zero false-positive count matters more than the IoU. An earlier build of the
segmenter reported **25** false-positive frames after extinction, because Otsu's
method returns a threshold on *any* input including pure sensor noise. That defect
would have corrupted every extinction time the system produced. It was found by this
harness and fixed with a two-part noise gate:

- **Detection gate.** The expected maximum of *N* independent Gaussian samples grows
  as σ√(2 ln N) — about 5σ over a 760×480 frame — so a fixed "6σ" rule sits barely
  above the noise ceiling. The gate is set relative to that extreme-value scale.
- **Hysteresis floor.** The growth threshold needs its own noise floor, or a valid
  seed grows through the noise field and floods the frame. Observed directly: a
  5186-pixel "flame" on an 80×80 pure-noise test.

Both fixes are in `analysis/flarex/segmentation.py` with the reasoning in comments,
and both are locked by tests.

### 1a. Detection size limit — reported, not hidden

The segmenter discards connected components below `min_object_px` (60 px here).
**3 frames** during the ignition ramp had true flames smaller than that limit. They
are excluded from the IoU statistic and counted separately, because scoring a
declared detection limit as an algorithm failure would misattribute the error.
**0 frames** above the limit were missed.

### 1b. Overlay ablation — quantifying a real-data hazard

The archived BASS-II video carries a **burned-in telemetry overlay** (N₂ flow rate,
fan voltage, anemometer reading, radiometer signal). It is bright, it is in frame,
and it is not flame.

| Configuration | IoU, mean |
|---|---|
| Overlay region excluded | **0.843** |
| Overlay region left in | **0.654** |

A **22.4 % relative degradation** from an artefact that is present in the real data
and that a naïve pipeline would never think to mask. This ablation is why the
phantom renders an overlay strip at all.

### 1c. Segmentation uncertainty — measured, not asserted

Both hysteresis thresholds are swept together over ±20 %:

| Quantity | Value |
|---|---|
| Nominal area | 2485 px |
| Half-range across the sweep | 98 px |
| **Relative standard uncertainty** | **3.1 %** |

This is the number quoted as the Type-B segmentation term in the area budget. A
sweep of the *high* threshold alone was tried first and reported ≈0 % uncertainty —
correctly, because in hysteresis thresholding the grown region is set by the *low*
threshold. That near-no-op would have produced a falsely confident error bar.

---

## 2. Change-point detection

Detected change points scored against the exactly known event frames.

### Against the commanded flow steps only (6 events)

| | |
|---|---|
| Detected | 10 |
| True positives | 6 |
| Precision | 0.600 |
| Recall | **1.000** |
| F1 | 0.750 |

### Against all known events — flow steps + ignition + extinction (8 events)

| | |
|---|---|
| Detected | 10 |
| True positives | **8** |
| False positives | 2 |
| False negatives | **0** |
| Precision | **0.800** |
| Recall | **1.000** |
| F1 | **0.889** |
| Median offset | **0.0 frames** |
| Mean absolute offset | **0.125 frames** |
| Matching tolerance | ±6 frames |

**Both tables are reported deliberately.** Scoring only against the flow steps
charges the detector with "false positives" for correctly finding ignition and
extinction — real events absent from a flow-step list. Reporting only the second
table would hide that 2 detections remain genuinely unexplained. Those 2 fall inside
constant-flow dwells and are over-segmentation.

Sub-frame localisation (mean |offset| = 0.125 frames) is the result that transfers:
it means the method can align an image-derived transition to a commanded event
without a hand-tuned lag.

---

## 3. Extinction Proximity Index

| Check | Result |
|---|---|
| Spearman ρ, EPI vs commanded flow velocity | **−0.989** |
| Status | CONSISTENT_WITH_EXPECTATION |
| EPI, median over the first dwell | 0.111 |
| EPI, at the last frame with a flame | **0.850** |

The index rises monotonically as commanded flow falls toward the limit and reaches
0.85 at the last frame where a flame exists.

**What this does and does not establish.** It establishes that the index is
correctly wired: the five terms combine with the right signs and the composite
tracks the driving variable. It establishes **nothing** about whether real flames
behave this way, because the phantom was built to have this behaviour. Stage 2 is
the test that could falsify it.

The monotonicity check is also the **falsification route**. If a real run returns
ρ > −0.3 the reported status is `NOT_SUPPORTED`, and that is the result.

### A physics caveat that constrains where this check is valid

Link et al. (2018) report the flame spread rate is **non-monotonic** in opposed flow
velocity — it rises, then falls, as flow increases. EPI is therefore only expected to
be monotone on the **low-velocity branch below the turning point**. Applying the
monotonicity check across the full flow range without splitting at the turning point
would be a misuse of it. This constraint is in the function's docstring, not just
here.

---

## 4. Combustion-state labelling — partially untested, and this is a real gap

The phantom is **stationary within each dwell** by construction. Consequently the
labeller correctly returns `QUASI_STEADY` for every dwell, `IGNITION` and `GROWTH`
for the ramp, and `POST_EXTINCTION` after flame loss.

**The `WEAKENING`, `TRANSITION` and `RE_IGNITION` classes are therefore not
exercised by this harness, and their accuracy is unmeasured.** Real flames drift
within a nominally constant condition; the phantom does not. Adding drift would mean
inventing more physics, which would not make the test more honest — it would only
make the gap harder to see.

These three classes require hand-labelled archived frames. That work is Stage 2.

---

## 5. Stage 2 — real-data validation procedure

Written and scripted. Not yet executed.

**5.1 Segmentation against manual ground truth.** Hand-label ≥100 frames spanning
high-flow, mid-flow, near-limit and post-extinction regimes, stratified so the dim
blue near-limit frames are over-represented — that is where a visible-band segmenter
is weakest and where the science is. Report IoU and Dice **per regime**, not pooled;
a pooled mean dominated by easy bright frames would conceal failure exactly where it
matters. With ~100 frames from a small number of tests, report the number of frames
and the number of independent tests alongside every metric.

**5.2 Change points against the commanded flow schedule.** Read the flow steps from
the burned-in telemetry overlay and from the test record. Score with the §2 metric.
This is the test with real falsification power, because the reference is independent
of the imagery being analysed.

**5.3 Physical cross-check against published values.** Derive the flame spread rate
by tracking the segmented leading edge and compare against the spread rates
published in Link et al. (2018) for matched sample diameter, oxygen concentration and
flow velocity. Agreement within the combined uncertainty would support the extractor;
disagreement is informative either way. **Note the systematic offset that cannot be
removed:** the upstream-most *visible* pixel is not the pyrolysis front, and the gap
between them needs a surface-temperature measurement to close.

**5.4 EPI monotonicity on real runs.** Apply §3 per test, restricted to the
low-velocity branch. Report every run including failures.

**5.5 Inter-annotator agreement.** Two annotators label an overlapping subset;
report Cohen's κ. If human annotators disagree on where GROWTH becomes QUASI_STEADY,
no classifier score above that ceiling is meaningful.

---

## 6. Deliberately absent

- **No trained ML model is shipped, and no ML metrics are reported.** A supervised
  classifier is only justified if it beats the transparent rule baseline on held-out
  labels. Those labels do not exist yet. Reporting a cross-validation score on a few
  hundred frames from one experiment would be reporting a number that cannot
  generalise. See [MODEL_CARD.md](MODEL_CARD.md).
- **No accuracy figure for real microgravity flames**, for the reason in §5.
- **No comparison against a NASA baseline system**, because we found no published
  open baseline for per-frame morphology extraction from this data to compare against.
