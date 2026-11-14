# Limitations

Written to be read by someone trying to find the weak point. The ones that hurt are
at the top, not buried.

---

## 1. There is no validated scientific result yet

FLARE-X has a **validated instrument** and **no validated measurement of a real
flame**. Every metric in [VALIDATION.md](VALIDATION.md) was obtained against a
synthetic phantom with an invented appearance model.

Stage 2 — real archived video, hand-labelled frames, comparison against published
spread rates — is written and scripted but **not executed**, because it requires an
individual NASA PSI registration.

If you take one thing from this page: *the pipeline works; it has not yet been shown
to work on the data it was designed for.*

---

## 2. Measurement limitations that cannot be removed with more code

### 2.1 Projected area is not surface area
A single camera views a three-dimensional flame. Everything reported as "area" is the
**projected** area on the image plane. The projection bias is not estimable from one
view, so it is carried as a **named, unquantified bias** in the uncertainty budget
rather than being given a number. Putting a plausible figure on it would be worse than
admitting the gap.

*Would require:* a second synchronised view, or tomographic reconstruction.

### 2.2 Visible-band detection undersizes exactly the flames that matter
The segmented region is the part of the flame emitting strongly enough in the camera's
visible response to exceed threshold. A dim blue near-limit flame has a **smaller
visible footprint than its actual reaction zone**.

This bias is largest in the near-limit regime — which is the regime the entire project
is about. It cannot be corrected without calibrated radiometry or chemiluminescence
imaging (CH*/OH* filtered).

### 2.3 The leading edge is not the pyrolysis front
Spread rate is derived from the upstream-most **visible** pixel. The pyrolysis front
sits ahead of it, at a distance set by the flame standoff and the preheat length.
That offset is a **systematic bias**, not noise, and it does not average out.

*Would require:* surface thermometry or IR imaging to close.

### 2.4 Brightness is not temperature, and this is enforced
The BASS-II video camera was not radiometrically calibrated, and the in-duct Oriel
71768 thermopile is **explicitly documented as uncalibrated** *(L1)*. No function in
this repository converts pixel brightness to temperature, heat release, soot volume
fraction or absolute irradiance. The channel is named `radiance_proxy` so the
constraint is impossible to forget.

χ = (R−B)/(R+B) is a **colour index**, not colour-ratio pyrometry. Real two-colour
pyrometry needs a calibrated spectral response and an emissivity model.

---

## 3. Data limitations

### 3.1 Lengths are in pixels until someone recovers the scale
The **still** camera's 34 px/mm is documented. The **video** camera's scale is not.
They are different cameras. FLARE-X refuses to substitute one for the other, so until
the scale is recovered from the in-duct moveable scale, every length and area is in
**pixels** and flagged `scaled=False`.

Physically honest. Also less impressive in a demo. Plan for it.

### 3.2 Frame rate is unverified
Not stated in the sources reviewed. The pipeline assumes 15 fps for the time axis and
**emits a warning**; every rate derived under that assumption is provisional.

### 3.3 N = 1 investigation
Everything is built and tuned around BASS-II opposed-flow rod geometry. Generalisation
to concurrent flow, to thin fabrics, to Saffire's scale or to SoFIE's CIR imaging is
**asserted by design, not demonstrated**.

### 3.4 No dataset-level DOI was located
Cite the PSI investigation identifier plus accession date. Recorded as `NOT_VERIFIED`
rather than invented.

### 3.5 The published data are themselves acknowledged as irregular
Link et al. note their microgravity data points were not systematically taken —
astronaut time, sample count and oxygen supply were all constrained — and that oxygen
concentration and flow velocity accuracy were difficult to establish. A derived
analysis inherits that irregularity. It cannot be cleaned away downstream.

---

## 4. Method limitations

### 4.1 Three state classes are untested
The phantom is **stationary within each dwell** by construction, so `WEAKENING`,
`TRANSITION` and `RE_IGNITION` are never exercised. Their accuracy is **unmeasured**.

Adding drift to the phantom would exercise them — and would mean inventing more
physics, which makes the gap harder to see rather than smaller. It is left visible.

### 4.2 Two change points remain unexplained
10 detected, 8 matched to known events. The 2 unmatched fall **inside constant-flow
dwells** and are over-segmentation. They are reported rather than tuned away, because
raising the penalty until they disappear would also start dropping real events.

### 4.3 The rule thresholds are conventions
`growth_slope`, `steady_slope`, `steady_cv` and the ρ < −0.3 monotonicity convention
are **reporting conventions, not significance tests**. They are listed in full in
[MODEL_CARD.md](MODEL_CARD.md) so they can be argued with.

### 4.4 EPI weights are chosen, not fitted
The five weights (0.25 / 0.25 / 0.20 / 0.15 / 0.15) were assigned by reasoning about
which terms are most directly tied to the published extinction mechanism. They are
**not** fitted, because fitting them would require labelled extinction-proximity
ground truth, which does not exist. A sensitivity analysis over the weights is
outstanding work.

### 4.5 EPI monotonicity is only valid on one branch
Flame spread rate is **non-monotonic** in opposed flow velocity *(L2)* — it rises then
falls. The monotonicity check is only meaningful **below the turning point**. Applying
it across the full flow range would be a misuse, and the turning point's location
itself varies with oxygen concentration.

### 4.6 Correlation is not mechanism
If EPI tracks flow, that shows the index responds to the driving variable. It does
**not** show that the mechanism is the published radiative/transport-limited one. The
measurements are *consistent with* that mechanism; consistency is not confirmation.

---

## 5. Scope limitations — what FLARE-X is not

- **Not a fire predictor.** The EPI is not a probability and has never been evaluated
  against any real fire event.
- **Not a certification tool.** No pass/fail against NASA-STD-6001 or any standard.
- **Not NASA-endorsed, -validated or -approved.** No NASA review of this work exists.
- **Not a flammability ranking system.** No material is described as safe or unsafe;
  comparisons are labelled *"under these experimental conditions"*.
- **Not a replacement for NASA's analysis.** It is a measurement layer over data NASA
  already analysed, designed to be handed to researchers, not to compete with them.

---

## 6. Reproducibility limitations

- Reproducing Stage 1 needs only this repository. Reproducing **Stage 2 needs a PSI
  account**, which we cannot provide.
- Results are pinned to file **sha256**, so a changed input invalidates a pinned
  result loudly. That protects against drift; it does not protect against a user
  analysing a different test than they think they are.
- No container image or environment lockfile is shipped yet. Library versions
  (`scikit-image` in particular) have changed APIs recently and could shift results at
  the margin.

---

## 7. Known unknowns we would want closed first

1. Real-data segmentation accuracy **stratified by regime**, with dim blue frames
   over-represented.
2. Inter-annotator agreement (Cohen's κ) on state boundaries — if humans disagree, no
   classifier score above that ceiling means anything.
3. Whether the change-point method survives real camera noise, automatic gain control
   and astronaut hand motion, none of which the phantom contains.
4. Whether the video scale is recoverable at all from the archived frames.
5. EPI weight sensitivity.
