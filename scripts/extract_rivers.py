#!/usr/bin/env python3
"""Inspect Natural Earth 10m river centerlines: list named rivers intersecting the China region,
so we can choose which to extract at full fidelity."""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "scripts", "ne_rivers.geojson")

# China-ish bbox (generous, includes Amur/Vladivostok area)
LNG_MIN, LNG_MAX, LAT_MIN, LAT_MAX = 73.0, 136.0, 17.0, 55.0


def coords_of(geom):
    if geom is None:
        return []
    if geom["type"] == "LineString":
        return [geom["coordinates"]]
    if geom["type"] == "MultiLineString":
        return list(geom["coordinates"])
    return []


def in_bbox(segs):
    for seg in segs:
        for lng, lat in seg:
            if LNG_MIN <= lng <= LNG_MAX and LAT_MIN <= lat <= LAT_MAX:
                return True
    return False


def main():
    with open(SRC) as f:
        data = json.load(f)

    seen = {}
    for feat in data["features"]:
        props = feat["properties"]
        segs = coords_of(feat.get("geometry"))
        if not segs or not in_bbox(segs):
            continue
        name = props.get("name_en") or props.get("name") or "?"
        npts = sum(len(s) for s in segs)
        key = name
        if key not in seen:
            seen[key] = {"features": 0, "points": 0, "featurecla": set()}
        seen[key]["features"] += 1
        seen[key]["points"] += npts
        seen[key]["featurecla"].add(props.get("featurecla", "?"))

    for name in sorted(seen):
        s = seen[name]
        print(f"{name!r}\tfeatures={s['features']}\tpoints={s['points']}\t{sorted(s['featurecla'])}")


if __name__ == "__main__":
    main()
