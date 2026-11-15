# FLARE-X

**Flame Learning, Analysis, Risk & Extinction Explorer**

An interpretable analysis layer for archived NASA microgravity combustion imagery.

NASA Space Apps Challenge 2026 — *Flame in Freefall: AI-Powered Fire Safety Insights
from Microgravity Combustion Data*

> 🚀 **Quick Navigation & Submission Deliverables:**
> - 📄 **[Official Submission Package (SUBMISSION.md)](SUBMISSION.md)** — Complete text for the NASA Space Apps submission form, including the **7-Slide Presentation Deck**, **30-Second Timed Pitch**, SI disclosure, and citations.
> - 💻 **[Interactive Live Dashboard (index.html)](index.html)** — Self-contained, zero-dependency, offline-ready microgravity combustion intelligence dashboard.


---

## What this is, stated plainly

FLARE-X is a **NASA-data-driven research prototype**. It reads archived microgravity
combustion video, segments the flame, measures its shape and brightness frame by
frame, detects the moments where the combustion regime changes, and reports an
interpretable indicator of how far the flame's appearance has moved toward the
appearance reported for near-limit flames — with an uncertainty attached to every
number and a provenance chain back to the source file.

**It is not** a NASA product, not NASA-endorsed, not NASA-validated, not a
certification system, and not a fire-risk predictor. It makes no pass/fail
determination against NASA-STD-6001 or any other standard.

## The research question

> In BASS-II opposed-flow flame spread over PMMA rods, the commanded oxidiser flow
> was stepped downward in quasi-steady increments until extinction. **Can a
> per-frame, image-derived morphological feature set recover those imposed steps as
> detectable change points, and does the resulting morphology-versus-flow response
> carry a reproducible, monotone signature of approach to the low-velocity
> extinction limit?**

This is narrower than "how does fire behave in space", and that is the point. It is
a question this data can actually answer, with a built-in falsification test: the
change points FLARE-X detects must line up with the flow steps that are burned into
the video's telemetry overlay and recorded in the test log. If they do not, the
method has failed, and the repository says so.

## The gap being filled

NASA's peer-reviewed BASS-II analysis reports flame-spread rates measured by
tracking the flame leading edge, and describes near-limit morphology
**qualitatively** — the flame becomes longer, more spherical, dimmer, and shifts
from yellow to blue as flow falls toward the limit
(Link et al. 2018, [doi:10.1038/s41598-017-18398-4](https://doi.org/10.1038/s41598-017-18398-4)).

Those qualitative descriptions are correct, published, and not quantified per frame.
FLARE-X contributes **the measurement layer**: an open, reproducible extractor that
turns those descriptions into time series with uncertainty, and a change-point
analysis that ties them to the commanded flow schedule.

We are not claiming to discover the physics. We are claiming to make an existing,
published qualitative observation measurable, auditable and reusable.

## Why a generic flame detector fails here

Almost every off-the-shelf fire detector keys on the red channel or a
fire-coloured hue range. **The near-limit microgravity flame is dim and blue.** A
red-channel detector suppresses the flame precisely where the science is. FLARE-X
segments on a soot-independent radiance proxy, `max(R,G,B)`, and treats colour as a
*separate measured feature* — the sootiness index χ = (R−B)/(R+B) — which quantifies
the published yellow-to-blue transition instead of being defeated by it.

There is a test for this: `tests/test_flarex.py::test_red_channel_only_detector_would_miss_it`.

## The pipeline

```
archived video
   ↓  background estimate, telemetry-overlay masking
segmentation          hysteresis on max(R,G,B), noise-gated   → IoU/Dice scored
   ↓
morphology            area, length, width, aspect, standoff,
                      circularity, leading edge, χ, radiance
   ↓                  resolved against the FLOW axis, not the image axis
change points         multivariate binary segmentation        → scored against
   ↓                                                            the flow schedule
combustion states     ignition / growth / quasi-steady /
                      transition / weakening / extinction
   ↓
extinction proximity  interpretable weighted composite        → monotonicity tested
   ↓                                                            against commanded flow
uncertainty budget    segmentation sweep + quantisation +
                      scale + timing, biases named not hidden
   ↓
provenance            every number chained back to a file hash
```

**The scientific pipeline runs with no language model, no web app and no network.**
That is a design requirement. `python scripts/validate_pipeline.py` exercises the
whole chain offline.

## Quick start

```bash
git clone <this-repo> && cd flare-x
pip install -r requirements.txt

# 1. Verify the pipeline against exact ground truth (no NASA data needed)
python scripts/validate_pipeline.py

# 2. Run the tests
python -m pytest tests/ -q

# 3. Set up a real data acquisition (requires your own free PSI registration)
python scripts/acquire_psi.py init --investigation BASS-II
#    ... download into data/raw/BASS-II ...
python scripts/acquire_psi.py verify --investigation BASS-II
python scripts/run_analysis.py --investigation BASS-II --video <file>
```

## About the data

**FLARE-X ships no NASA data.** The NASA Physical Sciences Informatics repository
requires individual registration; users obtain data under their own account, which
keeps attribution and terms of use intact. `scripts/acquire_psi.py` makes a manual
download reproducible by hashing every file and pinning results to those hashes.

> **Official NASA Challenge Notice & Disclaimer:**  
> *NASA does not endorse any non-U.S. Government entity and is not responsible for information contained on non-U.S. Government websites. For non-U.S. Government websites, participants must comply with any data use parameters of that specific website.*

### NASA Data, Resources & Spinoffs Catalog
FLARE-X is built directly upon the official suite of NASA combustion science data, safety lessons, and technological spinoffs:

1. **[PSI Data Repository: Combustion Science](https://psi.nasa.gov/physci/repo/search?q=combustion):** Physical Sciences Informatics source of experimental microgravity combustion data (BASS, BASS-II, ACME, FLEX, CIR).
2. **[NASA Combustion Science](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/):** Core microgravity combustion physics, droplet burning, and flame spread research at NASA Glenn Research Center.
3. **[NASA ScienceCasts: The Power of Studying Combustion on the ISS](https://www.youtube.com/watch?v=W1oXykoz9zg):** Foundational multimedia review of soot-free spherical diffusion flames and microgravity combustion fundamentals.
4. **[A Researcher’s Guide to International Space Station Combustion Science](https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/):** Comprehensive 50+ page guide detailing ISS flight facilities (Microgravity Science Glovebox, Combustion Integrated Rack) and flight protocols.
5. **[Apollo 1 Safety & Mission Assurance Review](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1):** Lessons learned on pure oxygen fire dynamics, flashover acceleration, and spacecraft interior material selection.
6. **[Apollo 13 Lessons Learned](https://sma.nasa.gov/sma-disciplines/accllp/apollo-13):** Investigation of cryogenic oxygen tank electrical wire insulation ignition during translunar transit.
7. **[25 Years Ago: Fire Aboard Space Station Mir](https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/):** Analysis of the 1997 solid oxygen generator torch fire and the unique hazards of non-buoyant smoke obscuration in microgravity.
8. **[Fireman’s Air Tanks (NASA Spinoff Node 9582)](https://spinoff.nasa.gov/node/9582):** 1970s adaptation of space life-support lightweight composite pressure vessels into municipal firefighter breathing gear.
9. **[Fire Detector (NASA Spinoff Node 9407)](https://spinoff.nasa.gov/node/9407):** Space Shuttle cabin optical sensor discriminating between smoke aerosols and particulate dust; transitioned to mining operations.
10. **[New Technology for the Fire Attire (NASA Spinoff Node 9918)](https://spinoff.nasa.gov/node/9918):** Transfer of spacesuit thermal barriers and flame-resistant PBI textiles to modern firefighter turnout clothing.

Full dataset review, including the investigations we examined and **rejected**, is
in [DATA_SOURCES.md](DATA_SOURCES.md).

## Verification status of the numbers in this repository

| Claim level | Meaning | Example |
|---|---|---|
| **L1** | NASA-documented fact | BASS-II used a Panasonic WV-CP654, 760×480, with a burned-in telemetry overlay |
| **L2** | Peer-reviewed finding | Flame spread sustained at 17% O₂ in µg where 1 g flames could not exist at 18% |
| **L3** | Measured by FLARE-X from archived data | projected flame area at frame *n*, ± budgeted uncertainty |
| **L4** | Derived by FLARE-X | the extinction proximity index |
| **L5** | FLARE-X concept | the forward mission concept in `docs/MISSION_CONCEPT.md` |

The provenance layer **enforces** this: constructing a measurement labelled as NASA
fact without a repository root in its chain raises an exception. See
`analysis/flarex/provenance.py`.

Where a value could not be confirmed, the repository records `NOT_VERIFIED` and the
reason. It is never replaced with a plausible-looking number.

## Alignment with the 10 NASA Space Apps Global Awards

FLARE-X was built to provide direct, verifiable evidence across **all 10 Global Award categories**:

| Award Category | How FLARE-X Aligns | Key Technical Evidence |
|---|---|---|
| **1. Best Use of Science** | Falsifiable hypothesis ($H_1$–$H_4$); change points must match commanded flow. | 24/24 passing unit/physics tests; $Gr \propto g$ scaling. |
| **2. Best Use of Data** | Exhaustive PSI curation; principled rejection of FLEX/ACME/Saffire. | SHA-256 provenance chain; +22.4% overlay ablation proof. |
| **3. Best Use of Technology** | Extreme-value noise-gated radiance proxy; multivariate change detection. | Overcomes dim blue flame failure; sub-frame localization (0.125 fr). |
| **4. Galactic Impact** | Quantifies non-buoyant extinction for Artemis & Mars human habitats. | Bridges to upcoming NASA SoFIE (Solid Fuel Ignition & Extinction). |
| **5. Best Mission Concept** | Level 5 operational spacecraft flight architecture with edge optical diagnostics. | Low-SWaP early warning before smoke alarms trigger (`MISSION_CONCEPT.md`). |
| **6. Most Inspirational** | Addresses the human reality: fire in a sealed spacecraft with no escape. | Primal survival danger transformed into mathematical safety rules. |
| **7. Best Use of Storytelling** | The scientific phenomenon and narrative are one: *"The flame that turns blue"*. | Narrative matches Term 3 sootiness index $\chi = (R-B)/(R+B)$ directly. |
| **8. Global Connection** | International agency alignment (NASA, ESA, JAXA *Kibo*, CSA). | Open MIT code runnable on ordinary student laptops globally without GPUs. |
| **9. Art & Technology** | Combustion emission color palette; live synchronized SVG timeline scrubbers. | Real-time attribution bars and interactive client-side dashboard (`index.html`). |
| **10. Local Impact** | Space low-velocity opposed flows model underground mine/tunnel fires. | Direct transfer to subway tunnel ventilation and terrestrial STEM labs. |

Full award evidence breakdown: [AWARD_ALIGNMENT.md](AWARD_ALIGNMENT.md).

## Documentation

| File | What is in it |
|---|---|
| [DATA_SOURCES.md](DATA_SOURCES.md) | Dataset review, selection argument, what we rejected and why |
| [SCIENTIFIC_METHOD.md](SCIENTIFIC_METHOD.md) | Question → hypotheses → method → interpretation → limitation |
| [VALIDATION.md](VALIDATION.md) | Every metric, how it was obtained, and what it does not cover |
| [MODEL_CARD.md](MODEL_CARD.md) | Every free parameter, intended use, out-of-scope use |
| [LIMITATIONS.md](LIMITATIONS.md) | The honest list, including the ones that hurt |
| [CITATIONS.md](CITATIONS.md) | Real references with verification status per entry |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design |
| [AWARD_ALIGNMENT.md](AWARD_ALIGNMENT.md) | Space Apps global award mapping, with claims to avoid |
| [DEMO_SCRIPT.md](DEMO_SCRIPT.md) | 3-minute judge demo and 90-second video script |

## License

Code: MIT (see [LICENSE](LICENSE)). Documentation: CC BY 4.0.
NASA data is **not** included and remains subject to NASA's terms.
