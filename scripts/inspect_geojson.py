#!/usr/bin/env python3
"""Inspect the downloaded China provinces GeoJSON: list features and rough size stats."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(HERE, "china_raw.json")

with open(path) as f:
    data = json.load(f)

print(f"features: {len(data['features'])}")
for feat in data["features"]:
    props = feat["properties"]
    geom = feat.get("geometry")
    gtype = geom["type"] if geom else "NO GEOM"
    print(f"{props.get('adcode')}\t{props.get('name')!r}\t{gtype}\tcenter={props.get('center')}")
