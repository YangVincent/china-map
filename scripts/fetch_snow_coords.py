#!/usr/bin/env python3
"""Resolve snow-layer POI coordinates from OSM (Nominatim) instead of memory.
Prints candidates for each named place; 1s delay per Nominatim usage policy."""
import json
import time
import urllib.parse
import urllib.request

PLACES = [
    ("thaiwoo", "太舞滑雪小镇 崇礼"),
    ("songhua", "松花湖滑雪场"),
    ("changbaishan", "万达长白山国际度假区"),
    ("koktokay", "可可托海滑雪场"),
]


def lookup(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "jsonv2", "limit": 3})
    req = urllib.request.Request(url, headers={
        "User-Agent": "china-map-learning-project/1.0 (personal educational map)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main():
    for key, q in PLACES:
        try:
            results = lookup(q)
        except Exception as e:
            print(f"{key}: ERROR {e}")
            time.sleep(1.2)
            continue
        if not results:
            print(f"{key}: NO RESULT for {q!r}")
        for res in results[:2]:
            print(f"{key}: ({float(res['lat']):.4f}, {float(res['lon']):.4f})  "
                  f"[{res.get('type')}] {res.get('display_name', '')[:90]}")
        time.sleep(1.2)


if __name__ == "__main__":
    main()
