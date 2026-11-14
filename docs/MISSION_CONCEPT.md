# Forward mission concept — claim level L5

> **L5 — FLARE-X forward concept. Not an observation, not a NASA plan, not
> flight-qualified, not tested for latency or robustness. Nothing on this page has
> been built or flown.**

## The problem it addresses

Microgravity combustion experiments are expensive in the resource that is scarcest on
orbit: crew time and downlink bandwidth. BASS-II tests were shaped by astronaut
availability, sample count and oxidiser supply, and the published analysis notes the
resulting data points were not systematically taken.

A flame-state detector that runs **at the instrument** could make each test worth more,
by telling the ground what happened while it is still possible to change what happens
next.

## Concept

```
camera / radiometer
        ↓
edge processing          Tier 1 only: rule-based, no learned parameters,
        ↓                milliseconds per frame on a low-power board
flame-state detection    ignition · growth · quasi-steady · weakening · extinction
        ↓
onboard analysis         morphology time series + extinction proximity index
        ↓
crew / ground support    "this test point reached quasi-steady at 2.1 cm/s;
        ↓                 the index is rising; the next step down is likely
                          the last one that sustains a flame"
mission database         indexed, provenance-tagged, comparable across tests
```

## Why this is plausible rather than aspirational

The plausibility argument rests on one property: **Tier 1 has no learned parameters.**
Segmentation is thresholding plus morphology; change-point detection is a cost
comparison; state labelling is a handful of inequalities. There is no model to load, no
GPU, no training set to ship, and nothing to drift. That is what makes an edge
deployment conceivable at all — and it is why the decision *not* to ship a neural
network is a design strength here rather than a compromise.

## What it would need before anyone should take it seriously

1. **Stage 2 validation on archived data.** Without it there is no evidence the
   detector works on real imagery.
2. **Latency and robustness characterisation** under automatic gain control, crew hand
   motion, variable lighting and compression artefacts — none of which the current
   validation contains.
3. **Failure-mode analysis.** What does the system do when it is wrong, and how does a
   crew member know? A detector that fails silently is worse than none.
4. **Flight qualification** of any hardware, which is outside this project's scope
   entirely.

## What it explicitly does not do

- It does **not** predict fires.
- It does **not** issue warnings or alarms.
- It does **not** make suppression decisions.
- It does **not** replace crew judgement or ground control.

It is a **measurement and indexing aid for experiments**, which is a far narrower and
far more defensible claim than fire detection.

## The nearest real successor

**SoFIE** (Solid Fuel Ignition and Extinction) has been operating in the ISS Combustion
Integrated Rack since 2022 across five investigations. NASA's stated objectives include
validating 1-g materials-flammability protocols for low-gravity fires. A feature
extractor built and validated on BASS-II is the natural instrument to point at SoFIE
data when it becomes publicly available — which, as of this review, we could not
confirm it is.

That is the honest next step: not a spacecraft, a dataset.
