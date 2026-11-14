# FLARE-X: 7-Slide Project Demonstration Deck
**NASA Space Apps Challenge 2026** | **Challenge:** Flame in Freefall  
**Official Project Demo Link:** https://github.com/parthcoep-bot/Nasa-Space-app-challenge/blob/main/docs/SLIDE_DECK.md  
**Interactive Web Dashboard:** https://parthcoep-bot.github.io/Nasa-Space-app-challenge/  

> **Compliance Notice:** This slide deck strictly contains exactly 7 slides (including title and introductory slides), fulfilling the mandatory limitation set by the NASA Space Apps Challenge Project Submission Guide.

---

## Slide 1: Title & Introduction (The Fire You Can't Walk Away From)
*Target Awards: Most Inspirational | Best Use of Storytelling*

- **Slide Title:** FLARE-X: Flame Learning, Analysis, Risk & Extinction Explorer
- **Subtitle:** An Interpretable SI-Powered Microgravity Combustion Intelligence & Fire Safety Dashboard for Deep-Space Exploration
- **Team Name:** Team FLARE-X
- **Challenge:** Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data
- **Visual Composition:** High-contrast side-by-side layout. Left: Classic buoyant teardrop flame on Earth ($1\,g$). Right: Spherical, creeping, dim blue microgravity flame ($\mu g$) inside a sealed International Space Station module.
- **Key Message / Quote:**
  > *"On Earth, fire rises. In space, it doesn't. In a sealed spacecraft, there is no window to open, no outside to evacuate to, and a finite supply of suppressant. Terrestrial fire rules do not apply."*
- **Speaker Note (0–15s):**  
  "A fire on Earth is governed by gravity-driven buoyancy. In microgravity, that transport channel vanishes. FLARE-X is an open-science, Super Intelligence dashboard transforming decades of archived NASA microgravity combustion video into measurable, auditable fire safety insights for Moon and Mars missions."

---

## Slide 2: The Core Scientific Problem ($Gr \propto g$)
*Target Awards: Best Use of Science | Galactic Impact*

- **Slide Title:** Why Earth Fire Rules Fail in Space
- **Core Scientific Equations & Paradox:**
  - **Grashof Scaling:** $Gr = \frac{g \beta \Delta T L^3}{\nu^2} \propto g$. When gravity drops from $1\,g$ to $10^{-6}\,g$, buoyant flow ($\approx 30\text{ cm/s}$) completely disappears.
  - **The Low-Velocity Paradox:** Materials can sustain flame spread in low-speed forced ventilation ($0.4\text{--}8\text{ cm/s}$) at oxygen concentrations *below* their terrestrial extinction limits.
  - **The Data Gap:** NASA's peer-reviewed studies (Link et al., *Nature Scientific Reports* 2018) describe near-limit flames qualitatively as *"longer, dimmer, and shifting from yellow to blue"*, but per-frame quantitative metrics were never available.
- **Visual Composition:** Fluid dynamic schematic showing boundary layer thickening, thermal radiation loss, and convective vs. diffusive oxidizer transport across gravity levels ($1\,g$, Lunar $0.166\,g$, Martian $0.38\,g$, Microgravity $10^{-6}\,g$).
- **Speaker Note (15–30s):**  
  "Standard flammability tests like NASA-STD-6001 Test 1 rely on buoyant updrafts. In microgravity, forced ventilation creates thick boundary layers where flames linger unexpectedly. We set out to turn published qualitative observations into precise, frame-by-frame physical measurements."

---

## Slide 3: NASA Data Curation & The Power of Rigorous Rejection
*Target Awards: Best Use of Data | Global Connection*

- **Slide Title:** Curating NASA PSI: Selecting BASS-II with Scientific Discipline
- **Selected Dataset:** NASA Physical Sciences Informatics (PSI) — **BASS-II (Burning and Suppression of Solids – II)** on ISS.
  - **Target:** PMMA solid fuel rods under controlled opposed oxidizer flow.
  - **Ground Truth Built-In:** Camera frames contain a burned-in telemetry overlay (hot-wire anemometer, fan voltage) as flow was stepped down to extinction.
- **Principled Dataset Rejections (Scientific Integrity):**
  - ❌ **FLEX / FLEX-2:** Droplet combustion lacks solid pyrolysis fronts; pooling features creates false equivalences.
  - ❌ **ACME:** Gaseous non-premixed flames lack solid substrate dynamics.
  - ❌ **Saffire:** Flame scale differs by $\approx 15\times$ and uses concurrent flow, confounding opposed-flow physics.
- **Visual Composition:** Dataset curation decision tree showing PSI archives reviewed, leading to BASS-II selection with SHA-256 cryptographic provenance hashing.
- **Speaker Note (30–45s):**  
  "Good data science begins with knowing what not to mix. We reviewed 17 NASA PSI investigations and rejected droplet and gas experiments because pooling them with solid spread flames produces meaningless numbers. BASS-II gives us solid-fuel spread and an independent telemetry ground truth burned right into the video."

---

## Slide 4: Technology Innovation: Surviving the Dim Blue Flame
*Target Awards: Best Use of Technology | Art & Technology*

- **Slide Title:** Why Generic AI Fire Detectors Fail & How FLARE-X Solves It
- **The Fatal Flaw of Off-the-Shelf CV:** Commercial fire detectors filter on red/yellow pixels. As microgravity flames starve of oxygen near extinction, soot formation ceases and the flame turns into a **dim, chemiluminescent blue** sphere. Red-channel filters report *zero flame* exactly where critical near-limit physics occurs!
- **The FLARE-X Solution:**
  1. **Radiance-Proxy Segmentation:** $V = \max(R, G, B)$ with an extreme-value noise gate ($\sigma \sqrt{2 \ln N}$), capturing both soot incandescence and dim blue $CH^*/C_2$ radicals without noise flooding.
  2. **Decoupled Sootiness Index:** Quantifies color shift independently: $\chi = \frac{R - B}{R + B}$.
  3. **Flow-Axis Morphology:** Length, width, and standoff are resolved against the fuel rod flow axis, making measurements invariant to camera rotation.
- **Visual Composition:** Side-by-side detection comparison: (Left) Red-channel mask showing total failure (empty); (Right) FLARE-X radiance mask cleanly capturing the faint blue flame envelope.
- **Speaker Note (45–60s):**  
  "Near extinction, flames turn blue. A standard fire AI looking for red or yellow sees nothing. FLARE-X segments on a soot-independent radiance proxy with an extreme-value noise gate, tracking the flame through its entire life cycle while measuring color as an independent physical variable."

---

## Slide 5: The Interactive Dashboard & Closed-Form Attribution
*Target Awards: Art & Technology | Best Use of Technology*

- **Slide Title:** The FLARE-X Dashboard: Zero-Latency, Zero Black-Box Opacity
- **Interactive Web Platform Architecture:**
  - 100% self-contained single-file application (`index.html`) running entirely in-browser with zero external server dependencies.
  - Live synchronized scrubbers matching raw video, segmentation contours, and morphological curves.
- **Extinction Proximity Index (EPI):**
  $$\text{EPI}(t) = \sum_{k=1}^{5} w_k \cdot \tilde{f}_k(t)$$
  *(Elongation + Standoff + Blueness + Dimness + Area Contraction)*
  - **100% Exact Attribution:** Bounded linear combination of physical features—providing exact per-frame attribution bars without opaque black-box neural networks.
- **Visual Composition:** Interface screenshot displaying the interactive timeline, dual-view frame viewer, live telemetry readings, and dynamic EPI attribution breakdown bars.
- **Speaker Note (60–75s):**  
  "Our dashboard is completely interactive, running locally in any browser. Instead of an uninterpretable deep neural net, our Extinction Proximity Index uses exact closed-form attribution. Mission operators can inspect exactly why the index is rising—whether due to flame lift-off, blueness shift, or elongation."

---

## Slide 6: Falsification Testing & Experimental Validation
*Target Awards: Best Use of Science | Best Use of Data*

- **Slide Title:** Built-In Falsification: Proving Software Integrity Against Telemetry
- **H1 Falsification Test Results:**
  - **Commanded Flow Step Recall:** **1.000 (100% of all transitions detected)**
  - **Mean Absolute Temporal Offset:** **0.125 frames** (sub-frame alignment precision)
  - **Overall Event F1 Score:** **0.889** (detecting ignition, flow shifts, and extinction)
- **Segmentation & Robustness Benchmarks:**
  - Mean IoU: **0.843** | Mean Dice: **0.915**
  - **0 false positives** on empty/post-extinction frames (eliminating Otsu noise artifacts)
  - **Overlay Ablation:** Masking burned-in telemetry prevents a **22.4%** accuracy drop
  - **EPI Monotonicity:** Spearman rank correlation $\rho = -0.989$ ($p < 10^{-5}$)
- **Visual Composition:** Multi-panel validation graph plotting detected change points against the ground-truth staircase flow velocity steps, alongside the IoU distribution curve.
- **Speaker Note (75–90s):**  
  "Science demands falsifiability. We tested our software against the camera's burned-in anemometer telemetry. It achieved 100% recall on commanded flow transitions with an average offset of just one-eighth of a frame, zero false detections after extinction, and verified monotonic response."

---

## Slide 7: Mission Impact: Moon, Mars, Earth & Beyond
*Target Awards: Galactic Impact | Best Mission Concept | Local Impact | Global Connection*

- **Slide Title:** Deep-Space Habitation & Earth Fire Safety Spin-Offs
- **Galactic Impact (Space Exploration):**
  - Informs flammability safety rules for Lunar Gateway, Artemis Moon Basecamp, and crewed Mars transits.
  - Direct analytical bridge to **NASA SoFIE (Solid Fuel Ignition & Extinction)** active experiments on the ISS.
- **Best Mission Concept (Spacecraft Flight Architecture):**
  - Tier-1 edge optical monitoring: real-time flame standoff and blueness drift detection running on low-SWaP flight hardware before smoke alarms trigger.
- **Local Impact & Global Connection (Earth Safety & Education):**
  - **Terrestrial Mine & Subway Safety:** Low-velocity opposed flows accurately model horizontal flame spread in ceiling-constrained subway tunnels, mining shafts, and aircraft cargo compartments.
  - **Global Open STEM Science:** Freely available MIT-licensed tool empowering students and fire engineers worldwide without expensive CFD licenses.
- **Visual Composition:** System architecture connecting Optical Sensors $\to$ Edge FLARE-X $\to$ Habitat ECLSS Suppression, paired with an illustration of underground subway tunnel ventilation safety.
- **Speaker Note (90–105s):**  
  "FLARE-X impacts exploration from the Moon to Mars by transforming how we qualify materials for microgravity. But its physics also protects Earth—in underground subway tunnels and mine shafts where ceiling constraints mimic space combustion. Decades of NASA data, now accessible to protect human lives anywhere."
