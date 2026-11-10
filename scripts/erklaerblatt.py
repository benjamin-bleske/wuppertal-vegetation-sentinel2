"""Bildstrecke fuer Laien: ein Beispielort in sechs Bildern (Satellit, Computer-Ergebnis, Luftbild) -> out/erklaerung/*.png"""
import io, requests, numpy as np, geopandas as gpd, rasterio
from rasterio.windows import from_bounds
from PIL import Image
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

cx, cy, h = 370370, 5683770, 450
b = (cx - h, cy - h, cx + h, cy + h)
def sat(y):
    with rasterio.open(f"data/composite_{y}.tif") as s:
        a = s.read([3, 2, 1], window=from_bounds(*b, s.transform), boundless=True, fill_value=-9999).astype("float32")
    a[a < 0] = np.nan
    return np.clip(np.moveaxis(a, 0, -1) / 0.18, 0, 1) ** 0.8
def dop(y):
    u = ("https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=nw_hist_dop_%d&STYLES="
         "&CRS=EPSG:25832&BBOX=%f,%f,%f,%f&WIDTH=700&HEIGHT=700&FORMAT=image/jpeg" % ((y,) + b))
    return np.asarray(Image.open(io.BytesIO(requests.get(u, timeout=60).content)).convert("RGB")) / 255
ext = (b[0], b[2], b[1], b[3])
chg = gpd.read_file("out/geojson/aenderung_2015_2025.geojson").to_crs(25832)
chg = chg[chg.intersects(gpd.GeoSeries.from_xy([cx], [cy], crs=25832).buffer(h).iloc[0])]
def veg(y):
    v = gpd.read_file(f"out/geojson/vegetation_{y}.geojson").to_crs(25832)
    return v[v.intersects(gpd.GeoSeries.from_xy([cx], [cy], crs=25832).buffer(h).iloc[0])]
def outline(a, color="#D32F2F"):
    for g in chg[chg.klasse == "Verlust"].geometry: 
        for q in (g.geoms if g.geom_type == "MultiPolygon" else [g]): a.plot(*q.exterior.xy, color=color, lw=2)

fig, ax = plt.subplots(2, 3, figsize=(17, 12.5))
T = dict(fontsize=14, fontweight="bold", loc="left", pad=10)
ax[0, 0].imshow(sat(2015), extent=ext); ax[0, 0].set_title("1  Satellitenfoto\n    Sommer 2015", **T)
ax[0, 1].imshow(sat(2025), extent=ext); ax[0, 1].set_title("2  Dieselbe Stelle,\n    Sommer 2025", **T)
for a, y, t in [(ax[0, 2], 2015, "3  Grünkarte des Computers 2015\n    (grün = viele Pflanzen)"), (ax[1, 0], 2025, "4  Grünkarte 2025, rote Linien =\n    'weniger Grün als 2015'")]:
    a.imshow(sat(y), extent=ext, alpha=.55)
    veg(y).plot(ax=a, color="#00C853", alpha=.55, edgecolor="none"); a.set_title(t, **T)
outline(ax[1, 0])
ax[1, 1].imshow(dop(2016), extent=ext); outline(ax[1, 1]); ax[1, 1].set_title("5  Luftbild 2016\n    gleiche rote Linien", **T)
ax[1, 2].imshow(dop(2023), extent=ext); outline(ax[1, 2]); ax[1, 2].set_title("6  Luftbild 2023 (Frühjahr, Bäume kahl)\n    gleiche rote Linien", **T)
from matplotlib.patches import Circle
for a in ax.flat:
    a.add_patch(Circle((cx, cy - 20), 190, fill=False, ec="#FFD600", lw=3, ls="--"))     # gelber Kreis: das Beispielfeld
    a.plot([b[0] + 40, b[0] + 240], [b[1] + 40, b[1] + 40], color="white", lw=5); a.plot([b[0] + 40, b[0] + 240], [b[1] + 40, b[1] + 40], color="black", lw=2)
    a.text(b[0] + 140, b[1] + 62, "200 m", ha="center", fontsize=11, fontweight="bold", color="white", bbox=dict(fc="black", alpha=.55, pad=1.5, lw=0))
for a in ax.flat: a.set_xlabel(""); a.set_ylabel(""); a.set_xlim(b[0], b[2]); a.set_ylim(b[1], b[3]); a.set_xticks([]); a.set_yticks([])
plt.tight_layout(h_pad=3.5); fig.savefig("out/erklaerung/beispiel_acker.png", dpi=80)

# 16 groesste Flaechen: nur Luftbild 2016, grosse Beschriftung, keine Koordinaten
big = gpd.read_file("out/geojson/aenderung_2015_2025.geojson").to_crs(25832)
big = big[big.klasse == "Verlust"]; big = big.assign(a=big.area).sort_values("a", ascending=False).iloc[:16]
fig, ax = plt.subplots(4, 4, figsize=(16, 16.5))
for k, (a, (_, q)) in enumerate(zip(ax.flat, big.iterrows())):
    x0, y0, x1, y1 = q.geometry.bounds; ccx, ccy = (x0 + x1) / 2, (y0 + y1) / 2; hh = max(x1 - x0, y1 - y0) / 2 + 120
    bb = (ccx - hh, ccy - hh, ccx + hh, ccy + hh)
    u = ("https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=nw_hist_dop_2016&STYLES="
         "&CRS=EPSG:25832&BBOX=%f,%f,%f,%f&WIDTH=500&HEIGHT=500&FORMAT=image/jpeg" % bb)
    a.imshow(np.asarray(Image.open(io.BytesIO(requests.get(u, timeout=60).content)).convert("RGB")) / 255, extent=(bb[0], bb[2], bb[1], bb[3]))
    for g in (q.geometry.geoms if q.geometry.geom_type == "MultiPolygon" else [q.geometry]): a.plot(*g.exterior.xy, color="#D32F2F", lw=2.2)
    a.set_xlim(bb[0], bb[2]); a.set_ylim(bb[1], bb[3]); a.set_xticks([]); a.set_yticks([])
    a.set_title(f"Nr. {k+1}: rund {round(q.a, -3):,.0f} m²".replace(",", "."), fontsize=15, fontweight="bold")
plt.tight_layout(h_pad=2); fig.savefig("out/erklaerung/die_16_groessten.png", dpi=70)
