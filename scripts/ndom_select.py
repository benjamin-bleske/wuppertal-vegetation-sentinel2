"""Waehlt zufaellig 80 nDOM-Kacheln (Stand 2025) aus, die Wuppertal schneiden, und laedt sie nach data/ndom/.
Quelle: https://www.opengeodata.nrw.de/produkte/geobasis/hm/ndom50_tiff/ndom50_tiff/ (Geobasis NRW, dl-de/zero-2-0)"""
import json, re, os, sys, numpy as np, geopandas as gpd, requests
from shapely.geometry import box
BASE = "https://www.opengeodata.nrw.de/produkte/geobasis/hm/ndom50_tiff/ndom50_tiff/"
idx = requests.get(BASE + "index.json", timeout=60).json()
files = [x for d in idx["datasets"] for x in d["files"]]
bnd = gpd.read_file("data/wuppertal_boundary.geojson").to_crs(25832).union_all()
cand = []
for x in files:
    m = re.match(r"ndom50_32(\d{3})_(\d{4})_1_nw_(\d{4})\.tif", x["name"])
    if m and m[3] == "2025" and box(int(m[1]) * 1000, int(m[2]) * 1000, int(m[1]) * 1000 + 1000, int(m[2]) * 1000 + 1000).intersects(bnd):
        cand.append(x)
print(len(cand), "Kacheln 2025 schneiden Wuppertal")
rng = np.random.default_rng(42)
pick = [cand[i] for i in rng.choice(len(cand), 80, replace=False)]
print("Groesse gesamt MB:", round(sum(int(x["size"]) for x in pick) / 1e6))
os.makedirs("data/ndom", exist_ok=True)
json.dump([x["name"] for x in pick], open("data/ndom/auswahl.json", "w"))
for x in pick:
    p = "data/ndom/" + x["name"]
    if os.path.exists(p) and os.path.getsize(p) == int(x["size"]): continue
    with requests.get(BASE + x["name"], stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(p, "wb") as f:
            for c in r.iter_content(1 << 20): f.write(c)
print("fertig")
