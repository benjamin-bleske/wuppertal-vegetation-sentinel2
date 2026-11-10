"""Schwellen-Test: Anteil der OSM-Wald- bzw. Feld/Wiesen-Pixel mit EVI > Schwelle, je Jahr.
Referenz = OpenStreetMap (c) contributors (ODbL), nur grobe Orientierung. Ausgabe: out/report/schwelle_osm.png + .json"""
import json, requests, numpy as np, geopandas as gpd, rasterio
from rasterio.features import rasterize
from shapely.geometry import shape, box
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

bnd = gpd.read_file("data/wuppertal_boundary.geojson").to_crs(25832)
bb = gpd.GeoSeries([bnd.unary_union], crs=25832).to_crs(4326).total_bounds   # w s e n
q = f"""[out:json][timeout:120];(
 way["landuse"="forest"]({bb[1]},{bb[0]},{bb[3]},{bb[2]});relation["landuse"="forest"]({bb[1]},{bb[0]},{bb[3]},{bb[2]});
 way["natural"="wood"]({bb[1]},{bb[0]},{bb[3]},{bb[2]});relation["natural"="wood"]({bb[1]},{bb[0]},{bb[3]},{bb[2]});
 way["landuse"~"^(farmland|meadow)$"]({bb[1]},{bb[0]},{bb[3]},{bb[2]});relation["landuse"~"^(farmland|meadow)$"]({bb[1]},{bb[0]},{bb[3]},{bb[2]});
);out geom;"""
r = requests.post("https://overpass-api.de/api/interpreter", data={"data": q}, headers={"User-Agent": "wuppertal-vegetation-sentinel2/1.0 (schwellen-test)"}, timeout=180); r.raise_for_status()
els = r.json()["elements"]
def poly(e):
    if e["type"] == "way" and "geometry" in e and len(e["geometry"]) > 3:
        return shape({"type": "Polygon", "coordinates": [[(p["lon"], p["lat"]) for p in e["geometry"]]]}).buffer(0)
    if e["type"] == "relation":
        outs = [[(p["lon"], p["lat"]) for p in m["geometry"]] for m in e.get("members", []) if m.get("role") == "outer" and "geometry" in m and len(m["geometry"]) > 3]
        from shapely.ops import unary_union
        from shapely.geometry import Polygon
        return unary_union([Polygon(o).buffer(0) for o in outs]) if outs else None
rows = []
for e in els:
    t = e.get("tags", {}); g = poly(e)
    if g is None or g.is_empty: continue
    rows.append({"klasse": "Wald" if (t.get("landuse") == "forest" or t.get("natural") == "wood") else "Feld/Wiese", "geometry": g})
g = gpd.GeoDataFrame(rows, crs=4326).to_crs(25832)
g = g[g.intersects(bnd.unary_union)]
g["geometry"] = g.geometry.buffer(-15)          # Rand weglassen (Mischpixel), 15 m nach innen
g = g[~g.is_empty]
print("Flaechen:", g.klasse.value_counts().to_dict())

years = list(range(2015, 2026)); thr = np.round(np.arange(0.40, 0.81, 0.05), 2)
res = {}
with rasterio.open("data/composite_2015.tif") as s: tr, shp = s.transform, (s.height, s.width)
def mask(k):
    gg = g[g.klasse == k]
    return rasterize([(x, 1) for x in gg.geometry if not x.is_empty], out_shape=shp, transform=tr, fill=0, dtype="uint8").astype(bool)
inside = rasterize([(bnd.unary_union, 1)], out_shape=shp, transform=tr, fill=0, dtype="uint8").astype(bool)
M = {k: mask(k) & inside for k in ("Wald", "Feld/Wiese")}
overlap = M["Wald"] & M["Feld/Wiese"]; M = {k: v & ~overlap for k, v in M.items()}
print("Pixel:", {k: int(v.sum()) for k, v in M.items()})
for y in years:
    with rasterio.open(f"data/composite_{y}.tif") as s: B, G, R, N = [s.read(i).astype("float32") for i in (1, 2, 3, 4)]
    ok = (B > -1) & (N > -1)
    evi = 2.5 * (N - R) / (N + 6 * R - 7.5 * B + 1)
    res[y] = {k: [float(((evi > t) & m & ok).sum() / (m & ok).sum() * 100) for t in thr] for k, m in M.items()}
json.dump({"schwellen": thr.tolist(), "anteil_prozent": res}, open("out/report/schwelle_osm.json", "w"))
fig, ax = plt.subplots(1, 3, figsize=(17, 5))
for k, c in (("Wald", "#2E7D32"), ("Feld/Wiese", "#EF6C00")):
    arr = np.array([res[y][k] for y in years])
    ax[0].plot(thr, arr.mean(0), color=c, lw=3, label=f"{k} (Mittel 2015-2025)"); ax[0].fill_between(thr, arr.min(0), arr.max(0), color=c, alpha=.2)
ax[0].set_xlabel("EVI-Schwelle"); ax[0].set_ylabel("% der Flächenpixel über der Schwelle"); ax[0].set_title("Wald hält, Feld/Wiese fällt?\n(Band = schlechtestes/bestes Jahr)"); ax[0].legend(); ax[0].grid(alpha=.3)
for i, k in enumerate(("Wald", "Feld/Wiese")):
    for y in years: ax[i + 1].plot(thr, res[y][k], label=str(y), color=plt.cm.viridis((y - 2015) / 10))
    ax[i + 1].set_title(f"{k}: je Jahr"); ax[i + 1].set_xlabel("EVI-Schwelle"); ax[i + 1].grid(alpha=.3)
ax[2].legend(ncol=2, fontsize=8)
plt.tight_layout(); plt.savefig("out/report/schwelle_osm.png", dpi=80)
for t in (0.45, 0.55, 0.6, 0.65, 0.7):
    j = list(thr).index(t); print(t, {k: (round(np.mean([res[y][k][j] for y in years]), 1), round(min(res[y][k][j] for y in years), 1), round(max(res[y][k][j] for y in years), 1)) for k in M})
