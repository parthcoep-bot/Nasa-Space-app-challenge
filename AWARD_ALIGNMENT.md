# Award Alignment: The 10 NASA Space Apps Global Awards

This document details how **FLARE-X** aligns with each of the **ten official NASA Space Apps Challenge Global Awards**.

Global judging evaluates all projects across these ten categories. Rather than specializing in only one narrow aspect, FLARE-X was deliberately engineered so that its scientific core, software architecture, user experience, and mission narrative provide strong, verifiable evidence across **all 10 categories**.

---

### 1. Best Use of Science
*"The project that makes the best and most valid use of science and/or the scientific method."*

| | |
|---|---|
| **Feature** | A falsifiable research question with a built-in refutation route: detected change points must coincide with the independently commanded hardware flow schedule. |
| **Evidence** | `SCIENTIFIC_METHOD.md` §2 — four hypotheses ($H_1$ to $H_4$), each with an explicit falsification condition, plus three hypotheses dropped with scientific reasons. |
| **Demo moment** | Showing the two defects the validation harness caught and we fixed: 25 false-positive frames after extinction, and a falsely confident 0% error bar. |
| **Presentation Slide** | Slide 2 ($Gr \propto g$ physics) & Slide 6 (Change-point falsification testing) |
| **Scientific Basis** | Link et al. (Nature Scientific Reports 2018); published radiative/transport-limited extinction mechanisms. |
| **Judge sees** | Automated `pytest` 24/24 passing, and `NOT_VERIFIED` entries left transparently standing in the registry rather than filled with fake numbers. |
| **Avoid** | "We discovered how flames behave in space." We measured, with uncertainty, something already published qualitatively. |

---

### 2. Best Use of Data
*"The project that best makes space data accessible or leverages it for a unique application."*

| | |
|---|---|
| **Feature** | Exhaustive multi-dataset review that documents **rejections** — FLEX, ACME, and Saffire examined and excluded on commensurability grounds — plus cryptographic SHA-256 provenance tracking. |
| **Evidence** | `DATA_SOURCES.md` §3; `data/registry/investigations.json`; `analysis/flarex/provenance.py`. |
| **Demo moment** | "We did not use FLEX. A droplet flame has no spread front; one feature set over both produces numbers that look comparable and aren't." |
| **Presentation Slide** | Slide 3 (NASA Data Curation & PSI Rigor) & Slide 6 (Telemetry Verification) |
| **Scientific Basis** | NASA Physical Sciences Informatics (PSI) Combustion Science repository. |
| **Judge sees** | Complete provenance chain from repository $\to$ investigation $\to$ test $\to$ file sha256 $\to$ frame $\to$ method $\to$ result. Masking the overlay recovers +22.4% segmentation accuracy. |
| **Avoid** | Implying we processed more investigations than one. MVP is BASS-II alone. |

---

### 3. Best Use of Technology
*"The project that exemplifies the most innovative use of technology."*

| | |
|---|---|
| **Feature** | Segmentation that survives the yellow$\to$blue transition where standard red-channel detectors report zero flame; extreme-value noise gating; multivariate change-point detection; exact closed-form EPI attribution. |
| **Evidence** | `test_red_channel_only_detector_would_miss_it`; `VALIDATION.md` §1; `analysis/flarex/segmentation.py`. |
| **Demo moment** | Side-by-side: red-channel mask **empty**, radiance-proxy mask **detects the dim blue flame**. |
| **Presentation Slide** | Slide 4 (Innovation: Surviving Dim Blue Flames) & Slide 5 (SI Dashboard & Exact Attribution) |
| **Scientific Basis** | Published near-limit chemiluminescent shift ($CH^*/C_2$ radicals) in microgravity. |
| **Judge sees** | The technology solving a stated scientific problem, not technology for its own sake. Zero-dependency offline web application running in pure vanilla JS/SVG. |
| **Avoid** | Opaque black-box models. There is no uninterpretable deep neural network, and `MODEL_CARD.md` explains why that is correct. |

---

### 4. Galactic Impact
*"The project with the most potential to improve life on Earth or in the universe."*

| | |
|---|---|
| **Feature** | Quantifying the dangerous low-flow regime where microgravity flames survive at oxygen concentrations *below* terrestrial flammability limits (NASA-STD-6001 Test 1). |
| **Evidence** | `DATA_SOURCES.md` §3 on SoFIE; NASA's stated SoFIE objective of validating 1-g flammability protocols for low-gravity fires. |
| **Demo moment** | Earth $\to$ LEO $\to$ Moon $\to$ Mars: the buoyancy channel ($Gr \propto g$) weakens or vanishes; $u_b \sim \sqrt{g\beta\Delta TL}$ drops from 30 cm/s to near zero. |
| **Presentation Slide** | Slide 2 (Core Physics Paradox) & Slide 7 (Moon, Mars & Deep-Space Habitation) |
| **Scientific Basis** | $Gr \propto g$; boundary layer thickening reducing heat feedback while radiative loss dominates. |
| **Judge sees** | An open measurement tool a combustion group or spacecraft habitat safety board can actually pick up and use for Artemis and Mars missions. |
| **Avoid** | Any invented lives-saved figure, risk-reduction percentage, or economic number. |

---

### 5. Best Mission Concept
*"The project with the most plausible concept and design."*

| | |
|---|---|
| **Feature** | Spacecraft optical sensor $\to$ edge flame-state detection $\to$ onboard analysis $\to$ crew/ground decision support. Labelled **Level 5 Concept** throughout. |
| **Evidence** | `docs/MISSION_CONCEPT.md`; plausibility rests on Tier 1 being rule-based and lightweight enough to run on low-SWaP radiation-tolerant flight computers. |
| **Demo moment** | The explicit L5 banner — separating concept from observation is the core design discipline. |
| **Presentation Slide** | Slide 7 (Forward Mission Architecture: Edge Processor to ECLSS Alert) |
| **Scientific Basis** | SoFIE flight heritage for solid-fuel diagnostics in the CIR aboard ISS. |
| **Judge sees** | A mission concept that names its own Technology Readiness Level (TRL) honestly. |
| **Avoid** | "NASA could deploy this tomorrow." Nothing here is flight-qualified or radiation-hardened yet. |

---

### 6. Most Inspirational
*"The project that captures our hearts."*

| | |
|---|---|
| **Feature** | *"On Earth, fire rises. In space, it doesn't."* — The human reality of deep space: a crew inside a sealed titanium hull with no window to open, no outside to evacuate to, and finite suppressant. |
| **Evidence** | Grounded in the physics of $Gr \propto g$, not melodrama. |
| **Demo moment** | 0:00–0:15 pitch — confronting humanity's most primal survival fear with the clarity of mathematics. |
| **Presentation Slide** | Slide 1 (The Fire You Can't Walk Away From) |
| **Scientific Basis** | Published fire-safety motivation in Link et al. (2018) and Jomaas et al. (2015). |
| **Judge sees** | Emotional and philosophical stakes that survive an aerospace engineer's scrutiny. |
| **Avoid** | Hollywood-style drama. No fictional explosions or dramatized casualties. |

---

### 7. Best Use of Storytelling
*"The project that most creatively communicates the potential of open data through the art of storytelling."*

| | |
|---|---|
| **Feature** | The yellow$\to$blue transition is simultaneously the **narrative image** and the **measured feature** $\chi$. The story and the data are the exact same physical object. |
| **Evidence** | `DEMO_SCRIPT.md`; `sootiness_index` in `analysis/flarex/morphology.py`. |
| **Demo moment** | "The flame turning blue is the story of fire starving in freefall — and it's also term three of the Extinction Proximity Index." |
| **Presentation Slide** | Slide 1 (Narrative Lead) & Slide 4 (Yellow-to-Blue Transition) |
| **Scientific Basis** | Colour shift caused by reduced soot radiation as low flow restricts thermal feedback. |
| **Judge sees** | Narrative that is literally derived from pixel measurements. |
| **Avoid** | Presenting synthetic phantom output as real flame footage without watermarks. Every synthetic frame carries `NOT NASA DATA`. |

---

### 8. Global Connection
*"The project that best connects people around the world through technology."*

| | |
|---|---|
| **Feature** | Bridges international space agency efforts (NASA, ESA, JAXA *Kibo* FLARE experiment, CSA). Democratizes NASA PSI data for universities and students worldwide via an open MIT codebase runnable on basic hardware. |
| **Evidence** | `requirements.txt` — lightweight packages, zero GPU requirements, zero cloud dependencies. |
| **Demo moment** | Running `validate_pipeline.py` or opening `index.html` on any laptop on Earth in seconds with zero cost. |
| **Presentation Slide** | Slide 3 (International Data Access) & Slide 7 (Global Open Science) |
| **Scientific Basis** | NASA PSI's open-science charter and international ISS research partnerships. |
| **Judge sees** | Genuinely accessible, reproducible science that empowers global researchers without commercial paywalls. |
| **Avoid** | "Anyone can download raw NASA PSI data anonymously." PSI requires individual registration — an honest barrier we do not paper over. |

---

### 9. Art & Technology
*"The project that most effectively combines technical and creative skills."*

| | |
|---|---|
| **Feature** | Aesthetic design derived directly from combustion physics: custom palette matching soot incandescence (`#E39B3A`), chemiluminescence (`#6BA4E8`), and dark flow ducts (`#14171C`). Live vector SVG scrubbers and exact attribution graphics. |
| **Evidence** | The interactive dashboard (`index.html`); vector contour overlays; IBM Plex typography. |
| **Demo moment** | Scrubbing the timeline while the flame contour, morphology curve, and attribution bars animate in perfect synchrony. |
| **Presentation Slide** | Slide 4 (Color Separation) & Slide 5 (The Interactive Dashboard) |
| **Scientific Basis** | Spectral emission of diffusion flames: carbon soot continuum to molecular radical bands. |
| **Judge sees** | Aesthetics doing real informational and functional work rather than superficial decoration. |
| **Avoid** | Flashy generative flame art that has no relationship to real physical data. |

---

### 10. Local Impact
*"The project that demonstrates the greatest potential for local impact."*

| | |
|---|---|
| **Feature** | Directly translates spaceflight low-velocity opposed-flow models to Earth safety: underground subway tunnels, mining shafts, high-altitude aircraft cargo compartments, and STEM fire academies. |
| **Evidence** | Low-speed horizontal flame spread in ceiling-constrained terrestrial geometries mirrors microgravity buoyancy suppression. |
| **Demo moment** | Explaining how subway and mining tunnel fires under forced horizontal ventilation exhibit the same boundary-layer flame spread physics as BASS-II. |
| **Presentation Slide** | Slide 7 (Terrestrial Mine & Tunnel Fire Safety) |
| **Scientific Basis** | Terrestrial flammability standards (NASA-STD-6001 Test 1, ASTM E1354) assume 1-g natural convection, misjudging horizontal duct flows. |
| **Judge sees** | Concrete local and civic applications that protect civilian infrastructure on Earth without requiring a space budget. |
| **Avoid** | Forcing an unverified local agency partnership claim. |

---

## Master Checklist of Claims to Avoid

- ❌ "NASA certified" / "NASA approved" / "NASA validated" / "NASA endorsed"
- ❌ "First ever" / "revolutionary" / "NASA has never done this"
- ❌ "Predicts spacecraft fires" / "fire risk probability" / "safety score"
- ❌ "Saves N lives" / any unevidenced economic figure
- ❌ "This material is safe / unsafe"
- ❌ "Black-box AI flame predictor"

Say instead:
- ✅ **"NASA-data-driven research prototype"**
- ✅ **"Data-analysis and decision-support concept"**
- ✅ **"Research prototype — data-derived indicator"**
- ✅ **"Under these experimental conditions"**
