# Vegetation Wuppertal 2015–2025 (Sentinel-2)

Zeitreihe der dichten Vegetation im Stadtgebiet Wuppertal aus Sentinel-2-Sommermosaiken, als GeoJSON mit
MapLibre-Style-JSON zum Einbinden per Drag & Drop in den Digital Twin Wuppertal.

## Methodik
[Verständliche Erklärung in Bildern (für Laien, mit Prüfbeispielen)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/erklaerung/)

[Wie finden wir Bäume im Satellitenbild? Schritt für Schritt (für Laien)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/baummaske/)

[Test: Welche Satellitengröße trennt Bäume? (NDVI, Jahresschwankung, nDOM-Referenz)](METHODIK_Baummaske.md)

[Logbuch Baumverlust als PDF (51 bestätigte Flächen, Foto von 2016 und von 2025 nebeneinander, 14 MB)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/logbuch/Logbuch_Baumverlust.pdf)

[Methodik als PDF (Workflow am Beispiel 2015 und 2016)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/Methodik_Vegetation_Wuppertal_2015_2016.pdf)

## Einbinden
Link auf das Portalfenster ziehen (https://digital-twin-wuppertal-live.github.io/geoportal/#/) oder die URL kopieren.

**Baumverlust (große Flächen ab 1 ha)**

- [EMPFOHLEN: Baumverlust bestätigt (51 Flächen, 144,5 ha; genau die Flächen aus dem Logbuch-PDF)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/baumverlust_final.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/baumverlust_final.style.json`
- [Größenvergleich: 144,5 ha Baumverlust = 3,9 Nordparks (rot: Form des Nordparks vergrößert, grün: echter Nordpark)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/baumverlust_nordpark_vergleich.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/baumverlust_nordpark_vergleich.style.json`
- [Vorstufe: alle 73 Erkennungen vor der Prüfung (nur zum Vergleich; rot wahrscheinlich, orange unsicher)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/baumverlust_ueber_1ha.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/baumverlust_ueber_1ha.style.json`

**Zeitreihe mit Filter-Buttons (eine Datei, 11 Jahre)**

- [Zeitreihe 2015–2025 mit Jahres-Buttons](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_zeitreihe.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_zeitreihe.style.json`
- [Zeitreihe 2015–2025, Test: Mehrfachauswahl (OR)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_zeitreihe_or.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_zeitreihe_or.style.json`

**Vegetation je Jahr**

- [Vegetation 2015](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2015.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2015.style.json`
- [Vegetation 2016](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2016.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2016.style.json`
- [Vegetation 2017](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2017.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2017.style.json`
- [Vegetation 2018](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2018.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2018.style.json`
- [Vegetation 2019](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2019.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2019.style.json`
- [Vegetation 2020](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2020.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2020.style.json`
- [Vegetation 2021](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2021.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2021.style.json`
- [Vegetation 2022](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2022.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2022.style.json`
- [Vegetation 2023](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2023.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2023.style.json`
- [Vegetation 2024](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2024.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2024.style.json`
- [Vegetation 2025](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2025.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/vegetation_2025.style.json`

**Veränderung**

- [Veränderung 2015 → 2020 (Verlust rot, Zuwachs blau)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/aenderung_2015_2020.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/aenderung_2015_2020.style.json`
- [Veränderung 2015 → 2025 (Verlust rot, Zuwachs blau)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/aenderung_2015_2025.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/aenderung_2015_2025.style.json`
- [Veränderung 2020 → 2025 (Verlust rot, Zuwachs blau)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/aenderung_2020_2025.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/aenderung_2020_2025.style.json`

**Untergrund**

- [Geländeschummerung (DGM1)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/schummerung.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/schummerung.style.json`

**Historische Luftbilder (Jahrgänge für Wuppertal)**

- [Luftbild 2010 (Geobasis NRW)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/luftbild_2010.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/luftbild_2010.style.json`
- [Luftbild 2013 (Geobasis NRW)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/luftbild_2013.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/luftbild_2013.style.json`
- [Luftbild 2016 (Geobasis NRW)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/luftbild_2016.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/luftbild_2016.style.json`
- [Luftbild 2019 (Geobasis NRW)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/luftbild_2019.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/luftbild_2019.style.json`
- [Luftbild 2021 (Geobasis NRW)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/luftbild_2021.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/luftbild_2021.style.json`
- [Luftbild 2023 (Geobasis NRW)](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/luftbild_2023.style.json) 
  `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/luftbild_2023.style.json`

## Methode
- Quelle: Copernicus Sentinel-2 L2A (Microsoft Planetary Computer), 10 m, Fenster **25.07.–15.09.** je Jahr.
- Wolkenfreies Median-Mosaik (`scripts/composite.py`): Szenenklassifikation SCL 2, 4, 5, 6, 7 gültig, Maske 2 px aufgeweitet, mind. 2 klare Beobachtungen je Pixel. SCL-Klasse 2 („dunkel“) bleibt gültig, weil ältere Prozessierungs-Baselines urbane Flächen so einstufen.
- Vegetation = **EVI > 0,45**, 3×3-Medianfilter, Flächen unter 400 m² entfernt (`scripts/vectorize.py`).
- Veränderung = Vegetationsmaske Jahr 1 gegen Jahr 2, nur Pixel, die in beiden Jahren gültig beobachtet wurden.
- **Baumverlust (neu):** Der EVI trennt Bäume nicht von Acker/Wiese (AUC 0,60 gegen Acker/Wiese). Deshalb wurde an der Höhenkarte nDOM 2025 (Geobasis NRW) angelernt, welche Satelliten-Eigenschaften Bäume trennen (EVI-Schwankung über die Jahre, NDVI, NDMI; Trefferquote auf Testkacheln 95 % / 94 %). Zwei Fenster 2015–2019 und 2021–2025, Schwelle je Fenster an OSM-Wald kalibriert (`scripts/baummaske.py`). Veröffentlicht sind nur Verlustflächen ≥ 1 ha (73 Stück), einzeln auf Luftbildern 2016/2023 angesehen. Ausführlich: [METHODIK_Baummaske.md](METHODIK_Baummaske.md), für Laien: [Erklärseite](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/baummaske/).

## Grenzen
- 10 m Auflösung: dichte Vegetation insgesamt (Bäume **und** dichte Wiesen), keine Einzelbäume.
- Jahresvergleiche hängen von Witterung und Sensor ab (z. B. Dürresommer 2020; 2015 nur Sentinel-2A). Ein Unterschied zwischen zwei Jahren ist kein Beleg für dauerhaften Baumverlust.
- In den Änderungslayern sind große eckige Flächen meist **Ackerland** (Fruchtfolge, Erntezeitpunkt) und schmale Streifen Randeffekte. Für Bäume gibt es deshalb die Baumverlust-Schicht (siehe Methode); die Vegetationsschichten und ihre Veränderungslayer sagen nichts über Bäume.
- 2015 gibt es erst ab 30.07. Daten (Start der Mission).
- Baumverlust: Die Baum-Referenz (nDOM) gibt es nur für 2025; die Zuwachsflächen sind nach Sichtprüfung größtenteils falsch (0 von 9 überzeugend), kleine Verluste häufig ebenfalls. **Es gibt keine Gesamtbilanz des Baumbestands.** Die Einordnung der 73 großen Flächen (58 wahrscheinlich Baumverlust, 15 unsicher) ist eine Sichtprüfung des Bearbeiters, nicht unabhängig bestätigt. Ursache der Verluste unbekannt.

## Reproduzieren
`python -m venv .venv && .venv/bin/pip install rasterio pystac-client planetary-computer shapely geopandas pyogrio scikit-image scipy matplotlib requests mercantile pillow`, dann `scripts/get_boundary.py`, `scripts/composite.py JAHR`, `scripts/vectorize.py`, `scripts/build_styles.py`, `scripts/make_hillshade.py`, `scripts/publish_site.sh`. Baumverlust: `scripts/schwelle_osm.py`, `scripts/ndom_select.py` (lädt 80 nDOM-Kacheln, 1,3 GB), `scripts/osm_buildings.py`, `scripts/baummaske_test.py`, `scripts/baummaske.py`, `scripts/verlust_gross_pruefen.py`, `scripts/publish_verlust_gross.py`. Achtung: `publish_site.sh` kopiert das ganze Verzeichnis `out/geojson` nach `docs/`; die unzuverlässigen Baumkarten dort nicht mitveröffentlichen.

## Quellen und Lizenzen
- Copernicus Sentinel-2 (Daten bereitgestellt über Microsoft Planetary Computer), Copernicus-Datenlizenz.
- Stadtgrenze: © OpenStreetMap contributors, ODbL 1.0.
- Geländeschummerung: DGM1 © Geobasis NRW, dl-de/zero-2-0.
- Höhenkarte nDOM 2025 (Baum-Referenz): © Geobasis NRW, dl-de/zero-2-0, <https://www.opengeodata.nrw.de/produkte/geobasis/hm/ndom50_tiff/>.
- Historische Luftbilder (WMS NW Hist DOP): © Geobasis NRW, dl-de/zero-2-0, <https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?REQUEST=GetCapabilities&SERVICE=WMS>.
- Gebäude und Waldflächen (nur Hilfsdaten für Referenz und Kalibrierung): © OpenStreetMap contributors, ODbL 1.0.
- EVI: Huete et al. 2002, <https://doi.org/10.1016/S0034-4257(02)00096-2>.

## Ergebnis (Stand 2026-11-05)
Anteil dichter Vegetation an der Stadtfläche (EVI > 0,45): 2015 53,5 % · 2016 50,4 · 2017 59,3 · 2018 44,6 · 2019 47,9 · 2020 44,9 · 2021 49,3 · 2022 47,6 · 2023 53,5 · 2024 61,1 · 2025 57,0.
Die Reihe ist **nicht monoton**; sie schwankt mit Witterung (Tiefpunkte in den Dürrejahren 2018 und 2020). 2015→2025: 8,8 km² Verlust, 14,7 km² Zuwachs. Damit lässt sich ein Rückgang des Baumbestands mit diesen Daten **nicht belegen**.

## Ergebnis Baumverlust (Stand 2026-11-10)
Fenster 2015–2019 → 2021–2025, Verlustflächen ≥ 1 ha: 73 Flächen, 1,9 km². Nach Sichtprüfung auf Luftbildern 2016/2023 sehen 58 nach abgeräumtem Nadelwald aus, 15 sind unsicher (5 Feld/Wiese, 4 Steinbruch, 3 Seeufer, 3 Gewerbe/Bahn/Bebauung). Alle Flächen einzeln: [Blatt 1](docs/baummaske/gross_1.png), [2](docs/baummaske/gross_2.png), [3](docs/baummaske/gross_3.png). Das belegt große Waldabräumungen, aber **keinen Gesamtrückgang** des Baumbestands: kleinere Verluste und der Zuwachs sind nicht verlässlich bestimmt.

## Ergebnis Baumverlust, von Hand bestätigt (Stand 2026-11-10)
Die 73 großen Flächen wurden im Prüf-Tool (`tools/pruef_tool/`, Anleitung dort) einzeln gegen Luftbilder **2016 (früher) und 2025 (heute)** (Geobasis NRW, dl-de/zero-2-0) beurteilt: **51 Ja (144,5 ha), 13 Nein, 9 Unsicher**. Nur die 51 bestätigten Flächen stehen im Layer [`baumverlust_final`](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/baumverlust_final.style.json) (GeoJSON: [`geojson/baumverlust_final.geojson`](docs/geojson/baumverlust_final.geojson)). Felder in der Infobox: `Nr`, `Fläche (ha)`, `Ursache` (nicht angegeben), `Notiz`. Die Entscheidungen liegen unverändert in [`docs/logbuch/entscheidungen.json`](docs/logbuch/entscheidungen.json).
Das [Logbuch als PDF](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/logbuch/Logbuch_Baumverlust.pdf) (14 MB) zeigt je Fläche Foto von 2016 und von 2025 mit gelbem Umriss, Maßstab, Koordinaten und Quelle. Neu erzeugen: `.venv/bin/python scripts/logbuch.py tools/pruef_tool/entscheidungen.json`, die Prüfdaten entstehen mit `scripts/build_pruef_daten.py`.
**Größenvergleich:** Zusammen sind die 51 bestätigten Flächen 144,5 ha groß, das sind 3,9 Nordparks (Nordpark Wuppertal laut OSM 37,3 ha). Der Layer [`baumverlust_nordpark_vergleich`](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/baumverlust_nordpark_vergleich.style.json) zeigt den echten Nordpark (grün) und seine Form auf 144,5 ha vergrößert (rot). Die rote Fläche zeigt nur die Größe, nicht den Ort des Verlusts (`scripts/publish_nordpark_vergleich.py`).
**Baumzuwachs ab 1 ha (Stand 2026-11-12):** Dasselbe Verfahren mit umgekehrtem Vorzeichen (2015–2019 kein Baum, 2021–2025 Baum, nahe Teile bis 20 m zusammengefasst) ergab 58 Kandidaten (114 ha). Nach Sichtprüfung an Luftbildern 2016/2025 sind **5 bestätigt (7,2 ha)**, 53 abgelehnt (meist Acker und Wiese). Zuwachs wird vom Verfahren also deutlich schlechter erkannt als Verlust (Trefferquote 9 %). Skripte: `scripts/zuwachs_kandidaten.py`, `scripts/build_zuwachs.py`, `scripts/logbuch_zuwachs.py`; Tool: `tools/pruef_tool_zuwachs/` mit den Entscheidungen. Dieser Zuwachs-Layer ist bisher nicht veröffentlicht; gegen 144,5 ha bestätigten Verlust (ebenfalls nur große Flächen) ist das keine Bilanz des Baumbestands.
**Grenzen:** Es ist eine Sichtprüfung des Bearbeiters, keine amtliche Prüfung. Die Luftbildjahre passen nicht genau zu den Sentinel-Fenstern (2015–2019 / 2021–2025). Die Ursache der Verluste (Sturm, Käfer, Einschlag) ist nicht erfasst. Flächen unter 1 ha und der Zuwachs fehlen, es gibt keine Gesamtbilanz des Baumbestands. Das Luftbild von 2025 ist ein Sommerbild (Bildflug meist Juni 2025), das von 2016 meist Sommer 2016; die Aufnahmedaten stehen je Fläche im Tool.
