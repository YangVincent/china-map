#!/usr/bin/env python3
"""Resolve the Ili-region (northwest Xinjiang) trip stops from OSM/Nominatim so the
route can be plotted on real coordinates. Multiple candidates printed where a spot is ambiguous."""
import json
import time
import urllib.parse
import urllib.request

PLACES = [
    ("urumqi", "Urumqi, Xinjiang"),
    ("baili_danxia_wenquan", "温泉 百里丹霞"),
    ("anjihai", "安集海大峡谷"),
    ("dushanzi", "独山子大峡谷"),
    ("wenquan", "温泉县 博尔塔拉 新疆"),
    ("sayram", "赛里木湖"),
    ("khorgos", "霍尔果斯口岸"),
    ("yining", "伊宁市"),
    ("huiyuan", "惠远古城 霍城"),
    ("zhaosu", "昭苏县 新疆"),
    ("zhaosu_wetland", "昭苏湿地公园"),
    ("xiata", "夏塔景区 昭苏"),
    ("tekes", "特克斯县 八卦城"),
    ("aheyazi", "阿合牙孜大峡谷"),
    ("kalajun", "喀拉峻草原"),
]


def lookup(q, limit=2):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "jsonv2", "limit": limit})
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
        if not res:
            print(f"{key}: NO RESULT for {q!r}")
        for i, r in enumerate(res):
            lat, lon = round(float(r["lat"]), 4), round(float(r["lon"]), 4)
            if i == 0:
                out[key] = [lat, lon]
            print(f"{key}[{i}]: [{lat}, {lon}]  {r.get('display_name','')[:75]}")
        time.sleep(1.2)
    print("\nJS-ready (first candidate each):")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
