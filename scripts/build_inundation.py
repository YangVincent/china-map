#!/usr/bin/env python3
"""Compute the real Three Gorges inundation footprint at 145m and 175m pool levels.

Method: AWS Terrain Tiles (terrarium encoding) are derived from SRTM, flown Feb 2000 —
BEFORE impoundment (filling began 2003) — so the DEM contains the original valley floor.
We flood-fill from real Yangtze river seeds (Natural Earth centerline) at each level,
constrained to west of the dam, and emit RGBA overlay strips for Leaflet ImageOverlay.

Output: china-map/reservoir-strip-{i}.png + printed bounds JSON.
  blue   = area under water at 145 m (summer flood-season drawdown pool)
  orange = additional area under water at 175 m (winter full pool) — the fluctuation band
"""
import concurrent.futures
import json
import math
import os
import re
import urllib.request

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(HERE, "scripts", "dem_cache")
os.makedirs(CACHE, exist_ok=True)

Z = 11
N = 2 ** Z
TILE = 256
# Corridor bbox: Chongqing to a bit past the dam
X0, X1 = 1628, 1657   # lng ~106.17 .. ~111.36
Y0, Y1 = 833, 852     # lat ~31.73 .. ~28.75
DAM_LNG = 111.02
LEVELS = (145.0, 175.0)

W = (X1 - X0 + 1) * TILE
H = (Y1 - Y0 + 1) * TILE


def fetch_tile(x, y):
    path = os.path.join(CACHE, f"{Z}_{x}_{y}.png")
    if not os.path.exists(path):
        url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{Z}/{x}/{y}.png"
        with urllib.request.urlopen(url, timeout=60) as r:
            data = r.read()
        with open(path, "wb") as f:
            f.write(data)
    return x, y, path


def lnglat_to_px(lng, lat):
    """Global mercator pixel coords -> local array col,row."""
    gx = (lng + 180.0) / 360.0 * N * TILE
    siny = math.sin(math.radians(lat))
    gy = (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi)) * N * TILE
    return gx - X0 * TILE, gy - Y0 * TILE


def tiley_to_lat(y):
    n = math.pi - 2.0 * math.pi * y / N
    return math.degrees(math.atan(math.sinh(n)))


def tilex_to_lng(x):
    return x / N * 360.0 - 180.0


def load_dem():
    jobs = [(x, y) for x in range(X0, X1 + 1) for y in range(Y0, Y1 + 1)]
    print(f"downloading {len(jobs)} tiles at z{Z}...")
    dem = np.zeros((H, W), dtype=np.float32)
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        for x, y, path in ex.map(lambda t: fetch_tile(*t), jobs):
            img = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
            elev = img[:, :, 0] * 256.0 + img[:, :, 1] + img[:, :, 2] / 256.0 - 32768.0
            r0, c0 = (y - Y0) * TILE, (x - X0) * TILE
            dem[r0:r0 + TILE, c0:c0 + TILE] = elev
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{len(jobs)}")
    return dem


def river_seeds():
    with open(os.path.join(HERE, "china-rivers.js")) as f:
        text = f.read().strip()
    text = re.sub(r"^const RIVERS = ", "", text).rstrip(";\n")
    rivers = json.loads(text)
    seeds = []
    for seg in rivers["yangtze"]:
        for lat, lng in seg:
            if 28.8 <= lat <= 31.7 and 106.2 <= lng <= DAM_LNG:
                c, r = lnglat_to_px(lng, lat)
                seeds.append((int(r), int(c)))
    return seeds


def flood(dem, level, seeds, dam_col):
    mask = dem <= level
    mask[:, dam_col:] = False
    filled = np.zeros_like(mask)
    fr_list, fc_list = [], []
    for r, c in seeds:
        # seed a neighborhood so we catch the channel even if the centerline is a pixel off
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                rr, cc = r + dr, c + dc
                if 0 <= rr < H and 0 <= cc < W and mask[rr, cc] and not filled[rr, cc]:
                    filled[rr, cc] = True
                    fr_list.append(rr)
                    fc_list.append(cc)
    fr = np.array(fr_list, dtype=np.int32)
    fc = np.array(fc_list, dtype=np.int32)
    waves = 0
    while fr.size:
        nr = np.concatenate([fr - 1, fr + 1, fr, fr])
        nc = np.concatenate([fc, fc, fc - 1, fc + 1])
        ok = (nr >= 0) & (nr < H) & (nc >= 0) & (nc < W)
        nr, nc = nr[ok], nc[ok]
        cand = mask[nr, nc] & ~filled[nr, nc]
        nr, nc = nr[cand], nc[cand]
        if nr.size:
            flat = nr.astype(np.int64) * W + nc
            uniq = np.unique(flat)
            nr = (uniq // W).astype(np.int32)
            nc = (uniq % W).astype(np.int32)
            filled[nr, nc] = True
        fr, fc = nr, nc
        waves += 1
        if waves % 1000 == 0:
            print(f"  wave {waves}, filled {int(filled.sum())} px")
    return filled


def main():
    dem = load_dem()
    seeds = river_seeds()
    print(f"{len(seeds)} river seed points")
    dam_col = int(lnglat_to_px(DAM_LNG, 30.0)[0])

    fills = {}
    px_edge_m = 40075016.686 * math.cos(math.radians(30.2)) / (N * TILE)
    for level in LEVELS:
        print(f"flood fill at {level} m...")
        fills[level] = flood(dem, level, seeds, dam_col)
        area = fills[level].sum() * px_edge_m ** 2 / 1e6
        print(f"  area under {level} m: ~{area:.0f} km^2 ({int(fills[level].sum())} px)")

    rgba = np.zeros((H, W, 4), dtype=np.uint8)
    band = fills[175.0] & ~fills[145.0]
    rgba[fills[145.0]] = (29, 111, 192, 170)
    rgba[band] = (226, 106, 44, 160)

    strips = 4
    rows_per = (Y1 - Y0 + 1) // strips
    bounds = []
    for i in range(strips):
        ty0 = Y0 + i * rows_per
        ty1 = ty0 + rows_per
        r0, r1 = (ty0 - Y0) * TILE, (ty1 - Y0) * TILE
        img = Image.fromarray(rgba[r0:r1], "RGBA")
        out = os.path.join(HERE, f"reservoir-strip-{i}.png")
        img.save(out, optimize=True)
        b = [[tiley_to_lat(ty1), tilex_to_lng(X0)], [tiley_to_lat(ty0), tilex_to_lng(X1 + 1)]]
        bounds.append([[round(b[0][0], 5), round(b[0][1], 5)], [round(b[1][0], 5), round(b[1][1], 5)]])
        print(f"{out}: {os.path.getsize(out)/1024:.0f} KB")

    print("RESERVOIR_BOUNDS = " + json.dumps(bounds))


if __name__ == "__main__":
    main()
