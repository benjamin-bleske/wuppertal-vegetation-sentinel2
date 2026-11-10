"""Baumwahrscheinlichkeit je Zeitfenster aus Sentinel-2 (Jahresschwankung, NDVI, NDMI), angelernt an nDOM 2025.
Fenster A = 2015-2019, Fenster B = 2021-2025 (2020 bleibt aussen vor, damit sich die Fenster nicht beruehren).
Modell: logistische Regression, angelernt auf Fenster B gegen die nDOM-Baummaske 2025 (zeitgleich), danach unveraendert auch auf Fenster A angewendet.
Ausgabe: data/baumprob_{A,B}.tif, out/geojson/baum_{A,B}.geojson, out/geojson/baumveraenderung.geojson, out/report/baummaske.json"""
import json, re, sys, numpy as np, geopandas as gpd, rasterio
from rasterio.features import rasterize
from scipy.optimize import minimize
from scipy.ndimage import median_filter, label
sys.path.insert(0, "scripts"); import vectorize as V

X0, Y1 = 354000, 5688000
WIN = {"A": range(2015, 2020), "B": range(2021, 2026)}
comp = {}
for y in range(2015, 2026):
    with rasterio.open(f"data/composite_{y}.tif") as s: comp[y] = s.read().astype("float32"); TR, CRS = s.transform, s.crs
H, W = comp[2015].shape[1:]
def feats(years):
    E, ND, NM = [], [], []
    for y in years:
        a = comp[y]; ok = a[0] > -1
        B, R, N, S = a[0], a[2], a[3], a[4]
        E.append(np.where(ok, 2.5 * (N - R) / (N + 6 * R - 7.5 * B + 1), np.nan))
        ND.append(np.where(ok, (N - R) / (N + R + 1e-6), np.nan)); NM.append(np.where(ok, (N - S) / (N + S + 1e-6), np.nan))
    E, ND, NM = map(np.stack, (E, ND, NM)); n = np.isfinite(E).sum(0)
    F = np.stack([np.nanmin(E, 0), np.nanstd(E, 0), np.nanmean(E, 0), np.nanmean(ND, 0), np.nanmean(NM, 0)])
    F[:, n < 3] = np.nan                                   # mind. 3 gueltige Jahre im Fenster
    return F
names = ["EVI Minimum", "EVI Schwankung", "EVI Mittel", "NDVI Mittel", "NDMI Mittel"]
with np.errstate(all="ignore"): FA, FB = feats(WIN["A"]), feats(WIN["B"])

# --- Referenz: nDOM 2025 (wie baummaske_test.py) ---
bld = gpd.read_file("data/osm_buildings.gpkg").geometry.buffer(2).union_all()
tiles = json.load(open("data/ndom/auswahl.json")); X, L, T = [], [], []
for ti, name in enumerate(tiles):
    m = re.match(r"ndom50_32(\d{3})_(\d{4})_", name); e0, n0 = int(m[1]) * 1000, int(m[2]) * 1000
    with rasterio.open("data/ndom/" + name) as s: h = s.read(1)
    bm = rasterize([(bld, 1)], out_shape=h.shape, transform=rasterio.transform.from_origin(e0, n0 + 1000, .5, .5), fill=0, dtype="uint8").astype(bool)
    ok = h > -100
    tree = ((h >= 3) & ~bm & ok).reshape(100, 20, 100, 20).mean((1, 3)); bf = bm.reshape(100, 20, 100, 20).mean((1, 3)); okf = ok.reshape(100, 20, 100, 20).mean((1, 3))
    r0, c0 = (Y1 - (n0 + 1000)) // 10, (e0 - X0) // 10
    if r0 < 0 or c0 < 0 or r0 + 100 > H or c0 + 100 > W: continue
    lab = np.full(tree.shape, -1); lab[(tree >= .6) & (bf < .1) & (okf > .95)] = 1; lab[(tree <= .05) & (bf < .1) & (okf > .95)] = 0
    X.append(FB[:, r0:r0 + 100, c0:c0 + 100].reshape(5, -1).T); L.append(lab.ravel()); T.append(np.full(lab.size, ti))
X, L, T = np.concatenate(X), np.concatenate(L), np.concatenate(T)
ok = (L >= 0) & np.isfinite(X).all(1); X, y, T = X[ok], L[ok], T[ok]
mu, sd = X.mean(0), X.std(0)
def fit(Xs, ys):
    A = np.c_[(Xs - mu) / sd, np.ones(len(ys))]
    return minimize(lambda w: np.mean(np.logaddexp(0, A @ w) - ys * (A @ w)) + 1e-3 * (w @ w), np.zeros(6), method="L-BFGS-B").x
def prob(Xs, w): return 1 / (1 + np.exp(-(np.c_[(Xs - mu) / sd, np.ones(len(Xs))] @ w)))
def bal(p, ys, t): q = p > t; return ((q[ys == 1]).mean() + (~q)[ys == 0].mean()) / 2
tr_m = T % 2 == 0; w_half = fit(X[tr_m], y[tr_m]); ph = prob(X[~tr_m], w_half)
ths = np.linspace(.2, .8, 61); thr = float(ths[np.argmax([bal(prob(X[tr_m], w_half), y[tr_m], t) for t in ths])])
q = ph > thr; test = {"schwelle": thr, "baum_erkannt": float(q[y[~tr_m] == 1].mean()), "nichtbaum_korrekt": float((~q)[y[~tr_m] == 0].mean())}
print("Testkacheln:", test)
w = fit(X, y); print("Gewichte:", dict(zip(names + ["const"], np.round(w, 2))))

# --- Anwenden auf die ganze Stadt, beide Fenster ---
inside = V.city_mask((H, W), TR, CRS)
def apply(F):
    flat = F.reshape(5, -1).T; okp = np.isfinite(flat).all(1); p = np.full(flat.shape[0], np.nan, "float32"); p[okp] = prob(flat[okp], w)
    return p.reshape(H, W)
P = {"A": apply(FA), "B": apply(FB)}
for k in P:
    with rasterio.open(f"data/baumprob_{k}.tif", "w", driver="GTiff", height=H, width=W, count=1, dtype="float32", crs=CRS, transform=TR, nodata=-1, compress="deflate") as d: d.write(np.nan_to_num(P[k], nan=-1), 1)
# Kalibrierung je Fenster: Fenster A (2015-2019, trockener, weniger Szenen 2015) wuerde sonst systematisch weniger Baum finden.
# Die Schwelle von A wird so gesetzt, dass derselbe Anteil der OSM-Waldpixel erkannt wird wie in B.
import requests, time
from shapely.geometry import Polygon
bb = gpd.read_file("data/wuppertal_boundary.geojson").total_bounds
qq = f'[out:json][timeout:120];(way["landuse"="forest"]({bb[1]},{bb[0]},{bb[3]},{bb[2]});way["natural"="wood"]({bb[1]},{bb[0]},{bb[3]},{bb[2]}););out geom;'
for _k in range(5):
    rr = requests.post("https://overpass-api.de/api/interpreter", data={"data": qq}, timeout=180, headers={"User-Agent": "wuppertal-vegetation-sentinel2/1.0 (kalibrierung)"})
    if rr.status_code == 200: break
    time.sleep(20)
fo = gpd.GeoDataFrame({"geometry": [Polygon([(p["lon"], p["lat"]) for p in e["geometry"]]).buffer(0) for e in rr.json()["elements"] if len(e.get("geometry", [])) > 3]}, crs=4326).to_crs(25832)
fo["geometry"] = fo.geometry.buffer(-15); fo = fo[~fo.is_empty]
FO = rasterize([(g, 1) for g in fo.geometry], out_shape=(H, W), transform=TR, fill=0, dtype="uint8").astype(bool) & inside
fm = FO & np.isfinite(P["A"]) & np.isfinite(P["B"])
recB = float((P["B"][fm] > thr).mean()); thrs = {"B": thr, "A": float(np.quantile(P["A"][fm], 1 - recB))}
print("Kalibrierung: OSM-Wald erkannt in B", round(recB * 100, 1), "%; Schwelle A", round(thrs["A"], 3), "statt", round(thr, 3))
def clean(p, k):
    m = median_filter(((p > thrs[k]) & np.isfinite(p)).astype("uint8"), size=3).astype(bool) & inside
    lab, n = label(m); sz = np.bincount(lab.ravel()); return m & ~np.isin(lab, np.where(sz < V.MIN_PX)[0]) | (m & (lab == 0))
M = {k: clean(P[k], k) for k in P}; valid = np.isfinite(P["A"]) & np.isfinite(P["B"]) & inside
code = np.zeros((H, W), "uint8"); code[M["A"] & ~M["B"] & valid] = 1; code[~M["A"] & M["B"] & valid] = 2
st = {"schwelle": thr, "schwellen_je_fenster": thrs, "osm_wald_erkannt": recB, "test": test, "gewichte": dict(zip(names + ["const"], map(float, w))),
      "baum_A_km2": float((M["A"] & valid).sum() / 1e4), "baum_B_km2": float((M["B"] & valid).sum() / 1e4),
      "verlust_km2": float((code == 1).sum() / 1e4), "zuwachs_km2": float((code == 2).sum() / 1e4), "gueltig_km2": float(valid.sum() / 1e4)}
print(json.dumps(st, indent=1, ensure_ascii=False)); json.dump(st, open("out/report/baummaske.json", "w"), indent=1, ensure_ascii=False)
V.write(M["A"] & valid, TR, CRS, "out/geojson/baum_A_2015_2019.geojson"); V.write(M["B"] & valid, TR, CRS, "out/geojson/baum_B_2021_2025.geojson")
V.write(code > 0, TR, CRS, "out/geojson/baumveraenderung_2015_2019__2021_2025.geojson", props={1: "Verlust", 2: "Zuwachs"}, values=code)
