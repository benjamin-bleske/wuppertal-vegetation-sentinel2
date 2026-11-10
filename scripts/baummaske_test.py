"""Welche Satellitengroesse trennt Baeume von Nicht-Baeumen? Referenz = nDOM 2025 (Geobasis NRW, 0,5 m), Gebaeude (OSM) ausgeschlossen.
Je 10-m-Pixel: Baum = >= 60 % der 0,5-m-Zellen hoeher als 3 m; Nicht-Baum = <= 5 %; Gebaeudeanteil < 10 %.
Merkmale aus den elf Sommer-Mosaiken 2015-2025. Ausgabe: out/report/baummaske_test.{png,json}"""
import json, glob, re, numpy as np, geopandas as gpd, rasterio
from rasterio.features import rasterize
from rasterio.windows import Window
from scipy.stats import rankdata
from scipy.optimize import minimize
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

X0, Y1 = 354000, 5688000
years = list(range(2015, 2026))
comp = {}
for y in years:
    with rasterio.open(f"data/composite_{y}.tif") as s: comp[y] = s.read().astype("float32")
def evi(a): B, N, R = a[0], a[3], a[2]; return 2.5 * (N - R) / (N + 6 * R - 7.5 * B + 1)
def ndvi(a): N, R = a[3], a[2]; return (N - R) / (N + R + 1e-6)
valid = np.all([c[0] > -1 for c in comp.values()], axis=0)
E = np.stack([np.where(valid, evi(comp[y]), np.nan) for y in years])         # (11, H, W)
feat = {"EVI 2025": E[-1], "EVI Mittel 11 Jahre": E.mean(0), "EVI Minimum 11 Jahre": E.min(0),
        "EVI 25%-Quantil": np.quantile(E, .25, axis=0), "EVI Schwankung (Std) 11 Jahre": E.std(0),
        "NDVI 2025": np.where(valid, ndvi(comp[2025]), np.nan), "NIR 2025": np.where(valid, comp[2025][3], np.nan),
        "Feuchteindex NDMI 2025": np.where(valid, (comp[2025][3] - comp[2025][4]) / (comp[2025][3] + comp[2025][4] + 1e-6), np.nan)}
# OSM-Acker/Wiese als schwierige Gegenklasse (15 m Randabstand), siehe schwelle_osm.py
import requests
from shapely.geometry import shape, Polygon
from shapely.ops import unary_union
bb = gpd.read_file("data/wuppertal_boundary.geojson").total_bounds
qq = f'[out:json][timeout:120];(way["landuse"~"^(farmland|meadow)$"]({bb[1]},{bb[0]},{bb[3]},{bb[2]}););out geom;'
import time
for _k in range(5):
    rr = requests.post("https://overpass-api.de/api/interpreter", data={"data": qq}, timeout=180, headers={"User-Agent": "wuppertal-vegetation-sentinel2/1.0 (baummaske)"})
    if rr.status_code == 200: break
    time.sleep(20 * (_k + 1))
rr.raise_for_status()
fw = gpd.GeoDataFrame({"geometry": [Polygon([(p["lon"], p["lat"]) for p in e["geometry"]]).buffer(0) for e in rr.json()["elements"] if len(e.get("geometry", [])) > 3]}, crs=4326).to_crs(25832)
fw["geometry"] = fw.geometry.buffer(-15); fw = fw[~fw.is_empty]
FW = rasterize([(g, 1) for g in fw.geometry], out_shape=E.shape[1:], transform=rasterio.transform.from_origin(X0, Y1, 10, 10), fill=0, dtype="uint8").astype(bool)
bld = gpd.read_file("data/osm_buildings.gpkg").geometry.buffer(2).union_all()
tiles = json.load(open("data/ndom/auswahl.json"))
rows = {k: [] for k in feat}; lab = []; tid = []; fwl = []
for ti, name in enumerate(tiles):
    m = re.match(r"ndom50_32(\d{3})_(\d{4})_", name); e0, n0 = int(m[1]) * 1000, int(m[2]) * 1000
    with rasterio.open("data/ndom/" + name) as s: h = s.read(1)
    tr = rasterio.transform.from_origin(e0, n0 + 1000, 0.5, 0.5)
    bm = rasterize([(bld, 1)], out_shape=h.shape, transform=tr, fill=0, dtype="uint8").astype(bool)
    ok = h > -100
    tree = ((h >= 3) & ~bm & ok).reshape(100, 20, 100, 20).mean((1, 3))
    bf = bm.reshape(100, 20, 100, 20).mean((1, 3)); okf = ok.reshape(100, 20, 100, 20).mean((1, 3))
    r0, c0 = (Y1 - (n0 + 1000)) // 10, (e0 - X0) // 10
    if r0 < 0 or c0 < 0 or r0 + 100 > E.shape[1] or c0 + 100 > E.shape[2]: continue
    L = np.full(tree.shape, -1); L[(tree >= .6) & (bf < .1) & (okf > .95)] = 1; L[(tree <= .05) & (bf < .1) & (okf > .95)] = 0
    for k, a in feat.items(): rows[k].append(a[r0:r0 + 100, c0:c0 + 100].ravel())
    fwl.append(FW[r0:r0 + 100, c0:c0 + 100].ravel()); lab.append(L.ravel()); tid.append(np.full(L.size, ti))
fwl = np.concatenate(fwl); lab = np.concatenate(lab); tid = np.concatenate(tid); D = {k: np.concatenate(v) for k, v in rows.items()}
ok = (lab >= 0) & np.all([np.isfinite(v) for v in D.values()], axis=0)
fwl = fwl[ok]; y = lab[ok]; D = {k: v[ok] for k, v in D.items()}; tid = tid[ok]
print("Pixel:", len(y), "Baum:", int(y.sum()), "Nicht-Baum:", int((1 - y).sum()))

def auc(x, y):                       # Wahrscheinlichkeit, dass ein Baum-Pixel einen hoeheren Wert hat als ein Nicht-Baum-Pixel
    r = rankdata(x); n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
def best(x, y):                      # beste Schwelle nach ausgewogener Genauigkeit
    qs = np.quantile(x, np.linspace(.02, .98, 97)); bs = (0, None, None)
    for t in qs:
        p = x > t; tpr = p[y == 1].mean(); tnr = (~p)[y == 0].mean(); b = (tpr + tnr) / 2
        if b > bs[0]: bs = (b, t, (tpr, tnr))
    return bs
res = {}
for k, x in D.items():
    a = auc(x, y); sign = 1 if a >= .5 else -1; a2 = max(a, 1 - a); b, t, (tpr, tnr) = best(sign * x, y)
    res[k] = {"auc": float(a2), "vorzeichen": sign, "schwelle": float(sign * t), "baum_erkannt": float(tpr), "nichtbaum_korrekt": float(tnr), "bal_acc": float(b)}
    print(f"{k:32s} AUC {a2:.3f}  Baum erkannt {tpr:.0%}  Nicht-Baum korrekt {tnr:.0%}  (Schwelle {sign*t:.3f})")
# Kombination: logistische Regression, Training/Test getrennt nach Kacheln (raeumliche Trennung)
names = list(D); Z = np.stack([(D[k] - D[k].mean()) / D[k].std() for k in names], 1); Z1 = np.c_[Z, np.ones(len(y))]
tr_m = (tid % 2 == 0); te_m = ~tr_m
def nll(w, A, t): z = A @ w; return np.mean(np.logaddexp(0, z) - t * z) + 1e-3 * (w @ w)
w = minimize(nll, np.zeros(Z1.shape[1]), args=(Z1[tr_m], y[tr_m]), method="L-BFGS-B").x
sc = Z1[te_m] @ w; b, t, (tpr, tnr) = best(sc, y[te_m])
res["Kombination (Test auf anderen Kacheln)"] = {"auc": float(auc(sc, y[te_m])), "baum_erkannt": float(tpr), "nichtbaum_korrekt": float(tnr), "bal_acc": float(b), "gewichte": dict(zip(names + ["const"], map(float, w)))}
print(f"{'Kombination (Testkacheln)':32s} AUC {auc(sc, y[te_m]):.3f}  Baum erkannt {tpr:.0%}  Nicht-Baum korrekt {tnr:.0%}")
# Schwieriger Test: Baum gegen Acker/Wiese (OSM) auf den Testkacheln
hm = te_m & ((y == 1) | ((y == 0) & fwl)); yy = y[hm]
print("Baum gegen Acker/Wiese: Baum", int(yy.sum()), "Acker/Wiese", int((1 - yy).sum()))
res["_hart"] = {}
for k in names:
    a = auc(D[k][hm], yy); res["_hart"][k] = float(max(a, 1 - a)); print(f"  hart {k:32s} AUC {max(a, 1 - a):.3f}")
sc2 = Z1[hm] @ w; b2, t2, (tpr2, tnr2) = best(sc2, yy)
res["_hart"]["Kombination"] = {"auc": float(auc(sc2, yy)), "baum_erkannt": float(tpr2), "feld_korrekt": float(tnr2)}
print(f"  hart Kombination AUC {auc(sc2, yy):.3f}  Baum erkannt {tpr2:.0%}  Acker/Wiese korrekt {tnr2:.0%}")
json.dump(res, open("out/report/baummaske_test.json", "w"), indent=1, ensure_ascii=False)
ks = sorted([k for k in res if "auc" in res[k]], key=lambda k: res[k]["auc"])
fig, ax = plt.subplots(1, 2, figsize=(15, 5.5))
ax[0].barh(ks, [res[k]["auc"] for k in ks], color=["#EF6C00" if "Kombi" not in k else "#2E7D32" for k in ks]); ax[0].set_xlim(.5, 1); ax[0].set_xlabel("AUC (0,5 = Zufall, 1 = perfekt)"); ax[0].set_title("Wie gut trennt ein Merkmal Baum von Nicht-Baum?")
for i, k in enumerate(("EVI 2025", "EVI Minimum 11 Jahre", "EVI Schwankung (Std) 11 Jahre")):
    pass
for k, c in (("EVI 2025", "#EF6C00"), ("EVI Minimum 11 Jahre", "#1976D2")):
    for v, ls in ((1, "-"), (0, "--")): ax[1].hist(D[k][y == v], bins=60, range=(-.1, .9), density=True, histtype="step", color=c, ls=ls, lw=2, label=f"{k}: {'Baum' if v else 'Nicht-Baum'}")
ax[1].legend(fontsize=8); ax[1].set_xlabel("EVI"); ax[1].set_title("Verteilung: Baum (durchgezogen) vs. Nicht-Baum (gestrichelt)")
plt.tight_layout(); plt.savefig("out/report/baummaske_test.png", dpi=80)
