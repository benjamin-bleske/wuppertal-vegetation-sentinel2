# Vegetation Wuppertal 2015–2025 (Sentinel-2)

Zeitreihe der dichten Vegetation im Stadtgebiet Wuppertal aus Sentinel-2-Sommermosaiken, als GeoJSON mit
MapLibre-Style-JSON zum Einbinden per Drag & Drop in den Digital Twin Wuppertal.

## Einbinden
Die URL einer Style-JSON (Endung `.json`) auf das Portalfenster ziehen:
https://digital-twin-wuppertal-live.github.io/geoportal/#/

Basis-URL: `https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/`

| Layer | Style-JSON |
|---|---|
| Vegetation je Jahr | `styles/vegetation_JAHR.style.json` |
| Veränderung (Verlust rot, Zuwachs blau) | `styles/aenderung_JAHR1_JAHR2.style.json` |
| Geländeschummerung (DGM1) | `styles/schummerung.style.json` |

## Methode
- Quelle: Copernicus Sentinel-2 L2A (Microsoft Planetary Computer), 10 m, Fenster **25.07.–15.09.** je Jahr.
- Wolkenfreies Median-Mosaik (`scripts/composite.py`): Szenenklassifikation SCL 2, 4, 5, 6, 7 gültig, Maske 2 px aufgeweitet, mind. 2 klare Beobachtungen je Pixel. SCL-Klasse 2 („dunkel“) bleibt gültig, weil ältere Prozessierungs-Baselines urbane Flächen so einstufen.
- Vegetation = **EVI > 0,45**, 3×3-Medianfilter, Flächen unter 400 m² entfernt (`scripts/vectorize.py`).
- Veränderung = Vegetationsmaske Jahr 1 gegen Jahr 2, nur Pixel, die in beiden Jahren gültig beobachtet wurden.

## Grenzen
- 10 m Auflösung: dichte Vegetation insgesamt (Bäume **und** dichte Wiesen), keine Einzelbäume.
- Jahresvergleiche hängen von Witterung und Sensor ab (z. B. Dürresommer 2020; 2015 nur Sentinel-2A). Ein Unterschied zwischen zwei Jahren ist kein Beleg für dauerhaften Baumverlust.
- In den Änderungslayern sind große eckige Flächen meist **Ackerland** (Fruchtfolge, Erntezeitpunkt) und schmale Streifen Randeffekte. Für eine Aussage zum Baumbestand müsste die Analyse auf Waldflächen/Gehölze beschränkt werden (offener nächster Schritt).
- 2015 gibt es erst ab 30.07. Daten (Start der Mission).

## Reproduzieren
`python -m venv .venv && .venv/bin/pip install rasterio pystac-client planetary-computer shapely geopandas pyogrio scikit-image scipy matplotlib requests mercantile pillow`, dann `scripts/get_boundary.py`, `scripts/composite.py JAHR`, `scripts/vectorize.py`, `scripts/build_styles.py`, `scripts/make_hillshade.py`, `scripts/publish_site.sh`.

## Quellen und Lizenzen
- Copernicus Sentinel-2 (Daten bereitgestellt über Microsoft Planetary Computer), Copernicus-Datenlizenz.
- Stadtgrenze: © OpenStreetMap contributors, ODbL 1.0.
- Geländeschummerung: DGM1 © Geobasis NRW, dl-de/zero-2-0.

## Ergebnis (Stand 2026-11-05)
Anteil dichter Vegetation an der Stadtfläche (EVI > 0,45): 2015 53,5 % · 2016 50,4 · 2017 59,3 · 2018 44,6 · 2019 47,9 · 2020 44,9 · 2021 49,3 · 2022 47,6 · 2023 53,5 · 2024 61,1 · 2025 57,0.
Die Reihe ist **nicht monoton**; sie schwankt mit Witterung (Tiefpunkte in den Dürrejahren 2018 und 2020). 2015→2025: 8,8 km² Verlust, 14,7 km² Zuwachs. Damit lässt sich ein Rückgang des Baumbestands mit diesen Daten **nicht belegen**.
