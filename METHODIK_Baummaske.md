# Von „Vegetation" zu „Bäumen": Test, welche Satellitengröße Bäume trennt

Stand: 10.11.2026. Alle Zahlen stammen aus den Skripten in `scripts/` und lassen sich damit neu erzeugen. Rohdaten und Zwischenstände liegen in `data/` (nicht im Repo).

## 1. Ausgangsfrage
Unsere Vegetationsschicht (EVI > 0,45) markiert „viel Grün" und kann Bäume nicht von Wiesen und Äckern trennen. Die großen „Verlust"-Flächen im Vergleich 2015 → 2025 sind überwiegend Äcker und Wiesen (siehe [verständliche Erklärung](https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/erklaerung/)). Gesucht: eine Satellitengröße (oder Kombination), die Bäume besser trennt, und eine Prüfung dagegen mit unabhängigen Daten.

## 2. Schritt 1: Hilft eine höhere EVI-Schwelle? (`scripts/schwelle_osm.py`)
- **Referenz:** OpenStreetMap (© OpenStreetMap contributors, ODbL): 660 Waldflächen (`landuse=forest`, `natural=wood`) und 1.071 Feld-/Wiesenflächen (`farmland`, `meadow`) in Wuppertal, 15 m vom Rand entfernt. Rund 418.000 Wald- und 188.000 Feld/Wiese-Pixel.
- **Messung:** Anteil der Pixel mit EVI über der Schwelle, in allen elf Sommermosaiken.

| Schwelle | Wald (Mittel, Spanne der Jahre) | Feld/Wiese |
|---|---|---|
| 0,45 (bisher) | 84 % (73–92) | 66 % (43–80) |
| 0,55 | 57 % (31–74) | 52 % (23–74) |
| 0,60 | 37 % (13–57) | 43 % (15–67) |
| 0,65 | 19 % (4–40) | 34 % (9–58) |

- **Ergebnis:** Ab etwa 0,57 verliert man mehr Wald als Feld. **Eine höhere EVI-Schwelle trennt nicht.** Bild: `docs/baummaske/schwelle_osm.png`.
- **Grenze:** OSM-Flächen sind von Freiwilligen gezeichnet (Brachen, Obstwiesen, lichter Wald sind nicht sauber getrennt).

## 3. Schritt 2: Welche Größe trennt Bäume? (`scripts/ndom_select.py`, `scripts/osm_buildings.py`, `scripts/baummaske_test.py`)
**Referenz „Baum" aus Höhendaten:**
- nDOM 2025 (normalisiertes Oberflächenmodell, 0,5 m, Geobasis NRW, dl-de/zero-2-0): <https://www.opengeodata.nrw.de/produkte/geobasis/hm/ndom50_tiff/ndom50_tiff/>. Für Wuppertal gibt es nur diesen einen Stand (2025, zum Teil 2023); ältere Jahrgänge sind nicht veröffentlicht, ebenso kein älteres DOM.
- 80 von 212 Kacheln (zufällig, Seed 42), 1,3 GB.
- Gebäude (OSM, 208.109 Grundrisse, 2 m Puffer) aus dem nDOM herausgenommen, weil das nDOM auch Dächer enthält.
- Auf das 10-m-Gitter der Satellitenmosaike gebracht (20 × 20 Zellen je Pixel). **Baum:** mindestens 60 % der Zellen höher als 3 m. **Nicht-Baum:** höchstens 5 %. Pixel mit mehr als 10 % Gebäudeanteil werden nicht verwendet. Ergebnis: 516.237 Pixel (302.502 Baum, 213.735 Nicht-Baum).

**Merkmale aus den Satellitenmosaiken (je Pixel):** EVI 2025; Mittel, Minimum, 25-%-Quantil und Standardabweichung des EVI über 2015–2025; NDVI 2025; NIR 2025; Feuchteindex NDMI 2025.

**Maß:** AUC (Wahrscheinlichkeit, dass ein Baum-Pixel einen höheren Wert hat als ein Nicht-Baum-Pixel; 0,5 = Zufall, 1 = perfekt). Die Kombination ist eine logistische Regression, angelernt auf der Hälfte der Kacheln und getestet auf der anderen Hälfte (räumlich getrennt).

### Ergebnis A: Baum gegen alles Nicht-Baum (inkl. Straßen, Dächer, Boden)
| Merkmal | AUC |
|---|---|
| EVI 2025 (unser bisheriger Layer) | 0,71 |
| NDVI 2025 | 0,89 |
| EVI Minimum 2015–2025 | 0,88 |
| NDMI 2025 | 0,86 |
| EVI Schwankung (Std) 2015–2025 | 0,78 |
| Kombination (Testkacheln) | 0,98 (Baum 93 % erkannt, Nicht-Baum 94 % korrekt) |

### Ergebnis B: Baum gegen Acker/Wiese (OSM), die schwierige Frage
Testkacheln: 148.940 Baum-Pixel, 37.822 Acker/Wiese-Pixel.

| Merkmal | AUC |
|---|---|
| EVI 2025 | 0,60 (kaum besser als Zufall) |
| EVI Mittel 2015–2025 | 0,61 |
| NDVI 2025 | 0,85 |
| EVI Minimum 2015–2025 | 0,85 |
| **EVI Schwankung (Std) 2015–2025** | **0,97** |
| Kombination | **0,99** (Baum 96 % erkannt, Acker/Wiese 97 % korrekt) |

Bild: `docs/baummaske/baummaske_test.png`. Gewichte der Kombination: `out/report/baummaske_test.json` (lokal).

## 4. Was daraus folgt
1. **Der EVI > 0,45 ist für Bäume ungeeignet.** Gegen Acker/Wiese trennt er kaum. Der **NDVI ist deutlich besser** (0,85 statt 0,60).
2. **Die Schwankung über die Jahre** trennt Baum und Acker/Wiese am besten (AUC 0,97): Ein Wald sieht jedes Jahr ähnlich aus, ein Feld wechselt mit der Fruchtfolge. Mit den Mosaiken, die wir schon haben, ist das ohne neue Satellitendaten berechenbar.
3. Die Kombination mehrerer Merkmale erreicht auf Testkacheln 96–97 % Treffsicherheit gegenüber Acker/Wiese.

## 5. Grenzen, die man kennen muss
- **Zirkelschluss bei Veränderungen:** Die Schwankung über die Jahre erkennt Bäume, weil sie stabil sind. Ein Pixel, das 2020 gefällt wurde, schwankt aber auch und fällt dann eher aus der Baummaske. Die Maske darf deshalb nicht aus allen elf Jahren abgeleitet werden, wenn man danach Baumverlust messen will. Sie muss aus einem Zeitraum **vor** der Veränderung kommen (z. B. 2015–2019), sonst wird gerade der Verlust ausgeblendet.
- **Referenzjahr 2025:** Das nDOM gibt es nur für 2025. Pixel, die bis dahin gefällt wurden, zählen als Nicht-Baum. Die Genauigkeit der Maske für frühere Jahre ist nicht gemessen. Prüfung an den historischen Luftbildern (2016, 2019) steht aus.
- **Stichprobe:** 80 von 212 Kacheln; die Hälfte zum Anlernen, die andere zum Testen. Benachbarte Kacheln sind sich ähnlich, die echte Genauigkeit kann niedriger liegen.
- **10 m:** Einzelbäume, Hecken und kleine Gehölze (< 600 m² bei 60 % Deckung) sind in dieser Auflösung nicht sichtbar.
- **Definition „Baum":** Höhe über 3 m laut nDOM, also auch Gebüsch und Masten. OSM-Gebäude sind nicht vollständig.
- **nDOM-Aufnahmezeitpunkt:** Frühjahr (laubfrei); wir haben das Aufnahmedatum nicht je Kachel geprüft.

## 6a. Umgesetzt: Baummaske je Zeitfenster und große Verlustflächen (`scripts/baummaske.py`, `scripts/verlust_gross_pruefen.py`, `scripts/publish_verlust_gross.py`)
- **Modell:** Logistische Regression (EVI-Minimum, EVI-Schwankung, EVI-Mittel, NDVI-Mittel, NDMI-Mittel je Fünf-Jahres-Fenster), angelernt auf Fenster 2021–2025 gegen die nDOM-Baummaske 2025, danach unverändert auf Fenster 2015–2019 angewendet. Auf Testkacheln: 95 % der Baum- und 94 % der Nicht-Baum-Pixel richtig (Schwelle 0,69).
- **Kalibrierung:** Die Schwelle für 2015–2019 wurde auf 0,577 gesenkt, damit dort derselbe Anteil der OSM-Waldpixel erkannt wird wie 2021–2025 (96,5 %). Ohne Kalibrierung lag die erkannte Baumfläche im früheren Fenster systematisch niedriger.
- **Ergebnis:** Verlust rund 5,5 km², Zuwachs rund 10 km², Baumfläche rund 70 bzw. 75 km² von rund 168 km². Der Zuwachs ist nach Sichtprüfung größtenteils falsch (0 von 9 Flächen überzeugend), die kleinen Verluste ebenfalls häufig. **Diese Bilanz ist nicht verwendbar.**
- **Sichtprüfung auf Luftbildern 2016/2023** (Geobasis NRW): 10 zufällige Verlustflächen: 4 eindeutig abgeräumter Nadelwald, 1 wahrscheinlich, 5 unklar; die drei größten (> 2 ha) eindeutig.
- **Veröffentlicht:** Nur Verlustflächen ≥ 1 ha (73 Stück, 1,9 km²), jede einzeln auf den Luftbildern angesehen (`docs/baummaske/gross_1..3.png`): 58 sehen nach abgeräumtem Nadelwald aus, 15 sind unsicher (5 Feld/Wiese, 4 Steinbruch, 3 Seeufer, 3 Gewerbe/Bahn/Bebauung). Die Einordnung ist eine Sichtprüfung durch den Bearbeiter, nicht unabhängig bestätigt. Attribut `pruefung` im GeoJSON. Die Ursache der Verluste (Sturm, Käfer, Einschlag) ist unbekannt.
- **Nicht veröffentlicht:** Baumkarten je Fenster, Zuwachs und kleine Verluste (siehe Grenzen).

## 6. Nächste Schritte
1. Baummaske aus 2015–2019 (Schwankung, NDVI, NDMI), angelernt an der nDOM-Referenz, auf die Luftbilder 2016 und 2019 prüfen.
2. Veränderung 2015 → 2025 nur innerhalb der Baummaske neu berechnen und wieder mit Luftbildern kontrollieren.
3. Ergebnis als Karten veröffentlichen, mit denselben Quellenangaben wie die anderen Layer.

## 7. Quellen
- Sentinel-2 L2A, Microsoft Planetary Computer: <https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a>
- nDOM / DOM / DGM1 NRW (Geobasis NRW, dl-de/zero-2-0): <https://www.opengeodata.nrw.de/produkte/geobasis/hm/>
- OpenStreetMap (ODbL): <https://www.openstreetmap.org/copyright>
- EVI: Huete et al. 2002, <https://doi.org/10.1016/S0034-4257(02)00096-2>
- Historische Luftbilder: <https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?REQUEST=GetCapabilities&SERVICE=WMS>

## 8. Neu erzeugen
```
python scripts/schwelle_osm.py                 # Schritt 1 (OSM-Referenz)
python scripts/ndom_select.py                  # nDOM-Kacheln laden (1,3 GB)
python scripts/osm_buildings.py                # Gebäude aus OSM
python scripts/baummaske_test.py               # Schritt 2 (Auswertung)
```
