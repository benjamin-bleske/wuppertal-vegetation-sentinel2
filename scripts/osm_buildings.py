"""Gebaeudegrundrisse Wuppertal aus OpenStreetMap (c) contributors (ODbL) -> data/osm_buildings.gpkg (EPSG:25832).
Dient nur dazu, Gebaeude aus der nDOM-Baummaske auszuschliessen (nDOM enthaelt auch Daecher)."""
import time, requests, numpy as np, geopandas as gpd
from shapely.geometry import Polygon
bnd = gpd.read_file("data/wuppertal_boundary.geojson")
w, s, e, n = bnd.total_bounds
xs, ys = np.linspace(w, e, 4), np.linspace(s, n, 4)      # 3x3 Teilabfragen
rows = []
for i in range(3):
    for j in range(3):
        q = f'[out:json][timeout:180];way["building"]({ys[j]},{xs[i]},{ys[j+1]},{xs[i+1]});out geom;'
        for k in range(4):
            r = requests.post("https://overpass-api.de/api/interpreter", data={"data": q}, timeout=240,
                              headers={"User-Agent": "wuppertal-vegetation-sentinel2/1.0 (gebaeudemaske)"})
            if r.status_code == 200: break
            time.sleep(20 * (k + 1))
        r.raise_for_status()
        for el in r.json()["elements"]:
            g = el.get("geometry") or []
            if len(g) > 3: rows.append({"id": el["id"], "geometry": Polygon([(p["lon"], p["lat"]) for p in g])})
        print(i, j, len(rows), flush=True)
gdf = gpd.GeoDataFrame(rows, crs=4326).drop_duplicates("id").to_crs(25832)
gdf = gdf[gdf.is_valid]
gdf.to_file("data/osm_buildings.gpkg", driver="GPKG"); print("Gebaeude:", len(gdf))
