"""Kombiniert die Jahres-Vegetation zu einer Datei (Attribut jahr, String) und erzeugt die Zeitreihen-Styles mit Filter-Buttons."""
import json, os
from build_styles import BASE, QUELLE, HINWEIS, style

YEARS = list(range(2015, 2026))
FARBEN = ["#8E24AA", "#5E35B1", "#3949AB", "#1E88E5", "#00ACC1", "#00897B", "#43A047", "#7CB342", "#C0CA33", "#F9A825", "#EF6C00"]

feats = []
for y in YEARS:
    for i, f in enumerate(json.load(open(f"out/geojson/vegetation_{y}.geojson"))["features"], 1):
        feats.append({"type": "Feature", "id": f"{y}-{i:04d}", "properties": {"jahr": str(y)}, "geometry": f["geometry"]})
os.makedirs("out/geojson", exist_ok=True)
with open("out/geojson/vegetation_alle.geojson", "w") as f:
    json.dump({"type": "FeatureCollection", "features": feats}, f, separators=(",", ":"))
print(len(feats), "Features")

farbe = ["match", ["get", "jahr"]] + [x for y, c in zip(YEARS, FARBEN) for x in (str(y), c)] + ["#2E7D32"]
DESC = ("Dichte Vegetation (EVI > 0,45) im Sommer 2015-2025, Jahr per Button waehlen. "
        "ACHTUNG: Die Reihe schwankt mit der Witterung (Tiefpunkte in den Duerrejahren 2018 und 2020) und belegt keinen Baumrueckgang. "
        + QUELLE + HINWEIS)

def zeitreihe(mode, fname, title):
    s = style(f"vegetation_zeitreihe_{mode}", title, DESC, ["Sentinel-2", "Vegetation", "Zeitreihe"],
              {"veg": {"type": "geojson", "data": f"{BASE}/geojson/vegetation_alle.geojson"}},
              [{"id": "veg-fill", "type": "fill", "source": "veg", "paint": {"fill-color": farbe, "fill-opacity": 0.55}}])
    s["metadata"]["carmaConf"]["filterConfig"] = {
        "layerPattern": "veg-", "filterMode": mode, "filterType": "button", "allLabel": "Alle Jahre",
        "filters": [{"key": str(y), "label": str(y), "propertyName": "jahr", "propertyValue": str(y)} for y in YEARS]}
    json.dump(s, open(f"out/styles/{fname}", "w"), ensure_ascii=False, indent=1)

zeitreihe("and", "vegetation_zeitreihe.style.json", "Vegetation Zeitreihe 2015-2025 (Sentinel-2, EVI)")
zeitreihe("or", "vegetation_zeitreihe_or.style.json", "Vegetation Zeitreihe 2015-2025 (Test: Mehrfachauswahl)")
