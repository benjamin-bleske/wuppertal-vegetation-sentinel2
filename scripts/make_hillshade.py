"""DGM1 NRW (dl-de/zero-2-0, Land NRW / Geobasis NRW) -> 5 m Mosaik -> multidirektionale Schummerung -> XYZ-PNG-Kacheln z9-14.
Aufruf: .venv/bin/python scripts/make_hillshade.py"""
import math, requests, numpy as np, rasterio, geopandas as gpd, mercantile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from rasterio.enums import Resampling
from rasterio.warp import reproject, calculate_default_transform
from rasterio.features import rasterize
from rasterio.transform import from_origin, from_bounds
from rasterio.windows import from_bounds as wfb
from scipy import ndimage
from PIL import Image

root = Path(__file__).resolve().parent.parent
data, raw = root / "data", root / "data" / "dgm1_raw"
raw.mkdir(parents=True, exist_ok=True)
BASE = "https://www.opengeodata.nrw.de/produkte/geobasis/hm/dgm1_tiff/dgm1_tiff/"
RES = 5.0
city = gpd.read_file(data / "wuppertal_boundary.geojson").to_crs(25832)
minx, miny, maxx, maxy = city.buffer(1000).total_bounds
x0, y0 = math.floor(minx / 1000) * 1000, math.floor(miny / 1000) * 1000
x1, y1 = math.ceil(maxx / 1000) * 1000, math.ceil(maxy / 1000) * 1000

# 1) Kacheln laden und auf 5 m mitteln
import re
listing = requests.get(BASE, timeout=120).text
avail = {tuple(m[:2]): m[2] for m in re.findall(r'name="dgm1_32_(\d+)_(\d+)_1_nw_(\d+)\.tif"', listing)}
def fetch(e, n):
    if (str(e), str(n)) not in avail: return None
    name = f"dgm1_32_{e}_{n}_1_nw_{avail[(str(e), str(n))]}.tif"
    p = raw / name
    if not p.exists():
        r = requests.get(BASE + name, timeout=120)
        if r.status_code != 200: return None
        p.write_bytes(r.content)
    return p
jobs = [(e, n) for e in range(x0 // 1000, x1 // 1000) for n in range(y0 // 1000, y1 // 1000)]
with ThreadPoolExecutor(4) as ex: files = [f for f in ex.map(lambda a: fetch(*a), jobs) if f]
print(len(files), "von", len(jobs), "DGM1-Kacheln")
W, H = int((x1 - x0) / RES), int((y1 - y0) / RES)
dem = np.full((H, W), np.nan, np.float32)
k = int(1000 / RES)
for p in files:
    _, _, e, n = p.stem.split("_")[:4]
    with rasterio.open(p) as s:
        a = s.read(1, masked=True).astype("float32").filled(np.nan)
    f = a.shape[0] // k
    with np.errstate(all='ignore'):
        a = np.nanmean(a.reshape(k, f, k, f).transpose(0, 2, 1, 3).reshape(k, k, -1), axis=2)
    c, r_ = (int(e) * 1000 - x0) // int(RES), (y1 - (int(n) * 1000 + 1000)) // int(RES)
    dem[r_:r_ + k, c:c + k] = a
tr = from_origin(x0, y1, RES, RES)
prof = dict(driver="GTiff", height=H, width=W, count=1, dtype="float32", crs="EPSG:25832", transform=tr, nodata=-9999, compress="deflate", predictor=3)
out = np.where(np.isnan(dem), -9999, dem)
with rasterio.open(data / "dgm_5m.tif", "w", **prof) as d: d.write(out, 1)

# 2) multidirektionale Schummerung (Horn-Gradient, 4 Azimute, gewichtet)
z = np.where(np.isnan(dem), np.nanmean(dem), dem)
dzdx = ndimage.sobel(z, axis=1) / (8 * RES)
dzdy = -ndimage.sobel(z, axis=0) / (8 * RES)
slope = np.arctan(np.hypot(dzdx, dzdy)); aspect = np.arctan2(-dzdy, -dzdx)  # Hangabwaertsrichtung (math.)
alt = math.radians(40)
def hill(az_deg):
    az = math.radians(360 - az_deg + 90)  # Kompass -> mathematisch
    return np.clip(np.cos(slope) * math.sin(alt) + np.sin(slope) * math.cos(alt) * np.cos(az - aspect), 0, 1)
shade = (hill(225) * 0.4 + hill(270) * 0.2 + hill(315) * 0.3 + hill(360) * 0.1)
shade = np.clip((shade - 0.35) / (0.95 - 0.35), 0, 1)  # Kontrast
shade8 = (shade * 255).astype("uint8")
shade8[np.isnan(dem)] = 128
hprof = dict(prof, dtype="uint8", nodata=None, predictor=2)
with rasterio.open(data / "hillshade.tif", "w", **hprof) as d: d.write(shade8, 1)

# 3) Master in Web-Mercator (Z14-Aufloesung), Stadtmaske mit Randausblendung
ZMAX, ZMIN = 14, 9
tiles = {}
cm = city.to_crs(3857)
for zz in range(ZMIN, ZMAX + 1):
    cb4 = city.buffer(300).to_crs(4326).total_bounds
    tiles[zz] = [t for t in mercantile.tiles(*cb4, zz)
                 if cm.intersects(__import__("shapely.geometry", fromlist=["box"]).box(*mercantile.xy_bounds(t))).any()]
res = {}
for zz in range(ZMIN, ZMAX + 1):
    ts = tiles[zz]
    xs, ys = [t.x for t in ts], [t.y for t in ts]
    b0, b1 = mercantile.xy_bounds(mercantile.Tile(min(xs), min(ys), zz)), mercantile.xy_bounds(mercantile.Tile(max(xs), max(ys), zz))
    left, top, right, bottom = b0.left, b0.top, b1.right, b1.bottom
    w, h = (max(xs) - min(xs) + 1) * 256, (max(ys) - min(ys) + 1) * 256
    dtr = from_bounds(left, bottom, right, top, w, h)
    g = np.zeros((h, w), np.float32)
    reproject(shade8.astype("float32"), g, src_transform=tr, src_crs="EPSG:25832", dst_transform=dtr, dst_crs="EPSG:3857", resampling=Resampling.average if zz < 14 else Resampling.bilinear)
    m = rasterize(cm.geometry, (h, w), transform=dtr, fill=0, default_value=1).astype("float32")
    px = (right - left) / w
    d = ndimage.distance_transform_edt(m == 0) * px  # Meter ausserhalb
    alpha = np.where(m == 1, 1.0, np.clip(1 - d / 250.0, 0, 1))
    res[zz] = (g, alpha, min(xs), min(ys))
    for t in ts:
        r0, c0 = (t.y - min(ys)) * 256, (t.x - min(xs)) * 256
        gg, aa = g[r0:r0 + 256, c0:c0 + 256], alpha[r0:r0 + 256, c0:c0 + 256]
        if aa.max() <= 0: continue
        img = np.dstack([gg, (aa * 255)]).clip(0, 255).astype("uint8")
        p = root / "out" / "tiles" / "hillshade" / str(zz) / str(t.x) / f"{t.y}.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(img, "LA").save(p, optimize=True)
    print("z", zz, len(ts), "Kacheln")

# 4) Vorschau
g, a, _, _ = res[12]
comp = (g * a + 245.0 * (1 - a)).clip(0, 255).astype("uint8")
Image.fromarray(comp).save(root / "out" / "hillshade_preview.png", optimize=True)
