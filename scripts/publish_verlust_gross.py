"""Veroeffentlicht die Baumverlust-Flaechen >= 1 ha (nach Sichtpruefung auf Luftbildern 2016/2023) als GeoJSON + Style.
Nummerierung = Reihenfolge nach Groesse wie in out/report/gross_*.png (scripts/verlust_gross_pruefen.py)."""
import json, geopandas as gpd
from shapely import set_precision
import sys; sys.path.insert(0, "scripts")
from build_styles import BASE, QUELLE, LINKS, style
FELD = {8, 19, 32, 34, 49}                 # sehen nach Feld/Wiese aus
STEIN = {7, 28, 52, 72}                    # Steinbruch
UFER = {23, 25, 61}                        # Stausee/Ufer
BEBAU = {41, 67, 73}                       # Gewerbe/Bahn/Bebauung
g = gpd.read_file("data/verlust_gross.gpkg").sort_values("a", ascending=False).reset_index(drop=True)
def pr(n):
    if n in FELD: return "unsicher: Feld oder Wiese moeglich"
    if n in STEIN: return "unsicher: Steinbruch"
    if n in UFER: return "unsicher: Seeufer"
    if n in BEBAU: return "unsicher: Gewerbe, Bahn oder Bebauung"
    return "wahrscheinlich Baumverlust"
g["nr"] = range(1, len(g) + 1); g["flaeche_ha"] = (g.a / 1e4).round(1); g["pruefung"] = g.nr.map(pr)
out = g[["nr", "flaeche_ha", "pruefung", "geometry"]].to_crs(4326); out["geometry"] = set_precision(out.geometry.values, 1e-6)
out.to_file("out/geojson/baumverlust_ueber_1ha.geojson", driver="GeoJSON", COORDINATE_PRECISION=6)
n_ok = int((g.pruefung == "wahrscheinlich Baumverlust").sum()); n = len(g)
desc = (f"Flaechen von mindestens 1 Hektar, auf denen Sentinel-2 zwischen den Sommern 2015-2019 und 2021-2025 einen Baumbestand verschwinden sieht ({n} Flaechen). "
        f"Sichtpruefung an Luftbildern 2016/2023 (Geobasis NRW): {n_ok} sehen nach abgeraeumtem Wald aus (rot), {n - n_ok} sind unsicher (orange: Feld/Wiese, Steinbruch, Seeufer, Bebauung moeglich). "
        "Die Sichtpruefung stammt vom Bearbeiter und ist nicht unabhaengig bestaetigt. Ursache der Verluste (Sturm, Kaefer, Einschlag) unbekannt. "
        "KEINE Gesamtbilanz des Baumbestands: kleinere Flaechen und der Zuwachs sind nicht verlaesslich und hier nicht enthalten. "
        "Baum-Referenz: nDOM 2025 Geobasis NRW https://www.opengeodata.nrw.de/produkte/geobasis/hm/ndom50_tiff/ ; Luftbilder https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?REQUEST=GetCapabilities&SERVICE=WMS ; "
        "Methode und Grenzen: https://github.com/benjamin-bleske/wuppertal-vegetation-sentinel2/blob/main/METHODIK_Baummaske.md ; Schritt fuer Schritt erklaert: https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/baummaske/ . ") + QUELLE + LINKS
sty = style("baumverlust_ueber_1ha", "Baumverlust ueber 1 Hektar (Sentinel-2, 2015-2019 zu 2021-2025)", desc, ["Sentinel-2", "Baeume", "Verlust", "Zeitreihe"],
            {"bv": {"type": "geojson", "data": f"{BASE}/geojson/baumverlust_ueber_1ha.geojson"}},
            [{"id": "bv-fill", "type": "fill", "source": "bv", "paint": {"fill-color": ["match", ["get", "pruefung"], "wahrscheinlich Baumverlust", "#D32F2F", "#F57C00"], "fill-opacity": 0.55}},
             {"id": "bv-line", "type": "line", "source": "bv", "paint": {"line-color": "#7f0000", "line-width": 1}}])
json.dump(sty, open("out/styles/baumverlust_ueber_1ha.style.json", "w"), ensure_ascii=False, indent=1)
print(n, "Flaechen;", n_ok, "wahrscheinlich;", round(float(g.a.sum()) / 1e6, 2), "km2 gesamt;", out.pruefung.value_counts().to_dict())
