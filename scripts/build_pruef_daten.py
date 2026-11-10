"""Erzeugt tools/pruef_tool/daten.js (die 73 Flaechen fuer das Pruef-Tool) aus data/verlust_gross.gpkg und dem vorlaeufigen GeoJSON.
Aufruf: .venv/bin/python scripts/build_pruef_daten.py"""
import json, geopandas as gpd
g = gpd.read_file("data/verlust_gross.gpkg").sort_values("a", ascending=False).reset_index(drop=True)
pr = {f["properties"]["nr"]: f["properties"] for f in json.load(open("out/geojson/baumverlust_ueber_1ha.geojson"))["features"]}
c = g.geometry.centroid.to_crs(4326) if False else gpd.GeoSeries(g.geometry.representative_point(), crs=25832).to_crs(4326)
from shapely import set_precision
g4 = gpd.GeoSeries(g.geometry, crs=25832).to_crs(4326)
def ring4(r): return [[round(x, 6), round(y, 6)] for x, y in r.coords]
def ring(r): return [[round(x, 1), round(y, 1)] for x, y in r.coords]
out = []
for i, row in g.iterrows():
    n = i + 1; geo = row.geometry
    x0, y0, x1, y1 = geo.bounds
    out.append({"nr": n, "ha": round(row.a / 1e4, 1), "pruefung": pr[n]["pruefung"], "lon": round(c[i].x, 6), "lat": round(c[i].y, 6),
                "bbox": [round(v, 1) for v in (x0, y0, x1, y1)], "ringe": [ring(geo.exterior)] + [ring(r) for r in geo.interiors],
                "ringe4326": [ring4(g4[i].exterior)] + [ring4(r) for r in g4[i].interiors]})
open("tools/pruef_tool/daten.js", "w").write("// automatisch erzeugt von scripts/build_pruef_daten.py; Koordinaten EPSG:25832, ringe = Aussenring + Loecher; ringe4326 = WGS84 fuer den Export\nconst FLAECHEN = "
                                              + json.dumps(out, separators=(",", ":")) + ";\n")
print(len(out))
