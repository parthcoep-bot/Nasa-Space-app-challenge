# Quickstart

## Without any NASA data (works immediately)

```bash
pip install -r requirements.txt
python scripts/validate_pipeline.py    # reproduces every number in VALIDATION.md
python -m pytest tests/ -q             # 24 tests
python scripts/build_webapp_payload.py # regenerate the interface data
python scripts/build_webapp.py         # build frontend/index.html
```

## With archived NASA video

```bash
python scripts/acquire_psi.py init --investigation BASS-II
# register at https://psiuserregistration.ndc.nasa.gov/ and download into data/raw/BASS-II
python scripts/acquire_psi.py verify --investigation BASS-II

python scripts/run_analysis.py \
  --investigation BASS-II \
  --video data/raw/BASS-II/<file> \
  --overlay 0,0,760,34 \
  --flow-angle 180 --surface 470,300 --surface-angle 0 \
  --steps my_flow_schedule.csv \
  --oxygen 0.175 --fuel "cast black PMMA rod, 6.4 mm"
```

`--steps` is a CSV of `frame,flow_cm_s` read from the burned-in telemetry overlay or the
test record. **Supplying it is what turns the change-point output from a description
into a scored, falsifiable measurement.** Without it the change points are reported but
not scored, and the tool says so.

Omit `--mm-per-px` until you have recovered the **video** camera's scale from the
in-duct moveable scale. Do not substitute the still camera's documented 34 px/mm — they
are different cameras, and the pipeline deliberately will not do it for you.
