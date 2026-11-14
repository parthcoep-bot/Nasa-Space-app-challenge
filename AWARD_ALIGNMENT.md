# Award alignment

The ten NASA Space Apps Global Awards, with the **official 2025 definitions verified
2026-09** from https://www.spaceappschallenge.org/2025/awards/. Definitions are
re-checked before submission; they can change year to year.

**Not ranked.** No claim of eligibility or of winning. Nothing here is a feature built
to tick a box — each row points at something already in the repository for scientific
reasons. If a category has no honest evidence, the row says so.

Also verified 2026-09: the 2026 hackathon is **14–15 November 2026**; teams are capped
at **6 members** for Global Judging; global judging criteria are scored 1–5 on
**impact, creativity, validity, relevance, presentation**.

---

### 1. Best Use of Science
*"The project that makes the best and most valid use of science and/or the scientific method."*

| | |
|---|---|
| **Feature** | A falsifiable research question with a built-in refutation route: detected change points must coincide with the commanded flow schedule. |
| **Evidence** | SCIENTIFIC_METHOD.md §2 — four hypotheses, each with an explicit falsification condition, plus three hypotheses **dropped** with reasons. |
| **Demo moment** | Showing the two defects the validation harness caught and we fixed — 25 false-positive frames after extinction, and a falsely confident 0 % error bar. |
| **Slide** | 7 |
| **Basis** | Link et al. 2018 (CC BY); the published radiative/transport-limited extinction mechanism. |
| **Judge sees** | `pytest` 24/24, and `NOT_VERIFIED` entries left standing in the registry. |
| **Avoid** | "We discovered how flames behave in space." We measured, with uncertainty, something already published qualitatively. |

### 2. Best Use of Data
*"The project that best makes space data accessible or leverages it for a unique application."*

| | |
|---|---|
| **Feature** | A dataset review that documents **rejections** — FLEX, ACME and Saffire examined and excluded on commensurability grounds — plus per-field verification status. |
| **Evidence** | DATA_SOURCES.md §3; `data/registry/investigations.json`. |
| **Demo moment** | "We did not use FLEX. A droplet flame has no spread front; one feature set over both produces numbers that *look* comparable and aren't." |
| **Slide** | 3 |
| **Basis** | PSI combustion-science listing, verified 2026-09. |
| **Judge sees** | Provenance chain from repository → investigation → test → file sha256 → frame → method → result. |
| **Avoid** | Implying we processed more investigations than one. MVP is BASS-II alone. |

### 3. Best Use of Technology
*"The project that exemplifies the most innovative use of technology."*

| | |
|---|---|
| **Feature** | Segmentation that survives the yellow→blue transition, where a red-channel detector fails; an extreme-value noise gate; exact per-frame EPI attribution. |
| **Evidence** | `test_red_channel_only_detector_would_miss_it`; VALIDATION.md §1. |
| **Demo moment** | Side-by-side: red-channel mask **empty**, radiance-proxy mask **detects the flame**. |
| **Slide** | 6 |
| **Basis** | Published yellow→blue near-limit shift *(L2)*. |
| **Judge sees** | The technology solving a stated scientific problem, not technology for its own sake. |
| **Avoid** | "AI-powered". There is no trained model, and MODEL_CARD.md explains why that is correct. |

### 4. Galactic Impact
*"The project with the most potential to improve life on Earth or in the universe."*

| | |
|---|---|
| **Feature** | An open measurement layer that makes archived microgravity combustion data quantitatively reusable — and points at SoFIE next. |
| **Evidence** | DATA_SOURCES.md §3 on SoFIE; NASA's own stated SoFIE objective of validating 1-g flammability protocols for low-gravity fires. |
| **Demo moment** | Earth → LEO → Moon → Mars: the buoyancy channel weakens or vanishes; Gr ∝ g makes that quantitative. |
| **Slide** | 8, 9 |
| **Basis** | Gr ∝ g; u_b ~ √(gβΔTL); buoyant flow ~30 cm/s in 1 g *(L2)*. |
| **Judge sees** | A tool a combustion group could actually pick up. |
| **Avoid** | **Any** lives-saved figure, risk-reduction percentage, or economic number. We have none and will not invent one. |

### 5. Best Mission Concept
*"The project with the most plausible concept and design."*

| | |
|---|---|
| **Feature** | Camera → edge flame-state detection → onboard analysis → crew/ground decision support → mission database. Labelled **L5 concept** throughout. |
| **Evidence** | `docs/MISSION_CONCEPT.md`; plausibility rests on Tier 1 being rule-based and cheap enough to run at the edge. |
| **Demo moment** | The explicit L5 banner — separating concept from observation *is* the design discipline. |
| **Slide** | 8 |
| **Basis** | SoFIE flight heritage for solid-fuel diagnostics in CIR. |
| **Judge sees** | A concept that names its own TRL honestly. |
| **Avoid** | "NASA could deploy this." Nothing here is flight-qualified, latency-tested or robustness-tested. |

### 6. Most Inspirational
*"The project that captures our hearts."*

| | |
|---|---|
| **Feature** | *"On Earth, fire rises. In space, it doesn't."* — then the physics of why, then a crew that cannot open a window. |
| **Evidence** | Grounded in Gr ∝ g, not in mood. |
| **Demo moment** | 0:00–0:15 — a sealed volume, no evacuation, limited suppressant. |
| **Slide** | 1 |
| **Basis** | Published fire-safety motivation in Link et al. 2018 and Jomaas et al. 2015. |
| **Judge sees** | Emotional stakes that survive a physicist's scrutiny. |
| **Avoid** | Drama beyond the physics. No invented incident, no dramatised casualty. |

### 7. Best Use of Storytelling
*"The project that most creatively communicates the potential of open data through the art of storytelling."*

| | |
|---|---|
| **Feature** | The yellow→blue transition is simultaneously the **narrative image** and the **measured feature** χ. The story and the data are the same object. |
| **Evidence** | DEMO_SCRIPT.md; `sootiness_index` in `segmentation.py`. |
| **Demo moment** | "The flame turning blue is the story — and it's also term three of the index." |
| **Slide** | 2, 6 |
| **Basis** | *(L2)* colour shift inferred as reduced soot production and flame temperature. |
| **Judge sees** | Narrative that is literally the measurement. |
| **Avoid** | Presenting phantom output as real flame footage. Every synthetic figure carries `NOT NASA DATA`. |

### 8. Global Connection
*"The project that best connects people around the world through technology."*

| | |
|---|---|
| **Feature** | MIT code, CC BY docs, no data lock-in, runs offline on a laptop with no GPU, no API key and no account. |
| **Evidence** | `requirements.txt` — eight packages, no deep-learning framework, no cloud SDK. |
| **Demo moment** | `python scripts/validate_pipeline.py` reproducing every published number in seconds. |
| **Slide** | 10 |
| **Basis** | NASA PSI's open-science mandate. |
| **Judge sees** | Genuinely reproducible work. |
| **Avoid** | "Anyone can analyse NASA data with this." PSI requires individual registration — a real barrier we do not paper over. |

### 9. Art & Technology
*"The project that most effectively combines technical and creative skills."*

| | |
|---|---|
| **Feature** | Every visual encodes a measurement: the flow staircase is the protocol; the colour ramp is χ; contour overlays are the actual segmentation masks. |
| **Evidence** | The web interface; the EPI attribution bars are exact contributions, not illustrations. |
| **Demo moment** | Scrubbing the timeline while contour, morphology trace and EPI attribution move together. |
| **Slide** | 5 |
| **Basis** | Palette derived from diffusion-flame emission — soot continuum to chemiluminescence. |
| **Judge sees** | Aesthetics doing informational work. |
| **Avoid** | Decorative flame imagery with no data behind it. |

### 10. Local Impact
*"The project that demonstrates the greatest potential for local impact."*

| | |
|---|---|
| **Feature** | A free, offline, open measurement instrument for combustion and fire-safety teaching — usable in Indian engineering departments and materials-testing labs without licences, GPUs or cloud access. |
| **Evidence** | Dependency list; offline validation path. |
| **Demo moment** | The transferable point: **flammability screening standards are written for 1 g**, and image-based flame measurement transfers directly to terrestrial cone-calorimeter and LOI test footage. |
| **Slide** | 9 |
| **Basis** | NASA-STD-6001 Test 1 is an upward, normal-gravity propagation test *(verified 2026-09)*; NASA's SoFIE objectives explicitly include validating 1-g protocols for low-gravity fires. |
| **Judge sees** | A concrete local use that does not depend on a space programme. |
| **Avoid** | Forcing an ISRO or national-mission connection we cannot evidence. We have no such collaboration and will not imply one. |

---

## Claims to avoid — the master list

Never say, in any medium:

- "NASA certified" / "NASA approved" / "NASA validated" / "NASA endorsed"
- "First ever" / "revolutionary" / "NASA has never done this"
- "Predicts spacecraft fires" / "fire risk probability" / "safety score"
- "X % safer" / "saves N lives" / any economic or environmental figure
- "This material is safe/unsafe"
- "AI-powered flame prediction"
- Any presentation of phantom output as an experimental observation

Say instead: **"NASA-data-driven research prototype"**, **"data-analysis and
decision-support concept"**, **"research prototype — data-derived indicator"**, and
**"under these experimental conditions"**.

## Honest self-assessment against the judging criteria

| Criterion | Where we are strong | Where we are weak |
|---|---|---|
| **Impact** | Reusable instrument; SoFIE-ready | No validated real-data result yet |
| **Creativity** | Blue-flame segmentation; in-frame telemetry as ground truth | The pipeline stages themselves are conventional |
| **Validity** | This is the strongest axis — falsifiable, tested, defects disclosed | Stage 2 outstanding; 3 state classes untested |
| **Relevance** | Direct fit to the challenge and to NASA-STD-6001's 1-g limitation | Single investigation, N = 1 |
| **Presentation** | Provenance and claim levels visible in the interface | Lengths in pixels until the video scale is recovered — less impressive, more honest |
