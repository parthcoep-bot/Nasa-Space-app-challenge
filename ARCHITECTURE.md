# Architecture

## Governing constraint

**The scientific pipeline must run with no language model, no web application and no
network.** Everything else is arranged around that.

Consequence: the analysis package imports only NumPy, SciPy, scikit-image,
scikit-learn, OpenCV and pandas. It does not import FastAPI, any HTTP client, or any
LLM SDK. `python scripts/validate_pipeline.py` exercises the entire chain offline, and
that is the test of whether this constraint is still being honoured.

---

## Layers

```
┌──────────────────────────────────────────────────────────────────┐
│  PRESENTATION   static web interface                             │
│                 reads a JSON payload; contains no science        │
└───────────────────────────┬──────────────────────────────────────┘
                            │  analysis_payload.json
┌───────────────────────────┴──────────────────────────────────────┐
│  SERVICE (optional)   FastAPI                                    │
│                       thin wrapper over analyse_run()            │
│                       removing it changes no result              │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────┴──────────────────────────────────────┐
│  ANALYSIS   analysis/flarex/   ← all of the science lives here   │
│                                                                  │
│   segmentation → morphology → timeseries → extinction            │
│        ↑             ↑            ↑            ↑                 │
│        └─────────────┴────────────┴────────────┘                 │
│                  provenance · uncertainty · physics              │
│                  pipeline (thin orchestrator)                    │
│                  phantom (validation only)                       │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────┴──────────────────────────────────────┐
│  DATA   data/registry/  verified metadata, in version control    │
│         data/raw/       user-supplied NASA files, gitignored     │
│                         + sha256 inventory                       │
└──────────────────────────────────────────────────────────────────┘
```

## Why the orchestrator is thin

`pipeline.analyse_run()` is roughly 150 lines and contains no science. Each module
below it can be imported and used alone. A reviewer who distrusts the orchestrator can
call `segment_flame` and `extract_features` directly and get the same numbers.

This also means the failure surface is small: if the orchestrator is wrong, it is
wrong about plumbing, not about combustion.

## Data flow, with the checkpoint at each stage

| Stage | Input | Output | What is checked |
|---|---|---|---|
| Acquisition | PSI download | sha256 inventory | `acquire_psi.py check` detects drift |
| Background | frame stack | per-pixel 5th percentile | percentile, not mean, so a dwelling flame cannot contaminate it |
| Segmentation | frame + background | bool mask + thresholds | noise gate; overlay exclusion; IoU/Dice when truth exists |
| Morphology | mask + radiance + geometry | 18 features | resolved against the **flow** axis; empty → `None`, not zero |
| Change points | multivariate series | split indices | scored against the commanded flow schedule |
| States | area + change points | labelled segments | rule evidence recorded per segment |
| EPI | five feature series | index + exact attribution | monotonicity vs commanded flow |
| Uncertainty | sweep + scale + timing | budget | unquantifiable biases **named**, not numbered |
| Provenance | all of the above | chained `Measurement` | claim-level violations **raise** |

## The provenance invariant

Enforced in `__post_init__`, not by convention:

```python
if level is ClaimLevel.L1_NASA_FACT and provenance.root_repository is None:
    raise ValueError(...)     # a derived number cannot pose as NASA fact

if status == "OK" and value is None:
    raise ValueError(...)     # use not_verified() instead of inventing a number
```

`assert_no_level_inflation()` additionally rejects any L1 claim whose chain passed
through a FLARE-X method or model node.

## Where an LLM may and may not appear

**May:** explaining an already-computed result in prose, retrieving cited literature,
generating plain-language summaries for the education mode.

**May not:** anywhere in segmentation, feature extraction, change-point detection,
state labelling, index computation, or uncertainty estimation.

The architectural guarantee is the import graph: `analysis/flarex/` has no LLM
dependency, so this cannot regress silently.

## Extension points

| To add | Change |
|---|---|
| A new investigation | Add to `data/registry/investigations.json` with verification status; supply a `DuctGeometry` |
| A droplet-flame module (FLEX) | New feature module — do **not** reuse solid-fuel morphology |
| Multi-sample frames (Saffire-II) | Set `keep_largest_only=False` and extend morphology to per-component output |
| A Tier 2 classifier | `analysis/flarex/models.py`; must beat Tier 1 on labels split **by test** |
| A second camera view | Would let the projection bias in `uncertainty.py` move from named to quantified |

## What is deliberately absent

No database — file-based, hash-pinned, inspectable with `cat`. No container
orchestration — it runs on a laptop. No authentication layer — it holds no user data.
No model registry — no models. No telemetry or analytics.
