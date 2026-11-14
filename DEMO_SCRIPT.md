# Demo script

Three artefacts: the 3-minute judge demo, the 90-second video, and the 10-slide deck.

---

## 1. Three-minute judge demo

Times are cues, not a countdown. If a judge interrupts, the interruption is the demo.

**0:00 — The problem.**
"A fire starts inside a sealed spacecraft. There is no window to open, no outside to
evacuate to, and a fixed amount of suppressant. Everything we know about how that fire
behaves was learned on a planet with gravity."

**0:15 — Why microgravity changes it.**
"On Earth a flame heats gas, the gas gets less dense, gravity pulls it up. That buoyant
flow is about 30 cm/s — far more than the ventilation flows in a cabin. Grashof number
scales linearly with g. Drop g by six orders of magnitude and buoyancy stops being the
thing that feeds the flame. What's left is forced flow, diffusion and radiation."

**0:30 — The data, and what we didn't use.**
"BASS-II, on the ISS: PMMA rods in a small flow duct. We also looked at FLEX and ACME
and rejected them — droplet and gaseous flames have no solid pyrolysis front, so one
feature set over both gives numbers that look comparable and aren't. We rejected
Saffire too: fifteen times the scale, and concurrent instead of opposed flow."

**0:45 — The protocol, and the trick.**
"The astronaut ignited at high flow, then stepped the flow *down*, waiting at each
level, until the flame went out. And the camera's burned-in overlay shows the
anemometer reading. So the ground truth for our analysis is inside the video."

**1:00 — Run it.** *(start the analysis)*

**1:15 — Segmentation.** *(show red-channel mask vs radiance-proxy mask)*
"Near the limit the flame is dim and blue. A standard fire detector keys on red and
sees nothing — here's that mask, it's empty. We segment on max-RGB, which catches soot
glow and chemiluminescence alike, and then we measure colour *separately* as a feature.
The flame turning blue is the story, and it's also term three of our index."

**1:30 — Morphology.** *(scrub the timeline)*
"Area, length, width, standoff — all resolved against the flow axis, not the image
axis, so a rotated camera doesn't change the physics."

**1:45 — Change points.** *(overlay detected vs commanded)*
"These are the transitions we detected. These are the flow steps the astronaut
commanded. On our validation run: recall one-point-oh, mean offset an eighth of a
frame. That's the falsification test — if they hadn't lined up, the method failed."

**2:00 — The index.** *(EPI with attribution bars)*
"Extinction proximity. Five terms, each one quantifying something NASA already
published *qualitatively* — longer, higher standoff, bluer, dimmer, smaller. It's a
weighted sum, so this attribution is exact, not a SHAP estimate of a black box. And
it's labelled what it is: a research-prototype indicator. Not a probability. Not a
risk score."

**2:15 — The physics.**
"Why it goes out: thick boundary layer, flame stands off, heat feedback to the fuel
drops, surface re-radiation takes over, oxygen transport becomes limiting. That's the
published mechanism. We measure appearance consistent with it — consistency isn't
confirmation, and we say so."

**2:30 — Forward concept.** *(L5 banner visible)*
"Camera, edge flame-state detection, crew and ground decision support. Labelled level
five: a concept, not an observation. It's plausible because our tier-one method is
rule-based and cheap enough to run at the edge."

**2:45 — Why it matters on Earth and next.**
"NASA-STD-6001 Test 1 is an upward flame propagation test — in normal gravity. The
published result is that the limiting oxygen concentration can be *lower* in
microgravity. That's not our claim; it's why NASA's own SoFIE objectives include
validating 1-g protocols for low-gravity fires. SoFIE is the next dataset, and this
extractor is built to point at it."

**3:00 — Close.**
"NASA measured this. We made it measurable, frame by frame, with error bars and a chain
back to the file hash. And here's what we *don't* know: we haven't validated on the
real video yet — that needs a PSI account and a hundred hand-labelled frames. The
instrument is built. The measurement is next."

### If a judge pushes

- *"So what's the AI?"* — "Change-point detection and rule-based labelling, no learned
  parameters. We deliberately shipped no trained model: a few hundred autocorrelated
  frames from one experiment would give a cross-validation score that can't
  generalise. The model card explains why."
- *"Isn't this just image processing?"* — "It is, plus a falsification test. The change
  points have to land on a schedule that's independent of the pixels. That's the
  difference between measuring and decorating."
- *"Can NASA use it?"* — "It's MIT-licensed and it runs offline. Whether it's useful is
  for the SoFIE team to judge, not us. We'd hand it over, not compete with them."

---

## 2. Ninety-second video

| Time | Visual | Voiceover |
|---|---|---|
| 0:00–0:08 | Candle flame, 1 g, teardrop | "On Earth, fire rises. Hot gas is less dense, gravity pulls it up, and the flame takes the shape we all recognise." |
| 0:08–0:16 | Same flame, buoyancy term fading to zero | "Remove gravity and that shape has no reason to exist." |
| 0:16–0:26 | ISS, MSG glovebox, flow duct | "NASA flew this on the Space Station. A rod of acrylic. A small wind tunnel. Oxidiser stepped down, level by level, until the flame went out." |
| 0:26–0:36 | Archived frame with telemetry overlay highlighted | "The flow reading is burned into the video. The ground truth is inside the data." |
| 0:36–0:46 | Segmentation contour appearing | "NASA's paper says that near the limit the flame gets longer, dimmer, and turns from yellow to blue. True. Published. Never measured frame by frame." |
| 0:46–0:56 | Morphology traces building | "FLARE-X measures it. Area, length, standoff, colour — every frame, with an error bar." |
| 0:56–1:06 | Change points snapping onto flow steps | "The transitions we detect land on the flow steps the astronaut commanded, to within an eighth of a frame." |
| 1:06–1:16 | EPI rising with attribution bars | "And an extinction proximity index you can take apart term by term. Not a prediction. A measurement of how far the flame has moved toward the limit." |
| 1:16–1:24 | Provenance chain animating | "Every number traces back to a file hash." |
| 1:24–1:30 | Title card | "We haven't validated on the real video yet. That's next. The instrument is built." |

**Scientific evidence per scene:** 0:08 Gr ∝ g; 0:16 BASS-II hardware *(L1)*;
0:26 camera overlay *(L1)*; 0:36 near-limit morphology *(L2, Link et al. 2018)*;
0:46–1:16 FLARE-X measurement *(L3/L4)*; 1:30 honest status.

**Rule for the edit:** any synthetic frame carries a visible `SYNTHETIC — NOT NASA
DATA` label. No exceptions, including in the 30-second cut.

---

## 3. Ten-slide deck

| # | Title | Visual | Key text | Speaker note | Source |
|---|---|---|---|---|---|
| 1 | The fire you can't walk away from | Sealed module, small flame | No window. No outside. Fixed suppressant. | Set stakes in 15 s. Don't dramatise beyond the physics. | Jomaas 2015; Link 2018 |
| 2 | Take away the rising | 1 g vs µg flame, Gr ∝ g | Buoyant flow ≈ 30 cm/s in 1 g. In free fall, gone. | Gr falls 10⁶×; u_b falls 10³×. | Link 2018 *(L2)* |
| 3 | What NASA flew — and what we left out | PSI listing, rejections struck through | BASS-II selected. FLEX, ACME, Saffire rejected, with reasons. | The rejections are the credibility. | PSI listing *(L1)* |
| 4 | Published, but not quantified | Paper quote beside an empty plot | "Longer, dimmer, bluer" — qualitative, per-frame never measured. | State the gap without overclaiming novelty. | Link 2018 *(L2)* |
| 5 | FLARE-X | Interface, contour + traces + EPI | Video → segmentation → morphology → states → index → provenance. | 20 s max. Let the tool speak. | — |
| 6 | Why a fire detector fails here | Red-channel mask empty; radiance mask full | Near-limit flames are dim and blue. | The single most important engineering decision. | `test_red_channel_only...` |
| 7 | Results, and two defects we caught | Metrics table + the fixes | IoU 0.843 · Dice 0.915 · 0 false positives · CP recall 1.00, mean offset 0.125 fr. | Say out loud: synthetic ground truth, not combustion findings. | VALIDATION.md |
| 8 | Experiment → spacecraft | Concept diagram, **L5** banner | Camera → edge detection → crew/ground support. | Name the TRL honestly. | SoFIE heritage |
| 9 | Earth, and here | 1-g test rig beside µg frame | Flammability standards are written for 1 g. Transfers to cone-calorimeter and LOI footage. | NASA-STD-6001 Test 1 is a 1-g upward test. | standards.nasa.gov *(verified 2026-09)* |
| 10 | What we don't know yet | Open checklist, repo link | Stage 2 outstanding. 3 state classes untested. 2 change points unexplained. | Close on the gap, not the claim. Judges trust teams that do. | LIMITATIONS.md |

**Slide 7 discipline:** every number gets the qualifier "against synthetic ground
truth". If a slide can be screenshotted and misread as a combustion result, it is
mislabelled.
