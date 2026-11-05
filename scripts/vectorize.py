"""EVI-Vegetationsmaske -> GeoJSON (EPSG:4326) je Jahr + Differenz-Layer.

Aufruf: vectorize.py veg JAHR      -> out/geojson/vegetation_JAHR.geojson
        vectorize.py diff J1 J2    -> out/geojson/aenderung_J1_J2.geojson (nur Verlust/Zuwachs, nur wo beide Jahre gueltig)
Maske: EVI > 0.45, 3x3-Medianfilter gegen Einzelpixel-Rauschen, Flaechen < MIN_PX Pixel entfernt.
"""
import sys, json, os
import numpy as np, rasterio, geopandas as gpd
from rasterio.features import shapes, geometry_mask
from scipy.ndimage import median_filter, label
from shapely.geometry import shape, mapping
from shapely import set_precision

EVI_THR = 0.45
MIN_PX = 4          # 400 m2
os.makedirs("out/geojson", exist_ok=True)

def load(year):
    with rasterio.open(f"data/composite_{year}.tif") as s:
        b2, b3, b4, b8, b11, n = s.read(); tr, crs = s.transform, s.crs
    evi = 2.5 * (b8 - b4) / (b8 + 6 * b4 - 7.5 * b2 + 1 + 1e-6)
    return evi, n >= 2, tr, crs

def city_mask(shape_, tr, crs):
    city = gpd.read_file("data/wuppertal_boundary.geojson").to_crs(crs)
    return geometry_mask(city.geometry, out_shape=shape_, transform=tr, invert=True)

def veg_mask(year):
    evi, ok, tr, crs = load(year)
    inside = city_mask(evi.shape, tr, crs)
    m = median_filter(((evi > EVI_THR) & ok).astype("uint8"), size=3).astype(bool) & inside
    lab, n = label(m)
    sizes = np.bincount(lab.ravel())
    m &= ~np.isin(lab, np.where(sizes < MIN_PX)[0]) | (lab == 0)
    return m, ok & inside, tr, crs

def write(mask, tr, crs, path, props=None, values=None):
    feats = []
    for geom, val in shapes(mask.astype("uint8") if values is None else values, mask=mask, transform=tr):
        g = shape(geom).simplify(5, preserve_topology=True)
        feats.append({"geometry": g, **({"klasse": props[int(val)]} if props else {})})
    gdf = gpd.GeoDataFrame(feats, geometry="geometry", crs=crs).to_crs(4326)
    gdf["geometry"] = set_precision(gdf.geometry.values, 1e-6)
    gdf.to_file(path, driver="GeoJSON", COORDINATE_PRECISION=6)
    print(path, f"{os.path.getsize(path)/1e6:.1f} MB", len(gdf), "Polygone")

if __name__ == "__main__":
    if sys.argv[1] == "veg":
        y = sys.argv[2]; m, ok, tr, crs = veg_mask(y)
        print(y, f"Vegetation {100*m.sum()/ok.sum():.1f}% der gueltigen Stadtflaeche")
        write(m, tr, crs, f"out/geojson/vegetation_{y}.geojson")
    else:
        y1, y2 = sys.argv[2:4]
        m1, ok1, tr, crs = veg_mask(y1); m2, ok2, _, _ = veg_mask(y2)
        valid = ok1 & ok2
        code = np.zeros(m1.shape, "uint8"); code[m1 & ~m2 & valid] = 1; code[~m1 & m2 & valid] = 2
        print(f"{y1}->{y2}: Verlust {code.__eq__(1).sum()*100/1e6:.2f} km2, Zuwachs {code.__eq__(2).sum()*100/1e6:.2f} km2, gueltig {100*valid.sum()/ok1.sum():.1f}%")
        write(code > 0, tr, crs, f"out/geojson/aenderung_{y1}_{y2}.geojson", props={1: "Verlust", 2: "Zuwachs"}, values=code)
