# Scientific method

The chain this project is held to, at every step:

```
QUESTION → HYPOTHESIS → DATA → METHOD → RESULT → INTERPRETATION → LIMITATION
```

Each numbered claim below carries a **claim level**. The provenance layer enforces
the distinction in code: constructing a measurement labelled `L1_NASA_FACT` without a
repository root in its chain raises an exception.

| Level | Meaning |
|---|---|
| **L1** | NASA-documented fact — hardware, protocol, instrument specification, metadata |
| **L2** | Peer-reviewed published finding |
| **L3** | Measured by FLARE-X from archived data |
| **L4** | Derived analytically by FLARE-X from L3 quantities |
| **L5** | FLARE-X forward concept — not an observation |

---

## 1. Question

**Starting point (the challenge prompt).** *How does combustion behaviour change when
buoyancy is suppressed, what patterns can be extracted from NASA combustion
experiments, and how can those improve spacecraft fire-safety engineering?*

That question is correct and far too large for any single dataset to answer. It is a
research programme, not a hypothesis. Answering it "yes, flames change" would be
restating L2 literature as if it were a result.

**Refined question.**

> In BASS-II opposed-flow flame spread over PMMA rods, the commanded oxidiser flow
> was stepped downward in quasi-steady increments until extinction. Can a per-frame,
> image-derived morphological feature set recover those imposed steps as detectable
> change points, and does the resulting morphology-versus-flow response carry a
> reproducible, monotone signature of approach to the low-velocity extinction limit?

### Why this refinement, specifically

The refinement came from reading the *protocol*, not from narrowing for its own sake.
Three properties of BASS-II make this question answerable where the broad one is not:

1. **The experiment is piecewise-stationary by construction.** *(L1/L2)* Ignition at
   relatively high opposed flow, quasi-steady spread within about a minute, then the
   flow stepped down with a dwell at each level until extinction. Every transition is
   an *externally imposed* event, not something inferred from the data being analysed.

2. **The reference is inside the frame.** *(L1)* The BASS-II video camera carried a
   burned-in digital overlay displaying the hot-wire anemometer reading and fan
   voltage. The independent ground truth for scoring detected change points is
   literally in the pixels — a property that is rare and that most archived
   experimental video does not have.

3. **The interesting regime is visually distinctive.** *(L2)* Near the limit the flame
   is reported to become longer, more spherical, dimmer, and to shift from yellow to
   blue. Those are appearance changes, and appearance is what an image-derived feature
   set can measure.

This question is **falsifiable in a single run**: if the detected change points do not
coincide with the commanded flow steps, the method has failed, and the repository is
built to say so rather than to explain it away.

---

## 2. Hypotheses

Only hypotheses the available data can actually test are retained.

### H1 — Event recovery *(testable now; primary falsification route)*
Change points detected jointly on (area, aspect ratio, radiance) coincide with the
commanded flow steps within a stated frame tolerance.

- **Falsified if:** recall against the commanded schedule is low, or the offset
  distribution is wide or biased.
- **Stage 1 status:** recall 1.000, mean |offset| 0.125 frames on the phantom.
- **Stage 2:** must be repeated on archived video. Until then H1 is *supported for the
  software, untested for the data.*

### H2 — Morphology quantifies published qualitative trends *(testable)*
On the low-velocity branch, flow-axis flame length and aspect ratio **increase**, and
sootiness index χ and relative radiance **decrease**, monotonically as commanded flow
falls toward the limit.

- This is the hypothesis that does the real scientific work, because it converts an
  L2 qualitative description into an L3 measurement with an error bar.
- **Falsified if:** any term's rank correlation with flow has the wrong sign on the
  low-velocity branch.

### H3 — Composite indicator *(testable)*
The Extinction Proximity Index is negatively rank-correlated with commanded opposed
flow velocity on the low-velocity branch (reporting convention: ρ < −0.3 taken as
consistent).

- **Falsified if:** ρ > −0.3, reported as `NOT_SUPPORTED`. The function returns that
  status; it is not an error path.

### H4 — Standoff as the mechanistic term *(partially testable)*
Minimum flame-to-surface distance increases toward the limit, consistent with the
published interpretation that a thickening boundary layer reduces heat feedback to the
fuel and that surface re-radiation comes to dominate the solid-phase energy balance.

- **Caveat that keeps this honest:** we measure the *visible* standoff, in projection,
  from one camera. We do not measure heat flux. Consistency with the published
  mechanism is not confirmation of it.

### Hypotheses considered and dropped

- **Cross-investigation feature comparison.** Dropped: FLEX and ACME have no solid
  pyrolysis front, Saffire differs in scale by roughly 15× and in flow configuration.
  See [DATA_SOURCES.md §3](DATA_SOURCES.md).
- **Absolute flame temperature from colour.** Dropped: the video is not
  radiometrically calibrated and the in-duct radiometer is documented as uncalibrated
  *(L1)*. Colour ratio pyrometry would require a calibrated two-colour setup and a
  known emissivity model. χ is reported as a **colour index**, never a temperature.
- **Material ranking as "safe" / "unsafe".** Dropped: no dataset of this size supports
  a flammability ranking. Any material comparison is labelled *"under these
  experimental conditions"* and names them.

---

## 3. Data

Selected: **BASS-II**, PSI Combustion Science. Full review, including everything
rejected and why, in [DATA_SOURCES.md](DATA_SOURCES.md).

**What FLARE-X refuses to assume.** Video frame rate and video px/mm scale are both
`NOT_VERIFIED`. The still camera's documented 34 px/mm is **not** substituted for the
video camera's scale — they are different cameras with different optics. Until the
scale is recovered from the in-duct moveable scale, every length is reported in
**pixels** and flagged as unscaled. This is enforced by `FlameFeatures.scaled`.

---

## 4. Method

### 4.1 Why a conventional flame detector is the wrong instrument *(design decision)*

*(L2)* Near-limit microgravity flames are **dim and blue** — the published
interpretation being reduced soot production and reduced flame temperature as flow
falls below about 1 cm/s.

Almost every off-the-shelf fire detector keys on the red channel or a fire-coloured
hue range. Applied here, it suppresses the flame exactly where the science is.

FLARE-X therefore:
- segments on `V = max(R,G,B)`, a **soot-independent** radiance proxy that responds to
  the soot continuum and to CH*/C₂ chemiluminescence alike;
- treats colour as a **separate measured feature**, χ = (R−B)/(R+B), which *quantifies*
  the yellow→blue transition instead of being defeated by it.

Locked by `test_red_channel_only_detector_would_miss_it`.

### 4.2 Segmentation

Hysteresis thresholding, seeds above a high level grown through pixels above a low
level, with an absolute noise gate in front. The gate is set relative to the
**extreme-value** noise scale σ√(2 ln N) rather than a bare multiple of σ, because the
expected maximum of a 760×480 noise field is already ≈5σ. Both thresholds carry
independent noise floors. Rationale and the defect this fixed:
[VALIDATION.md §1](VALIDATION.md).

The burned-in telemetry overlay is excluded by an explicit region mask. Quantified
cost of not doing so: IoU 0.843 → 0.654.

### 4.3 Morphology

Every directional feature is resolved against a supplied `DuctGeometry` — the flow
axis and the fuel surface line — **not** against the image axes. A bounding box in
image coordinates is meaningless if the camera is rotated or the rod is mounted
diagonally. Locked by
`test_features_are_resolved_against_the_flow_axis_not_the_image_axis`.

An empty mask returns `None`, not a zero-area flame. A dark frame is a **gap in the
record**, which is a different thing from a flame of zero size, and the distinction
propagates all the way to the state labeller.

### 4.4 Transparent baseline before any learning

**Tier 1 (shipped):** multivariate binary segmentation for change points with a
BIC-style penalty, plus explicit rule-based state labelling. No learned parameters, so
it cannot silently memorise a dataset, and every boundary traces to an inequality a
reviewer can check by hand.

**Tier 2 (not shipped):** a supervised classifier is justified only if it beats Tier 1
on held-out hand labels. Those labels do not exist yet, so **no model is shipped and no
ML metric is reported.** See [MODEL_CARD.md](MODEL_CARD.md).

### 4.5 The composite indicator

Five terms, each a quantification of a *published* qualitative observation rather than
a free parameter: elongation ↑, standoff ↑, sootiness ↓, radiance ↓, area ↓.
Normalisation direction is fixed per term, so the index cannot be tuned per run by
flipping a sign. Because it is a weighted sum of normalised terms, per-frame
attribution is **exact** — not a SHAP approximation of an opaque model.

---

## 5. Result

Stage 1 results (software accuracy against exact synthetic ground truth) are in
[VALIDATION.md](VALIDATION.md). **There is no Stage 2 result yet**, and the repository
does not present Stage 1 numbers as combustion findings.

---

## 6. Interpretation

*(L2, the published mechanism — not ours)* At very low opposed flow the flame is weak
and sits away from the surface behind a thickened boundary layer. Heat transfer from
flame to solid falls, surface re-radiation comes to dominate the energy balance, and
oxygen transport to the reaction zone becomes limiting. The flame quenches at a
limiting low flow velocity — the radiative / oxygen-transport-limited branch.

*(L1, why gravity matters quantitatively)* Gravity enters through the body-force term,
so Gr ∝ g. Between 1 g and ~10⁻⁶ g the Grashof number falls by six orders of magnitude
and the buoyant velocity scale u_b ~ √(gβΔTL) by three. The flame-induced buoyant flow
in normal gravity is of order 30 cm/s *(L2)* — larger than the 0.4–8 cm/s forced flows
used in these microgravity tests, and larger than spacecraft ventilation flows of order
0.1 m/s. In free fall that transport channel is simply gone.

*(L4, what FLARE-X adds)* A per-frame, uncertainty-bearing quantification of the
appearance changes associated with that mechanism, traceable to a file hash.

---

## 7. Limitation

Every result above is bounded by: projection from one camera, visible-band detection,
unscaled lengths, a leading edge that is not the pyrolysis front, untested state
classes, and N = 1 investigation. Full list in [LIMITATIONS.md](LIMITATIONS.md).

**The governing limitation:** FLARE-X currently has a validated *instrument* and no
validated *scientific result*. Stage 2 is the work that would change that.
