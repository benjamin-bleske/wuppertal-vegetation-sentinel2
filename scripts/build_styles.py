"""Erzeugt MapLibre-Style-JSONs (Muster wie carmaWIKI: carmaConf.layerInfo + geojson-Source mit URL)."""
import json, os, sys

BASE = os.environ.get("PAGES_BASE", "https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2")
OUT = "out/styles"
os.makedirs(OUT, exist_ok=True)
QUELLE = ("Quelle: Copernicus Sentinel-2 L2A (Median-Mosaik 25.07.-15.09., 10 m, Microsoft Planetary Computer); "
          "Stadtgrenze (c) OpenStreetMap contributors (ODbL). ")
HINWEIS = ("Hinweis: EVI > 0,45 zeigt dichte Vegetation insgesamt (Baeume und dichte Wiesen), keine einzelnen Baeume. "
           "Jahresvergleiche sind witterungsabhaengig (z. B. Duerresommer 2018/2020). In den Aenderungslayern sind grosse eckige Flaechen meist Ackerland (Fruchtfolge/Erntezeitpunkt), keine Baumverluste; schmale Streifen sind Randeffekte.")

def style(name, title, desc, tags, sources, layers):
    return {"version": 8, "name": name,
            "metadata": {"carmaConf": {"layerInfo": {"title": title, "description": desc, "keywords": [], "tags": tags},
                                       "instant": True}},
            "sources": sources, "layers": layers}

def save(fname, s):
    with open(f"{OUT}/{fname}", "w") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)

def veg(year):
    sid = f"veg{year}"
    save(f"vegetation_{year}.style.json", style(
        f"vegetation_{year}", f"Vegetation {year} (Sentinel-2, EVI)",
        f"Dichte Vegetation im Sommer {year}: EVI > 0,45. {QUELLE}{HINWEIS}",
        ["Sentinel-2", "Vegetation", "Zeitreihe", str(year)],
        {sid: {"type": "geojson", "data": f"{BASE}/geojson/vegetation_{year}.geojson"}},
        [{"id": f"{sid}-fill", "type": "fill", "source": sid,
          "paint": {"fill-color": "#2E7D32", "fill-opacity": 0.55}}]))

def change(y1, y2):
    sid = f"aend{y1}{y2}"
    save(f"aenderung_{y1}_{y2}.style.json", style(
        f"aenderung_{y1}_{y2}", f"Vegetationsaenderung {y1} bis {y2} (Sentinel-2, EVI)",
        f"Rot: Vegetation {y1} vorhanden, {y2} nicht (Verlust). Blau: neu {y2} (Zuwachs). Nur Pixel, die in beiden Jahren gueltig beobachtet wurden. {QUELLE}{HINWEIS}",
        ["Sentinel-2", "Vegetation", "Aenderung", f"{y1}-{y2}"],
        {sid: {"type": "geojson", "data": f"{BASE}/geojson/aenderung_{y1}_{y2}.geojson"}},
        [{"id": f"{sid}-fill", "type": "fill", "source": sid,
          "paint": {"fill-color": ["match", ["get", "klasse"], "Verlust", "#D32F2F", "Zuwachs", "#1976D2", "#999999"],
                    "fill-opacity": 0.75}}]))

def hillshade():
    save("schummerung.style.json", style(
        "schummerung_wuppertal", "Gelaendeschummerung Wuppertal (DGM1 NRW)",
        "Multidirektionale Schummerung aus dem DGM1 NRW (Geobasis NRW, dl-de/zero-2-0), Zoom 9-14, ausserhalb der Stadtgrenze ausgeblendet.",
        ["DGM", "Schummerung", "Gelaende"],
        {"hs": {"type": "raster", "tiles": [f"{BASE}/tiles/hillshade/{{z}}/{{x}}/{{y}}.png"],
                "tileSize": 256, "minzoom": 9, "maxzoom": 14,
                "attribution": "Geobasis NRW (dl-de/zero-2-0)"}},
        [{"id": "hs-raster", "type": "raster", "source": "hs", "paint": {"raster-opacity": 0.6}}]))

if __name__ == "__main__":
    years = [int(y) for y in sys.argv[1].split(",")]
    for y in years: veg(y)
    for a, b in [(years[0], years[-1]), (2015, 2020), (2020, 2025)]:
        if a in years and b in years and a != b: change(a, b)
    hillshade()
    print(sorted(os.listdir(OUT)))
