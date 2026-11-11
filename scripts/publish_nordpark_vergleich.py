"""Vergleichslayer: Summe der bestaetigten Baumverlust-Flaechen als Flaeche in Form des Nordparks (Wuppertal).
Der Nordpark (OSM way 26435842) wird um seinen Schwerpunkt so vergroessert, dass er so gross ist wie alle bestaetigten Flaechen zusammen.
Das ist eine Veranschaulichung der Groesse, kein Ort des Verlusts.
Aufruf: .venv/bin/python scripts/publish_nordpark_vergleich.py   (benoetigt out/geojson/baumverlust_final.geojson)"""
import json, time, requests, geopandas as gpd
from shapely import affinity, set_precision
from shapely.geometry import Polygon
import sys; sys.path.insert(0, "scripts")
from build_styles import BASE, style

def de(x, n=1): return f"{x:.{n}f}".replace(".", ",")
verl = gpd.read_file("out/geojson/baumverlust_final.geojson").to_crs(25832)
summe_ha = float(verl.geometry.area.sum()) / 1e4
r = None
for _ in range(5):
    r = requests.post("https://overpass-api.de/api/interpreter", data={"data": "[out:json][timeout:60];way(26435842);out geom;"},
                      headers={"User-Agent": "wuppertal-vegetation-sentinel2/1.0"}, timeout=90)
    if r.status_code == 200: break
    time.sleep(5)
r.raise_for_status()
w = r.json()["elements"][0]; assert w["tags"].get("name") == "Nordpark"
park = gpd.GeoSeries([Polygon([(n["lon"], n["lat"]) for n in w["geometry"]])], crs=4326).to_crs(25832).iloc[0]
park_ha = park.area / 1e4; faktor = summe_ha / park_ha
gross = affinity.scale(park, xfact=faktor ** 0.5, yfact=faktor ** 0.5, origin=park.centroid)
rows = [{"Name": f"Fläche aller bestätigten Baumverluste, in Form des Nordparks vergrößert", "Fläche (ha)": round(summe_ha, 1),
         "Vergleich": f"{de(faktor)} mal so groß wie der Nordpark", "geometry": gross},
        {"Name": "Nordpark (tatsächliche Größe)", "Fläche (ha)": round(park_ha, 1), "Vergleich": "Referenz", "geometry": park}]
out = gpd.GeoDataFrame(rows, crs=25832).to_crs(4326); out["geometry"] = set_precision(out.geometry.values, 1e-6)
out.to_file("out/geojson/baumverlust_nordpark_vergleich.geojson", driver="GeoJSON", COORDINATE_PRECISION=6)
desc = (f"Größenvergleich: Die {len(verl)} per Sichtprüfung bestätigten Baumverlust-Flächen (je mindestens 1 Hektar) sind zusammen {de(summe_ha)} ha groß. "
        f"Der Nordpark in Wuppertal hat {de(park_ha)} ha, die Verlustfläche entspricht also {de(faktor)} Nordparks. Rot: die Form des Nordparks, um den Schwerpunkt auf {de(summe_ha)} ha vergrößert; "
        "grün: der tatsächliche Nordpark. Die rote Fläche zeigt NUR die Größe und ist kein Ort eines Verlusts; die echten Verlustflächen stehen im Layer 'Baumverlust bestätigt'. "
        "Es sind nur Flächen ab 1 ha nach Sichtprüfung; keine Gesamtbilanz des Baumbestands. "
        "Quellen: Nordpark OpenStreetMap, Weg 26435842, https://www.openstreetmap.org/way/26435842 (c) OpenStreetMap contributors, ODbL, https://www.openstreetmap.org/copyright ; "
        "Verlustflächen: Copernicus Sentinel-2 L2A https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a, Luftbilder Geobasis NRW https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?REQUEST=GetCapabilities&SERVICE=WMS ; "
        "Methode: https://github.com/benjamin-bleske/wuppertal-vegetation-sentinel2/blob/main/METHODIK_Baummaske.md .")
sty = style("baumverlust_nordpark_vergleich", f"Vergleich: {de(summe_ha)} ha Baumverlust = {de(faktor)} Nordparks", desc, ["Vergleich", "Baeume", "Nordpark"],
            {"nv": {"type": "geojson", "data": f"{BASE}/geojson/baumverlust_nordpark_vergleich.geojson"}},
            [{"id": "nv-fill", "type": "fill", "source": "nv", "paint": {"fill-color": ["match", ["get", "Vergleich"], "Referenz", "#2E7D32", "#D32F2F"], "fill-opacity": ["match", ["get", "Vergleich"], "Referenz", 0.75, 0.35]}},
             {"id": "nv-line", "type": "line", "source": "nv", "paint": {"line-color": ["match", ["get", "Vergleich"], "Referenz", "#1B5E20", "#7f0000"], "line-width": 2}}])
sty["metadata"]["carmaConf"]["layerInfo"]["keywords"] = [
    'carmaconf://infoBoxMapping:header: "Größenvergleich Baumverlust"',
    'carmaconf://infoBoxMapping:title: p["Name"]',
    'carmaconf://infoBoxMapping:subtitle: "Fläche: " + String(p["Fläche (ha)"]).replace(".", ",") + " Hektar"',
    'carmaconf://infoBoxMapping:additionalInfo: p["Vergleich"]']
json.dump(sty, open("out/styles/baumverlust_nordpark_vergleich.style.json", "w"), ensure_ascii=False, indent=1)
print(f"Summe {summe_ha:.2f} ha, Nordpark {park_ha:.2f} ha, Faktor {faktor:.2f}")
