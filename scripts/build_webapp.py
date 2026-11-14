#!/usr/bin/env python3
"""Inline the payload into the template to produce a self-contained page.

The interface is a single HTML file with no external dependency beyond a web
font, so it opens from disk, works offline, and can be archived alongside the
results it displays.
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
tpl = (ROOT / "frontend" / "index.template.html").read_text()
payload = (ROOT / "frontend" / "payload.json").read_text()
# guard against breaking out of the <script type="application/json"> block
payload = payload.replace("</script", "<\\/script").replace("<!--", "<\\!--")
out = ROOT / "frontend" / "index.html"
out.write_text(tpl.replace("__PAYLOAD__", payload))
print(f"Built {out} ({out.stat().st_size/1e6:.2f} MB)")
