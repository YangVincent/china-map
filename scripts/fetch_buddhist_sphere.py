#!/usr/bin/env python3
"""Fetch Bhutan's border polygon + the centers of the Tibetan-Buddhist (Vajrayana) world
from OSM/Nominatim, so both can be drawn on real data. Writes china-buddhist.js."""
import json
import os
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(HERE, "china-buddhist.js")

CENTERS = [
    ("thimphu", "Thimphu, Bhutan"),
    ("leh", "Leh, Ladakh, India"),
    ("gangtok", "Gangtok, Sikkim, India"),
    ("dharamshala", "Dharamshala, Himachal Pradesh, India"),
    ("kathmandu", "Kathmandu, Nepal"),
    ("ulaanbaatar", "Ulaanbaatar, Mongolia"),
    ("ulanude", "Ulan-Ude, Buryatia, Russia"),
    ("kyzyl", "Kyzyl, Tuva, Russia"),
    ("elista", "Elista, Kalmykia, Russia"),
    ("labrang", "Xiahe, Gansu, China"),
]


def q(params):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "china-map-learning-project/1.0"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read())


def main():
    out = {"centers": {}}

    # Bhutan border polygon (simplified)
    try:
        res = q({"q": "Bhutan", "format": "jsonv2", "limit": 1,
                 "polygon_geojson": 1, "polygon_threshold": 0.02})
        geo = res[0]["geojson"]
        # take the largest ring (outer boundary), as [lat,lng]
        if geo["type"] == "Polygon":
            ring = geo["coordinates"][0]
        else:  # MultiPolygon — largest
            ring = max((p[0] for p in geo["coordinates"]), key=len)
        out["bhutan"] = [[round(lat, 4), round(lng, 4)] for lng, lat in ring]
        print(f"bhutan: {len(out['bhutan'])} boundary points")
    except Exception as e:
        print("bhutan ERROR", e)
    time.sleep(1.2)

    for key, name in CENTERS:
        try:
            res = q({"q": name, "format": "jsonv2", "limit": 1})
            if res:
                out["centers"][key] = [round(float(res[0]["lat"]), 4), round(float(res[0]["lon"]), 4)]
                print(f"{key}: {out['centers'][key]}")
            else:
                print(f"{key}: NONE")
        except Exception as e:
            print(key, "ERR", e)
        time.sleep(1.2)

    with open(DST, "w") as f:
        f.write("const BUDDHIST = ")
        json.dump(out, f, separators=(",", ":"))
        f.write(";\n")
    print(f"wrote {DST}: {os.path.getsize(DST)/1024:.0f} KB")


if __name__ == "__main__":
    main()
