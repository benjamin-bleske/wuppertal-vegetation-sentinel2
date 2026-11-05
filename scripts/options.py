"""Drei Optionen, Vegetation/Baeume im Mosaik hervorzuheben (Vorschau fuer ein Jahr).
A: NDVI > 0.65            (Standard, einfach, sättigt bei dichtem Laub)
B: EVI  > 0.45            (weniger Saettigung, korrigiert Dunst/Boden mit Blau)
C: Gehoelz-Naeherung: NDVI > 0.65 und NDMI > 0.25 und lokale NIR-Textur hoch (Baeume statt glatter Wiese)
"""
import sys
import numpy as np, rasterio, geopandas as gpd
from rasterio.features import geometry_mask
from scipy.ndimage import uniform_filter
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

def indices(year):
    with rasterio.open(f"data/composite_{year}.tif") as s:
        a = s.read(); tr, crs = s.transform, s.crs
    b2, b3, b4, b8, b11, n = a
    ok = n >= 2
    eps = 1e-6
    ndvi = (b8 - b4) / (b8 + b4 + eps)
    evi = 2.5 * (b8 - b4) / (b8 + 6 * b4 - 7.5 * b2 + 1 + eps)
    ndmi = (b8 - b11) / (b8 + b11 + eps)
    m = uniform_filter(b8, 3); tex = np.sqrt(np.maximum(uniform_filter(b8 ** 2, 3) - m ** 2, 0))
    return dict(b2=b2, b3=b3, b4=b4, ok=ok, ndvi=ndvi, evi=evi, ndmi=ndmi, tex=tex, tr=tr, crs=crs)

def masks(d, tex_thr=None):
    A = d["ndvi"] > 0.65
    B = d["evi"] > 0.45
    C = (d["ndvi"] > 0.65) & (d["ndmi"] > 0.25) & (d["tex"] > (tex_thr if tex_thr is not None else 0.0))
    return A & d["ok"], B & d["ok"], C & d["ok"]

if __name__ == "__main__":
    year = sys.argv[1]
    d = indices(year)
    city = gpd.read_file("data/wuppertal_boundary.geojson").to_crs(d["crs"])
    inside = geometry_mask(city.geometry, out_shape=d["ndvi"].shape, transform=d["tr"], invert=True)
    d["ok"] &= inside
    tex_thr = np.nanpercentile(d["tex"][inside & d["ok"]], 40)
    A, B, C = masks(d, tex_thr)
    area = inside.sum()
    rgb = np.clip(np.dstack([d["b4"], d["b3"], d["b2"]]) / 0.3, 0, 1)
    rgb[~inside] = 1
    fig, ax = plt.subplots(2, 2, figsize=(16, 13))
    ax[0, 0].imshow(rgb); ax[0, 0].set_title(f"{year} Echtfarben-Mosaik")
    for a, m, t in [(ax[0, 1], A, "A: NDVI > 0.65"), (ax[1, 0], B, "B: EVI > 0.45"), (ax[1, 1], C, "C: NDVI+NDMI+Textur")]:
        img = np.where(inside[..., None], np.where(m[..., None], [0.1, 0.5, 0.15], [0.93, 0.93, 0.9]), 1.0)
        a.imshow(img); a.set_title(f"{t}  –  {100 * m[inside].sum() / area:.1f}% der Stadtfläche")
    for a in ax.flat:
        a.axis("off")
    plt.tight_layout(); plt.savefig(f"out/options_{year}.png", dpi=70)
    print({k: round(100 * m[inside].sum() / area, 1) for k, m in zip("ABC", (A, B, C))}, "tex_thr", tex_thr)
