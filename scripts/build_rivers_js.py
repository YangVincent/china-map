#!/usr/bin/env python3
"""Extract real river geometry from Natural Earth 10m centerlines into china-rivers.js.

Output: const RIVERS = { key: [ [ [lat,lng], ... ], ... ] }  (list of segments per river)
Coordinates rounded to 4 decimals (~11m), plenty for this map.
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "scripts", "ne_rivers.geojson")
DST = os.path.join(HERE, "china-rivers.js")

# key -> (set of NE names, optional bbox filter (lng_min, lng_max, lat_min, lat_max))
TARGETS = {
    "yangtze": ({"Yangtze"}, None),
    "yellow": ({"Huang", "Yellow"}, (95.0, 120.0, 32.0, 42.0)),
    "wei": ({"Wei"}, (103.0, 111.0, 33.0, 36.5)),
    "han": ({"Han"}, (105.5, 115.0, 29.5, 34.5)),
    "huai": ({"Huai"}, None),
    "amur": ({"Amur", "Ergun"}, (115.0, 135.5, 47.0, 54.0)),
    "ussuri": ({"Ussuri", "Wusuli"}, (130.0, 136.0, 43.0, 49.0)),
    "yalu": ({"Yalu"}, None),
    "tumen": ({"Tumen"}, None),
    "pearl": ({"Xi", "Xun", "Hongshui", "Nanpan"}, (102.0, 114.5, 21.5, 26.5)),
    "gan": ({"Gan"}, (113.5, 116.8, 24.5, 29.8)),
    "bei": ({"Bei"}, (112.3, 114.6, 22.6, 25.5)),
    "mekong": ({"Mekong"}, (90.0, 108.0, 20.5, 39.0)),   # Lancang: keep the in-China stretch and a bit beyond
    "yarlung": ({"Brahmaputra", "Dihang"}, (79.0, 98.0, 27.5, 32.0)),
    "brahmaputra": ({"Brahmaputra", "Dihang", "Jamuna"}, (88.0, 98.5, 23.0, 30.5)),
    "nu": ({"Nu", "Salween"}, (91.0, 100.5, 23.0, 33.0)),
}


def coords_of(geom):
    if geom is None:
        return []
    if geom["type"] == "LineString":
        return [geom["coordinates"]]
    if geom["type"] == "MultiLineString":
        return list(geom["coordinates"])
    return []


def main():
    with open(SRC) as f:
        data = json.load(f)

    rivers = {k: [] for k in TARGETS}
    for feat in data["features"]:
        props = feat["properties"]
        name = props.get("name_en") or props.get("name") or ""
        for key, (names, bbox) in TARGETS.items():
            if name not in names:
                continue
            for seg in coords_of(feat.get("geometry")):
                pts = []
                for lng, lat in seg:
                    if bbox:
                        lng_min, lng_max, lat_min, lat_max = bbox
                        if not (lng_min <= lng <= lng_max and lat_min <= lat <= lat_max):
                            # bbox acts as a clip: break segment at exits so we don't jump
                            if len(pts) >= 2:
                                rivers[key].append(pts)
                            pts = []
                            continue
                    pts.append([round(lat, 4), round(lng, 4)])
                if len(pts) >= 2:
                    rivers[key].append(pts)

    with open(DST, "w") as f:
        f.write("const RIVERS = ")
        json.dump(rivers, f, separators=(",", ":"))
        f.write(";\n")

    total = 0
    for key, segs in rivers.items():
        npts = sum(len(s) for s in segs)
        total += npts
        lats = [p[0] for s in segs for p in s]
        lngs = [p[1] for s in segs for p in s]
        if lats:
            print(f"{key}: {len(segs)} segs, {npts} pts, lat {min(lats):.1f}..{max(lats):.1f}, lng {min(lngs):.1f}..{max(lngs):.1f}")
        else:
            print(f"{key}: EMPTY")
    print(f"total pts: {total}, file: {os.path.getsize(DST)/1024:.0f} KB")


if __name__ == "__main__":
    main()
