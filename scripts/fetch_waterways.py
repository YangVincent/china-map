#!/usr/bin/env python3
"""Fetch small-waterway geometry from OpenStreetMap (Overpass) that Natural Earth lacks:
the Chang 昌江 / Rao 饶河 (Jingdezhen's rivers) and the Gan 赣江 delta reach near Nanchang.

Stitches unordered OSM ways into ordered polylines and writes china-waterways.js:
  const WATERWAYS = { chang: [[lat,lng],...], gandelta: [[lat,lng],...] };
"""
import json
import os
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(HERE, "china-waterways.js")
OVERPASS = "https://overpass-api.de/api/interpreter"

QUERIES = {
    # Chang Jiang (Jingdezhen's river) + Rao He continuation to Poyang Lake
    "chang": '[out:json][timeout:60];(way["waterway"="river"]["name"="昌江"](28.7,116.3,29.6,117.6);way["waterway"="river"]["name"="饶河"](28.7,116.2,29.2,117.1););out geom;',
    # Gan main stem through/below Nanchang up to its Poyang Lake delta mouth
    "gandelta": '[out:json][timeout:60];(way["waterway"="river"]["name"="赣江"](28.4,115.6,29.2,116.4););out geom;',
}


def fetch(query):
    req = urllib.request.Request(
        OVERPASS,
        data=("data=" + urllib.parse.quote(query)).encode(),
        headers={
            "User-Agent": "china-map-learning-project/1.0 (personal educational map)",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())


def stitch(ways):
    """Greedy endpoint-matching: chain ways sharing endpoints (within ~100m) into the longest path."""
    segs = [[(round(p["lat"], 5), round(p["lon"], 5)) for p in w.get("geometry", [])] for w in ways]
    segs = [s for s in segs if len(s) >= 2]
    if not segs:
        return []

    def close(a, b):
        return abs(a[0] - b[0]) < 0.002 and abs(a[1] - b[1]) < 0.002

    chain = segs.pop(0)
    changed = True
    while changed and segs:
        changed = False
        for i, s in enumerate(segs):
            if close(chain[-1], s[0]):
                chain += s[1:]
            elif close(chain[-1], s[-1]):
                chain += list(reversed(s))[1:]
            elif close(chain[0], s[-1]):
                chain = s[:-1] + chain
            elif close(chain[0], s[0]):
                chain = list(reversed(s))[:-1] + chain
            else:
                continue
            segs.pop(i)
            changed = True
            break
    return chain


def main():
    out = {}
    for key, q in QUERIES.items():
        data = fetch(q)
        ways = [e for e in data.get("elements", []) if e["type"] == "way"]
        chain = stitch(ways)
        out[key] = [[p[0], p[1]] for p in chain]
        if chain:
            print(f"{key}: {len(ways)} ways -> {len(chain)} pts, "
                  f"ends {chain[0]} .. {chain[-1]}")
        else:
            print(f"{key}: EMPTY ({len(ways)} ways fetched)")

    with open(DST, "w") as f:
        f.write("const WATERWAYS = ")
        json.dump(out, f, separators=(",", ":"))
        f.write(";\n")
    print(f"wrote {DST}: {os.path.getsize(DST)/1024:.0f} KB")


if __name__ == "__main__":
    main()
