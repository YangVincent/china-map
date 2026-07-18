#!/usr/bin/env python3
"""Convert china_raw.json into china-geo.js (a JS constant) so the page works over file:// without fetch/CORS.

Drops the '100000_JD' pseudo-feature (boundary decoration, not a province).
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(HERE, "china_raw.json")
dst = os.path.join(HERE, "china-geo.js")

with open(src) as f:
    data = json.load(f)

features = [
    feat for feat in data["features"]
    if str(feat["properties"].get("adcode", "")).isdigit()
]
out = {"type": "FeatureCollection", "features": features}

with open(dst, "w") as f:
    f.write("const CHINA_GEOJSON = ")
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")

print(f"wrote {dst}: {len(features)} features, {os.path.getsize(dst)/1024:.0f} KB")
