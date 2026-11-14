# Data sources

Review date: **2026-09-19**. Every statement below is marked with how it was
verified. Where a value could not be confirmed it is recorded as `NOT_VERIFIED`
and left that way.

---

## 1. The repository

**NASA Physical Sciences Informatics (PSI)**
- Landing page: https://www.nasa.gov/physical-sciences-informatics-psi/
- Investigations index: https://www.nasa.gov/physical-sciences-informatics-psi/psi-investigations-by-research-area/
- Data access: https://psiuserregistration.ndc.nasa.gov/

*verified 2026-09*: PSI is NASA's open repository for microgravity physical-sciences
data, launched 2014, organised into six disciplines including Combustion Science.
The Data Repository link on NASA's PSI pages resolves to a **user registration
portal**, so access is free but individual.

### Redistribution policy — ours, not NASA's

**FLARE-X bundles no PSI files.** This is a project policy. Users obtain data under
their own registration, which keeps attribution and terms of use intact.
`scripts/acquire_psi.py` makes the manual download reproducible: it writes an
acquisition manifest, hashes every downloaded file, and pins every later result to
those hashes so a result can never silently drift onto different bytes.

---

## 2. Investigations reviewed

Everything in the PSI Combustion Science listing was reviewed. The listing
(*verified 2026-09*) contains: ACME BRE, ACME E-FIELD Flames, ACME S-Flames, BASS,
BASS-II, CFI, DAFT, DAFT-2, FLEX, FLEX-2, SAFFIRE-I, SAFFIRE-II, SAFFIRE-III, SAME,
SAME-R, SLICE, SPICE, and two ground-based studies.

Full machine-readable detail: [`data/registry/investigations.json`](data/registry/investigations.json).

---

## 3. What we rejected, and why

This section exists because a dataset review that only lists what you kept is not a
review. Combining datasets to look impressive is the failure mode being guarded
against here.

### FLEX / FLEX-2 — rejected for the MVP
Droplet combustion. A burning droplet is a spherically symmetric gas-phase problem
with **no solid-phase pyrolysis front and no flame spread**. Its morphology
descriptors (equivalent diameter, circularity) are not physically commensurate with
a solid-fuel spread flame's length, width and standoff. Running one feature set over
both would produce numbers that *look* comparable and are not. FLEX remains central
to microgravity extinction research and is a good target for a future module with a
droplet-specific feature set.

### ACME (BRE / E-FIELD / S-Flames) — rejected for the MVP
Gaseous laminar non-premixed flames. Same commensurability argument as FLEX: no
solid fuel, no spread front.

### Saffire-I / II / III — rejected for the MVP, retained as published context
*verified 2026-09*: Saffire-I and -III burned a 94 cm × 40.6 cm cotton-fiberglass
fabric; Saffire-II examined nine samples of 29 cm × 5 cm including a 1 cm thick flat
PMMA sample; forced airflow was 20–25 cm/s, described as typical of spacecraft
circulation. Conducted aboard an uncrewed Cygnus vehicle after ISS departure.

Rejected because the comparison would not be like-for-like: different hardware,
different imaging chain, **flame scale differing by roughly a factor of 15**, and a
concurrent rather than opposed flow configuration. Pooling Saffire morphology with
BASS-II morphology would be exactly the kind of cross-dataset combination this
review is meant to prevent. Saffire is cited in FLARE-X at claim level L2 as
published context for the scale question.

### SoFIE — not available, most important forward target
*verified 2026-09*: SoFIE is **not listed** in the PSI combustion investigations
index (index page last updated 2023-07-26), although the payload has been operating
on ISS in the Combustion Integrated Rack since 2022 with five investigations (MIST,
SMµRF, NCA, RTDFS, GEL). We could not confirm public PSI availability. That is a
`NOT_VERIFIED`, not a "no data exists" — check PSI directly.

SoFIE matters because NASA's own stated objectives for it include *validating NASA
materials-flammability selection 1-g test protocols for low-gravity fires*
(*verified 2026-09*). A feature extractor built and validated on BASS-II is the
natural instrument to point at SoFIE data when it is released.

---

## 4. Selected dataset: BASS-II

**Burning and Suppression of Solids – II.** PSI Combustion Science, status Complete,
ROSES eligible (*verified 2026-09*).

### Why BASS-II and not anything else

1. **It is a solid-fuel spread flame with an extinction event.** The research
   question needs a pyrolysis front, a measurable standoff, and a flame that goes
   out. FLEX and ACME have none of these.
2. **The protocol is a controlled staircase, not a free-running burn.** The
   commanded flow is stepped downward with a quasi-steady dwell at each level until
   extinction. That makes each transition an *externally imposed, independently
   documented event*, which is what turns change-point detection from a decorative
   exercise into a falsifiable measurement.
3. **The video carries its own ground truth.** The camera's burned-in digital
   overlay displays the hot-wire anemometer reading and fan voltage. The independent
   reference for scoring detected change points is inside the frame.
4. **The near-limit regime is the interesting one and it is visually distinctive.**
   The published yellow→blue, dim, elongated, high-standoff morphology is exactly
   what an image-derived feature set can quantify.
5. **There is a peer-reviewed paper against which derived quantities can be
   cross-checked**, open access under CC BY 4.0.

### Hardware and conditions (all *verified 2026-09*)

| Item | Value | Source |
|---|---|---|
| Platform | ISS, Microgravity Science Glovebox | NASA GRC / NTRS |
| Flow duct | black anodized 76 × 76 mm, 17 cm test section | Link et al. 2018 |
| Flow generation | upstream fan, voltage-controlled, optional inlet restrictors | Link et al. 2018 |
| Flow measurement | omnidirectional spherical hot-wire anemometer | Link et al. 2018 |
| Max flow | up to 53 cm/s | NTRS 20160000593 |
| Video camera | Panasonic WV-CP654 colour, **760 × 480 px** | Link et al. 2018 |
| **Video overlay** | **burned-in: N₂ flow rate, fan voltage, anemometer reading, radiometer signal** | Link et al. 2018 |
| Still camera | Nikon D300, 4320 × 2968 px, **34 px/mm in sample plane** | Link et al. 2018 |
| Radiometer | Oriel 71768 thermopile, CaF₂ window, 0.13–11 µm | Link et al. 2018 |
| **Radiometer calibration** | **NOT CALIBRATED** — a measure of flame dynamics and steadiness only | Link et al. 2018 |
| O₂ control | GN₂ vitiation of the MSG working volume, PSR model calibrated against CSA-CP | NTRS 20210011385 |
| Fuel (opposed-flow) | cast **black** PMMA rods, ⌀ 6.4 / 9.5 / 12.7 mm, L 57.2 mm, hemispherical ends | Link et al. 2018 |
| O₂ range (µg) | 16–21 %, uncertainty **±0.3 %** | Link et al. 2018 |
| Opposed flow range | 0.4–8 cm/s | Link et al. 2018 |
| Ignition | Kanthal A-1 29-gauge hot wire, ~1.1 Ω, 5 V | Link et al. 2018 |

### Deliberately unresolved

| Item | Status | Consequence in FLARE-X |
|---|---|---|
| Video frame rate | `NOT_VERIFIED` | Time axis provisional; a warning is emitted and all rates are flagged |
| **Video** scale (px/mm) | `NOT_VERIFIED` — only the **still** camera's 34 px/mm is documented | All lengths stay in **pixels** until recovered from the in-duct moveable scale. The code does not substitute the still-camera value; they are different cameras. |
| Per-test pressure | `NOT_VERIFIED` | Not used in any derived quantity |
| Dataset-level DOI | `NOT_VERIFIED` — none located | Cite PSI investigation ID + accession date |

### Why other fuels are in the registry but not the MVP

BASS-II also burned SIBAL cotton-fiberglass, acrylic sheets and films, and a solid
sphere section; the BASS series also used Nomex, Ultem and wax-saturated fiberglass.
Material comparison is a supported module, but **only within matched geometry and
flow configuration**. Comparing a thin fabric's concurrent-flow spread against a
thick rod's opposed-flow spread would confound material with geometry and with flow
direction simultaneously. Any material comparison FLARE-X displays is labelled
*"under these experimental conditions"* and names the conditions.

---

## 5. Defensible combination: BASS + BASS-II

BASS and BASS-II share hardware lineage (both modified SPICE hardware in the MSG)
and the same imaging chain. That makes **method transfer** defensible: a feature
extractor calibrated for one applies to the other without recalibration.

It does **not** automatically make *results* poolable. Pooling requires matching
fuel, geometry and flow configuration test by test. FLARE-X supports the former and
requires the user to justify the latter.

---

## 6. Standard referenced

**NASA-STD-6001**, *Flammability, Offgassing, and Compatibility Requirements and Test
Procedures*. Current version **B w/Change 3**, status ACTIVE (*verified 2026-09* from
standards.nasa.gov).

Relevant because Test 1 is an **upward flame propagation screening test conducted in
normal gravity**, and the peer-reviewed microgravity result is that the limiting
oxygen concentration can be *lower* in microgravity than in normal gravity for these
conditions. That is precisely why NASA's own SoFIE objectives include validating 1-g
flammability protocols for low-gravity fires.

**FLARE-X produces no pass/fail determination against this or any standard.**
