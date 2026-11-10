"""Pruefblatt: zufaellig gezogene Veraenderungsflaechen neben Sentinel-RGB und amtlichen Luftbildern (WMS NW Hist DOP).
Aufruf: pruefblatt.py [SEED]   Ausgabe: out/report/pruefblatt_aenderung_2015_2025.png"""
import sys, io, requests, numpy as np, geopandas as gpd, rasterio
from rasterio.windows import from_bounds
from PIL import Image
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 7
rng = np.random.default_rng(seed)
d = gpd.read_file("out/geojson/aenderung_2015_2025.geojson").to_crs(25832)
d["a"] = d.area
picks = []
for kl in ("Verlust", "Zuwachs"):
    for lo, hi, n in [(20000, 1e9, 1), (2000, 10000, 2)]:
        c = d[(d.klasse == kl) & (d.a >= lo) & (d.a < hi)]
        picks += [c.iloc[i] for i in rng.choice(len(c), n, replace=False)]

def rgb(year, b):
    with rasterio.open(f"data/composite_{year}.tif") as s:
        w = from_bounds(*b, s.transform); a = s.read([3, 2, 1], window=w, boundless=True, fill_value=-9999).astype("float32")
    a[a < 0] = np.nan
    return np.clip(np.moveaxis(a, 0, -1) / 0.18, 0, 1) ** 0.8

def dop(year, b):
    u = ("https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=nw_hist_dop_%d&STYLES="
         "&CRS=EPSG:25832&BBOX=%f,%f,%f,%f&WIDTH=500&HEIGHT=500&FORMAT=image/jpeg" % ((year,) + tuple(b)))
    r = requests.get(u, timeout=60)
    try:
        im = np.asarray(Image.open(io.BytesIO(r.content)).convert("RGB")) / 255
    except Exception:
        return None
    return None if im.mean() > 0.97 else im        # leere (weisse) Kachel = dort kein Bild dieses Jahrgangs

cols = [("Sentinel-2 Echtfarben 2015", lambda b: rgb(2015, b)), ("Sentinel-2 Echtfarben 2025", lambda b: rgb(2025, b)),
        ("Luftbild 2016 (Geobasis NRW)", lambda b: dop(2016, b)), ("Luftbild 2023 (Geobasis NRW)", lambda b: dop(2023, b))]
fig, ax = plt.subplots(len(picks), 4, figsize=(15, 3.8 * len(picks)))
for r, p in enumerate(picks):
    x0, y0, x1, y1 = p.geometry.bounds
    cx, cy, h = (x0 + x1) / 2, (y0 + y1) / 2, max(x1 - x0, y1 - y0, 250) / 2 + 120
    b = (cx - h, cy - h, cx + h, cy + h)
    col = "#D32F2F" if p.klasse == "Verlust" else "#1976D2"
    for c, (title, fn) in enumerate(cols):
        a = ax[r, c]; im = fn(b)
        if im is None: a.text(.5, .5, "kein Bild", ha="center", va="center", transform=a.transAxes, color="grey")
        else: a.imshow(im, extent=(b[0], b[2], b[1], b[3]), origin="upper")
        geoms = p.geometry.geoms if p.geometry.geom_type == "MultiPolygon" else [p.geometry]
        for g in geoms: a.plot(*g.exterior.xy, color=col, lw=1.6)
        a.set_xlim(b[0], b[2]); a.set_ylim(b[1], b[3]); a.set_xticks([]); a.set_yticks([])
        if r == 0: a.set_title(title, fontsize=10)
    ax[r, 0].set_ylabel(f"{p.klasse}\n{p.a:,.0f} m²\nE {cx:.0f} N {cy:.0f}".replace(",", "."), fontsize=9, color=col)
fig.suptitle(f"Pruefblatt Veraenderung 2015→2025 (Zufallsstichprobe, Seed {seed}); Umriss rot = Verlust, blau = Zuwachs", fontsize=12)
plt.tight_layout(rect=(0, 0, 1, 0.985))
fig.savefig("out/report/pruefblatt_aenderung_2015_2025.png", dpi=70)
print("ok", len(picks))
