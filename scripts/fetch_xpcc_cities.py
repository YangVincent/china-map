#!/usr/bin/env python3
"""Resolve the XPCC (bingtuan) directly-administered cities from OSM/Nominatim,
so the scattered enclave pattern can be plotted over the XUAR."""
import json
import time
import urllib.parse
import urllib.request

# XPCC cities (division HQ cities the corps administers directly)
PLACES = [
    ("shihezi", "石河子市 新疆"),        # 8th Div — flagship
    ("wujiaqu", "五家渠市 新疆"),        # 6th Div — near Urumqi
    ("aral", "阿拉尔市 新疆"),           # 1st Div — Tarim/south
    ("tumushuk", "图木舒克市 新疆"),      # 3rd Div — Kashgar area
    ("beitun", "北屯市 新疆"),           # 10th Div — Altay/north
    ("tiemenguan", "铁门关市 新疆"),      # 2nd Div — Korla area
    ("shuanghe", "双河市 新疆"),          # 5th Div — Bortala
    ("kekedala", "可克达拉市 新疆"),      # 4th Div — Ili
    ("kunyu", "昆玉市 新疆"),            # 14th Div — Hotan/south
    ("huyanghe", "胡杨河市 新疆"),        # 7th Div — Karamay area
    ("xinxing", "新星市 哈密 新疆"),      # 13th Div — Hami
    # a few regular XUAR prefecture capitals for contrast
    ("urumqi", "乌鲁木齐市"),
    ("kashgar", "喀什市 新疆"),
    ("hotan", "和田市 新疆"),
    ("korla", "库尔勒市 新疆"),
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
            print(f"{key}: [{lat}, {lon}]  {res[0].get('display_name','')[:55]}")
        else:
            print(f"{key}: NO RESULT for {q!r}")
        time.sleep(1.2)
    print("\nJS-ready:")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
