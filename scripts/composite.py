"""Wolkenfreies Median-Mosaik Sentinel-2 L2A (Planetary Computer) fuer Wuppertal.

Aufruf: composite.py JAHR [START ENDE]   (Standard-Fenster 07-25 .. 09-15)
Ausgabe: data/composite_JAHR.tif  (EPSG:25832, 10 m, Baender: B02 B03 B04 B08 B11 n_obs)
Reflektanz 0..1; pro Pixel Median der wolkenfreien Beobachtungen (SCL 2,4,5,6,7, Maske 2 px aufgeweitet).
"""
import sys, time
import numpy as np, rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from concurrent.futures import ThreadPoolExecutor
from scipy.ndimage import binary_dilation
from pystac_client import Client
import planetary_computer as pc

year = sys.argv[1]
start = sys.argv[2] if len(sys.argv) > 2 else "07-25"
end = sys.argv[3] if len(sys.argv) > 3 else "09-15"
BBOX = [6.98, 51.14, 7.37, 51.36]          # Suchbereich (WGS84), etwas groesser als die Stadt
# Zielgitter EPSG:25832, 10 m: Wuppertal ca. E 357000-379000, N 5666000-5685000 (etwas Puffer)
X0, Y0, X1, Y1 = 354000, 5663000, 382000, 5688000
W, H = (X1 - X0) // 10, (Y1 - Y0) // 10
TR = from_origin(X0, Y1, 10, 10)
BANDS = ["B02", "B03", "B04", "B08", "B11"]

cat = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
items = list(cat.search(collections=["sentinel-2-l2a"], bbox=BBOX,
                        datetime=f"{year}-{start}/{year}-{end}",
                        query={"eo:cloud_cover": {"lt": 80 if year == "2015" else 40}}).items())
print(year, len(items), "Szenen")

def read(item, asset, resampling, tries=4):
    for k in range(tries):
        try:
            href = pc.sign(item.assets[asset].href)          # frische Signatur je Versuch
            with rasterio.open(href) as src:
                with WarpedVRT(src, crs="EPSG:25832", transform=TR, width=W, height=H,
                               resampling=resampling, nodata=0) as vrt:
                    return vrt.read(1)
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(3 * (k + 1))

def process(item):
    try:
        scl = read(item, "SCL", Resampling.nearest)
        if not (scl > 0).any():
            return None
        bl = float(item.properties.get("s2:processing_baseline", "2.12"))
        off = -1000 if bl >= 4.0 else 0
        data = [(read(item, b, Resampling.bilinear).astype("float32") + off) / 10000 for b in BANDS]
        raw0 = read(item, "B04", Resampling.nearest) == 0
        good = np.isin(scl, [2, 4, 5, 6, 7]) & ~raw0      # Klasse 2 (dunkel) gueltig: aeltere Baselines stufen urbane Flaechen so ein
        good = ~binary_dilation(~good & (scl > 0), iterations=2) & good   # Wolkenraender/Schatten puffern
        return item.id, np.stack(data), good
    except Exception as e:
        print("FEHLER", item.id, str(e)[:120])
        return None

with ThreadPoolExecutor(4) as ex:
    res = [r for r in ex.map(process, items) if r is not None]
print(len(res), "Szenen verarbeitet")

stack = np.full((len(BANDS), len(res), H, W), np.nan, "float32")
for k, (_, d, g) in enumerate(res):
    for b in range(len(BANDS)):
        stack[b, k][g] = d[b][g]
n_obs = np.sum(~np.isnan(stack[0]), axis=0).astype("float32")
med = np.nanmedian(stack, axis=1)
med[:, n_obs < 2] = np.nan                                   # mind. 2 klare Beobachtungen
out = np.concatenate([med, n_obs[None]], 0)
out = np.nan_to_num(out, nan=-9999)
with rasterio.open(f"data/composite_{year}.tif", "w", driver="GTiff", height=H, width=W, count=6,
                   dtype="float32", crs="EPSG:25832", transform=TR, nodata=-9999, compress="deflate") as dst:
    dst.write(out)
    dst.descriptions = BANDS + ["n_obs"]
print("n_obs Median", np.median(n_obs[n_obs > 0]), "Anteil <2 Obs:", float((n_obs < 2).mean()))
print("Szenen:", [r[0] for r in res])
