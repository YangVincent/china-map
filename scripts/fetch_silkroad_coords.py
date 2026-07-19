#!/usr/bin/env python3
"""Resolve the Silk Road's western caravan cities from OSM (Nominatim), so the
extension from Kashgar to the Mediterranean is drawn on real city coordinates,
not guessed. Ancient sites are queried via their modern towns."""
import json
import time
import urllib.parse
import urllib.request

# key: (query, note)
PLACES = [
    ("kashgar", "Kashgar, Xinjiang, China"),
    ("irkeshtam", "Irkeshtam pass China Kyrgyzstan"),
    ("osh", "Osh, Kyrgyzstan"),
    ("khujand", "Khujand, Tajikistan"),
    ("samarkand", "Samarkand, Uzbekistan"),
    ("bukhara", "Bukhara, Uzbekistan"),
    ("merv", "Mary, Turkmenistan"),
    ("nishapur", "Neyshabur, Iran"),
    ("rayy", "Rey, Tehran, Iran"),
    ("hamadan", "Hamadan, Iran"),
    ("ctesiphon", "Salman Pak, Baghdad, Iraq"),
    ("baghdad", "Baghdad, Iraq"),
    ("palmyra", "Tadmur, Syria"),
    ("damascus", "Damascus, Syria"),
    ("antioch", "Antakya, Turkey"),
    ("tyre", "Tyre, Lebanon"),
    ("constantinople", "Istanbul, Turkey"),
    # southern branch to India (Buddhism transmission)
    ("balkh", "Balkh, Afghanistan"),
    ("bamiyan", "Bamyan, Afghanistan"),
    ("taxila", "Taxila, Pakistan"),
]


def lookup(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "jsonv2", "limit": 1})
    req = urllib.request.Request(url, headers={
        "User-Agent": "china-map-learning-project/1.0 (personal educational map)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main():
    out = {}
    for key, q in PLACES:
        try:
            res = lookup(q)
        except Exception as e:
            print(f"{key}: ERROR {e}")
            time.sleep(1.2)
            continue
        if res:
            lat, lon = round(float(res[0]["lat"]), 4), round(float(res[0]["lon"]), 4)
            out[key] = [lat, lon]
            print(f"{key}: [{lat}, {lon}]  {res[0].get('display_name','')[:70]}")
        else:
            print(f"{key}: NO RESULT for {q!r}")
        time.sleep(1.2)
    print("\nJS-ready:")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
