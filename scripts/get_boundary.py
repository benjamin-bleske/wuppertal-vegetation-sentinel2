"""Holt die Verwaltungsgrenze der Stadt Wuppertal (OSM, admin_level=6) via Nominatim.
Daten (c) OpenStreetMap contributors, ODbL 1.0 (https://www.openstreetmap.org/copyright)"""
import json, requests, geopandas as gpd
from pathlib import Path
root = Path(__file__).resolve().parent.parent
r = requests.get("https://nominatim.openstreetmap.org/search",
    params={"q": "Wuppertal, Nordrhein-Westfalen, Germany", "format": "jsonv2", "polygon_geojson": 1,
            "featureType": "settlement", "limit": 5},
    headers={"User-Agent": "dt-wuppertal-vegetation-research/1.0 (bleskebenjamin@gmail.com)"}, timeout=60)
r.raise_for_status()
hit = [x for x in r.json() if x["geojson"]["type"] in ("Polygon", "MultiPolygon") and x.get("osm_type") == "relation"]
print([(x["osm_type"], x["osm_id"], x["display_name"], x["category"], x["type"]) for x in r.json()])
h = hit[0]
feat = {"type": "FeatureCollection", "features": [{"type": "Feature",
        "properties": {"name": "Wuppertal", "osm_relation": h["osm_id"], "admin_level": 6,
                       "attribution": "(c) OpenStreetMap contributors, ODbL"},
        "geometry": h["geojson"]}]}
out = root / "data" / "wuppertal_boundary.geojson"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(feat))
g = gpd.read_file(out)
print("Relation", h["osm_id"], "Bounds", g.total_bounds, "Flaeche km2", g.to_crs(25832).area.sum() / 1e6)
