"""Erzeugt aus dem Verlust-Pruef-Tool und dem Verlust-Logbuch die Zuwachs-Varianten (Baumzuwachs >= 1 ha, Luftbild 2016 -> 2025).
Eingang: data/zuwachs_gross.gpkg (scripts/zuwachs_kandidaten.py), tools/pruef_tool/index.html, scripts/logbuch.py
Ausgang: tools/pruef_tool_zuwachs/{index.html,daten.js,ANLEITUNG.md}, scripts/logbuch_zuwachs.py
Aufruf: .venv/bin/python scripts/build_zuwachs.py"""
import json, os, re, geopandas as gpd

def ersetze(s, paare):
    for a, b in paare:
        assert a in s, "nicht gefunden: " + a[:70]
        s = s.replace(a, b)
    return s

g = gpd.read_file("data/zuwachs_gross.gpkg").sort_values("a", ascending=False).reset_index(drop=True)
N = len(g)
# ---- daten.js
c = gpd.GeoSeries(g.geometry.representative_point(), crs=25832).to_crs(4326); g4 = gpd.GeoSeries(g.geometry, crs=25832).to_crs(4326)
ring = lambda r: [[round(x, 1), round(y, 1)] for x, y in r.coords]
ring4 = lambda r: [[round(x, 6), round(y, 6)] for x, y in r.coords]
out = []
for i, row in g.iterrows():
    geo = row.geometry; x0, y0, x1, y1 = geo.bounds
    if geo.geom_type == "MultiPolygon": geo = max(geo.geoms, key=lambda p: p.area); g4.iloc[i] = max(g4.iloc[i].geoms, key=lambda p: p.area)
    out.append({"nr": i + 1, "ha": round(row.a / 1e4, 1), "pruefung": "Kandidat aus dem Satellitenvergleich: 2015–2019 kein Baum, 2021–2025 Baum (Fläche zählt nur die Zuwachs-Pixel)",
                "lon": round(c[i].x, 6), "lat": round(c[i].y, 6), "bbox": [round(v, 1) for v in (x0, y0, x1, y1)],
                "ringe": [ring(geo.exterior)] + [ring(r) for r in geo.interiors], "ringe4326": [ring4(g4[i].exterior)] + [ring4(r) for r in g4[i].interiors]})
os.makedirs("tools/pruef_tool_zuwachs", exist_ok=True)
open("tools/pruef_tool_zuwachs/daten.js", "w").write("// automatisch erzeugt von scripts/build_zuwachs.py; Koordinaten EPSG:25832, ringe = Aussenring + Loecher; ringe4326 = WGS84\nconst FLAECHEN = " + json.dumps(out, separators=(",", ":")) + ";\n")

# ---- Tool
h = open("tools/pruef_tool/index.html").read()
h = re.sub(r"    <li><b>Ja = Baumverlust:</b>.*</li>", "    <li><b>Ja = Baumzuwachs:</b> links (früher, 2016) Acker, Wiese, Brache oder freie Fläche – rechts (heute, 2025) Wald oder dichte Baumgruppe mit hohen Kronen.</li>", h)
h = re.sub(r"    <li><b>Nein:</b>.*</li>", "    <li><b>Nein:</b> schon 2016 Wald (dann ist es kein Zuwachs) – oder rechts steht kein Wald (nur Feld, Wiese, Gebüsch, Solaranlage, Garten, Gewächshaus, anderer Anbau).</li>", h)
h = ersetze(h, [
    ("<title>Prüf-Tool Baumverlust Wuppertal</title>", "<title>Prüf-Tool Baumzuwachs Wuppertal</title>"),
    ("Ist hier wirklich Baum-Bestand verschwunden?", "Ist hier wirklich Baumbestand dazugekommen?"),
    ("<b>73 Flächen</b>", f"<b>{N} Flächen</b>"),
    ("offenbar Bäume verschwunden sind", "offenbar Bäume dazugekommen sind (Achtung: Das Verfahren verwechselt Zuwachs oft mit Feldfrüchten, die in einem Fenster gerade grün waren; rechnen Sie mit vielen „Nein“)"),
    ('max="73"', f'max="{N}"'),
    ("Baumverlust (J)", "Baumzuwachs (J)"),
    ('"pruef_tool_baumverlust_v1"', '"pruef_tool_baumzuwachs_v1"'),
    ("✔ Ja = Baumverlust", "✔ Ja = Baumzuwachs"),
    ("ja = Baumverlust, nein", "ja = Baumzuwachs, nein"),
    ("baumverlust_final.geojson", "baumzuwachs_final.geojson"),
    ("<option>unbekannt</option><option>Kahlschlag/Einschlag</option><option>Sturm/Käfer vermutet</option><option>Steinbruch/Abbau</option><option>Bebauung</option><option>Sonstiges</option>",
     "<option>unbekannt</option><option>Aufforstung/Pflanzung</option><option>natürliche Wiederbewaldung</option><option>Aufwuchs nach Kahlschlag</option><option>Park/Grünanlage</option><option>Sonstiges</option>"),
    ("z. B. „Nadelwald 2016, 2025 komplett kahl“", "z. B. „2016 Wiese, 2025 junger Mischwald“"),
])
open("tools/pruef_tool_zuwachs/index.html", "w").write(h)
open("tools/pruef_tool_zuwachs/ANLEITUNG.md", "w").write(f"""# Prüf-Tool Baumzuwachs (Wuppertal)
Gleiche Bedienung wie `tools/pruef_tool/ANLEITUNG.md`, aber für {N} Zuwachs-Kandidaten ab 1 ha (Baum 2021–2025, kein Baum 2015–2019 laut Sentinel-2).
1. `cd tools/pruef_tool_zuwachs && python3 -m http.server 8766`, dann http://localhost:8766/index.html öffnen.
2. Links Luftbild 2016, rechts 2025. Ja (J) = Baumzuwachs, Nein (N), Unsicher (U). Auf Beschriftung des Bildes achten: ein Sommerbild links und rechts vergleichen.
3. „Entscheidungen exportieren“ liefert `entscheidungen.json`. Daraus: `.venv/bin/python scripts/logbuch_zuwachs.py entscheidungen.json` (finaler Layer und Logbuch-PDF).
Der Zuwachs wurde früher nach Stichprobe als unzuverlässig eingestuft (0 von 9 überzeugend); dies ist die Prüfung mit Luftbildern dazu.
""")

# ---- Logbuch
s = open("scripts/logbuch.py").read()
s = re.sub(r'"""Finaler Layer.*?"""', '"""Finaler Layer und Logbuch-PDF (Baumzuwachs) aus den im Zuwachs-Pruef-Tool exportierten Entscheidungen.\nAufruf: .venv/bin/python scripts/logbuch_zuwachs.py tools/pruef_tool_zuwachs/entscheidungen.json\nErzeugt: out/geojson/baumzuwachs_final.geojson, out/styles/baumzuwachs_final.style.json, out/Logbuch_Baumzuwachs.pdf (erzeugt von scripts/build_zuwachs.py)"""', s, count=1, flags=re.S)
s = re.sub(r'    desc = \(f"Baumverlust-Flaechen.*?\) \+ QUELLE \+ LINKS\n', '''    desc = (f"Baumzuwachs-Flaechen von mindestens 1 Hektar, auf denen Sentinel-2 zwischen den Sommern 2015-2019 und 2021-2025 einen neuen Baumbestand sieht "
            f"und die vom Nutzer per Sichtpruefung an Luftbildern (Geobasis NRW, 2016 und 2025) bestaetigt wurden: {len(ja)} bestaetigte Flaechen, zusammen {de(ges_ha)} ha "
            f"({geprueft} von {len(g)} Kandidaten entschieden). Die Bestaetigung ist eine Sichtpruefung des Nutzers, keine amtliche Pruefung; die Luftbild-Jahre passen nicht genau zu den Sentinel-Zeitraeumen. "
            "Der Zuwachs ist methodisch unsicherer als der Verlust (Feldfruechte werden leicht mit Baeumen verwechselt); die Sichtpruefung ist der entscheidende Schritt. "
            "KEINE Gesamtbilanz des Baumbestands: kleinere Flaechen (unter 1 ha) und alle Verluste sind hier nicht enthalten. "
            "Luftbilder https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?REQUEST=GetCapabilities&SERVICE=WMS ; "
            f"Methode und Grenzen: {METHODIK} ; Schritt fuer Schritt erklaert: https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/baummaske/ . ") + QUELLE + LINKS\n''', s, count=1, flags=re.S)
s = ersetze(s, [
    ("data/verlust_gross.gpkg", "data/zuwachs_gross.gpkg"),
    ("baumverlust_final", "baumzuwachs_final"), ("Logbuch_Baumverlust.pdf", "Logbuch_Baumzuwachs.pdf"),
    ('"Baumverlust bestaetigt (Sichtpruefung, Sentinel-2 2015-2019 zu 2021-2025)"', '"Baumzuwachs bestaetigt (Sichtpruefung, Sentinel-2 2015-2019 zu 2021-2025)"'),
    ('["Sentinel-2", "Baeume", "Verlust", "Sichtpruefung"]', '["Sentinel-2", "Baeume", "Zuwachs", "Sichtpruefung"]'),
    ('"Baumverlust bestätigt, Nr. "', '"Baumzuwachs bestätigt, Nr. "'),
    ("Logbuch Baumverlust Wuppertal", "Logbuch Baumzuwachs Wuppertal"), ('"Logbuch Baumverlust"', '"Logbuch Baumzuwachs"'),
    ("Wuppertal, Flächen ab 1 Hektar – per Sichtprüfung bestätigt", "Wuppertal, Flächen ab 1 Hektar – per Sichtprüfung bestätigt (Wiederbewaldung und neuer Baumbestand)"),
    ("auf denen zwischen den Sommern 2015–2019 und 2021–2025 Baumbestand (meist Nadelwald) verschwunden ist. ", "auf denen zwischen den Sommern 2015–2019 und 2021–2025 neuer Baumbestand entstanden ist. "),
    ("Die Erkennung fand 73 Flächen von mindestens 1 Hektar.", f"Die Erkennung fand {N} Kandidaten von mindestens 1 Hektar; der Zuwachs wird vom Verfahren unsicherer erkannt als der Verlust."),
    ("Bestätigt als Baumverlust (Ja)", "Bestätigt als Baumzuwachs (Ja)"), ('"Erkennungen ab 1 ha"', '"Kandidaten ab 1 ha"'),
    ("nur die größeren Flächen (ab 1 ha) und nur das, was auf den Luftbildern erkennbar war.", "nur die größeren Zuwachsflächen (ab 1 ha) und nur das, was auf den Luftbildern erkennbar war. Verluste sind in einem eigenen Logbuch dokumentiert."),
    ("Wo früher Bäume waren und später nicht mehr, entsteht eine Verlustfläche.", "Wo früher keine Bäume waren und später welche, entsteht eine Zuwachsfläche (Kandidat). Das Verfahren verwechselt Zuwachs häufig mit Feldfrüchten, daher ist die Sichtprüfung entscheidend."),
    ("Flächen unter 1 ha und Baumzuwachs sind nicht enthalten.", "Flächen unter 1 ha und Baumverluste sind hier nicht enthalten."),
    ("(Einschlag, Sturm, Käfer, Abbau, Bebauung) ist aus den Bildern nicht sicher ablesbar.", "(Pflanzung, natürliche Wiederbewaldung, Aufwuchs nach Kahlschlag) ist aus den Bildern nicht sicher ablesbar."),
    ("Bildflug laut Geobasis NRW für alle 73 Flächen im Jahr 2025 (meist Juni, 5 Flächen Juli, 1 Fläche März)", "Bildflug laut Geobasis NRW im Jahr 2025 (meist Sommer; das Datum je Fläche wurde hier nicht einzeln abgefragt)"),
    ("ha Baumverlust\"", "ha Baumzuwachs\""),
    ('CACHE = "data/logbuch_cache"', 'CACHE = "data/logbuch_cache_zuwachs"'),
    ("Ein Verlust kann zwischen den Zeiträumen, aber auch vor 2016 passiert sein.", "Ein Zuwachs kann zwischen den Zeiträumen, aber auch schon vor 2016 begonnen haben."),
])
open("scripts/logbuch_zuwachs.py", "w").write(s)
print(N, "Kandidaten; Tool und Logbuch-Skript erzeugt")
