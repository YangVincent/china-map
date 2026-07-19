#!/usr/bin/env python3
"""Source coordinates for the Great Wall's major passes/sections and the Karakoram Highway
from OSM (Nominatim), so both are drawn on real anchor points rather than guessed."""
import json
import time
import urllib.parse
import urllib.request

PLACES = [
    # Great Wall — Han western extension (guarding Dunhuang)
    ("yumenguan", "Yumen Pass, Dunhuang, Gansu"),
    ("yangguan", "Yang Pass, Dunhuang, Gansu"),
    # Ming Great Wall, west to east
    ("jiayuguan", "Jiayuguan Fort, Gansu"),
    ("wuwei", "Wuwei, Gansu"),
    ("shizuishan", "Shizuishan, Ningxia"),
    ("yinchuan", "Yinchuan, Ningxia"),
    ("yulin", "Yulin, Shaanxi"),
    ("yanmenguan", "Yanmen Pass, Shanxi"),
    ("datong", "Datong, Shanxi"),
    ("badaling", "Badaling Great Wall, Beijing"),
    ("mutianyu", "Mutianyu Great Wall, Beijing"),
    ("jinshanling", "Jinshanling Great Wall, Hebei"),
    ("shanhaiguan", "Shanhaiguan, Qinhuangdao, Hebei"),
    ("laolongtou", "Laolongtou Great Wall, Qinhuangdao"),
    # Karakoram Highway
    ("tashkurgan", "Tashkurgan, Xinjiang"),
    ("khunjerab", "Khunjerab Pass"),
    ("sost", "Sost, Gilgit-Baltistan, Pakistan"),
    ("gilgit", "Gilgit, Pakistan"),
    ("besham", "Besham, Pakistan"),
    ("abbottabad", "Abbottabad, Pakistan"),
    ("islamabad", "Islamabad, Pakistan"),
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
            print(f"{key}: [{lat}, {lon}]  {res[0].get('display_name','')[:60]}")
        else:
            print(f"{key}: NO RESULT for {q!r}")
        time.sleep(1.2)
    print("\nJS-ready:")
    print(json.dumps(out))


if __name__ == "__main__":
    main()
