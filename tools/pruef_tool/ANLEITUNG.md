# Anleitung: Baumverlust prüfen und Logbuch erstellen

## Worum geht es?
Das Programm hat 73 Flächen gefunden, auf denen Bäume verschwunden sein könnten. Sie schauen sich jede Fläche auf zwei Luftbildern an (2016 und 2025) und entscheiden: Ja, Nein oder Unsicher. Aus Ihren "Ja" entstehen eine Karten-Ebene und ein Logbuch als PDF.

## Schritt 1: Prüf-Tool öffnen
- Einfach: Im Ordner `tools/pruef_tool/` die Datei `index.html` doppelt anklicken (am besten mit Chrome).
- Alternativ im Terminal: `cd tools/pruef_tool` und `python3 -m http.server 8000`, dann im Browser `http://localhost:8000` öffnen. Beenden mit Strg+C.
- Sie brauchen Internet, weil die Luftbilder live von Geobasis NRW geladen werden.

## Schritt 2: Entscheiden
- Links steht das Bild von früher (2016), rechts das von heute (2025). Der gelbe Umriss zeigt die Fläche.
- **Ja** = früher dichter, dunkler Wald, heute kahle Fläche. **Nein** = schon früher kein Wald (Feld, Wiese, Steinbruch, Gebäude, Wasser) oder heute noch Wald. **Unsicher** = Sie wissen es nicht, Fläche bleibt für später.
- Tasten: `J` Ja, `N` Nein, `U` Unsicher, Pfeil links/rechts blättern, `O` Umriss an/aus, `+`/`-` Ausschnitt. Beim Schreiben einer Notiz gelten die Tasten nicht.
- Oben können Sie andere Jahre wählen (2010, 2013, 2019, 2021) und mit "Näher heran" / "Mehr Umgebung" den Ausschnitt ändern.
- Der Vorschlag des Assistenten ist nur eine Orientierung und nicht bestätigt.
- Das Bild 2025 ist ein aktuelles Sommerbild (Bildflug meist Juni 2025). Die Zwischenjahre 2019 und 2023 sind Winter- bzw. Frühjahrsbilder mit kahlen Laubbäumen, zusätzlich wählbar sind 2024 (September) und andere Jahre. Die Bildjahre passen nicht genau zu den Satelliten-Zeiträumen.
- Ihre Eingaben werden automatisch in Ihrem Browser gespeichert. Sie bleiben beim Schließen erhalten, aber nur in diesem Browser auf diesem Rechner (und getrennt, je nachdem ob Sie die Datei per Doppelklick oder über `localhost` öffnen). Exportieren Sie deshalb regelmäßig.

## Schritt 3: Exportieren
Klicken Sie "Entscheidungen exportieren". Die Datei `entscheidungen.json` landet im Download-Ordner. Legen Sie sie nach `tools/pruef_tool/entscheidungen.json`. (Mit "Entscheidungen importieren" lesen Sie so eine Datei wieder ein.) Optional gibt "Finalen Layer herunterladen" direkt ein GeoJSON nur mit den "Ja"-Flächen.

## Schritt 4: Skript starten
Im Terminal im Projektordner:

    .venv/bin/python scripts/logbuch.py tools/pruef_tool/entscheidungen.json

Das Skript lädt die Luftbilder (Zwischenspeicher: `data/logbuch_cache/`), das dauert einige Minuten. Es kommt heraus:
- `out/geojson/baumverlust_final.geojson` – nur die "Ja"-Flächen (Nr., Größe in ha, Ursache, Notiz)
- `out/styles/baumverlust_final.style.json` – Darstellung und Beschreibung mit Quellenlinks
- `out/Logbuch_Baumverlust.pdf` – Titelseite mit Zahlen, Methode und Grenzen, Übersichtstabelle, dann je bestätigter Fläche eine Seite mit Bild früher und heute

Wo ein Jahr kein Bild liefert, steht im PDF "kein Bild verfügbar".

## Schritt 5: Veröffentlichen (bewusst ein eigener Schritt)
Das Skript veröffentlicht nichts. Die "Ja"-Flächen wären erst nach der Veröffentlichung in `docs/` und über GitHub Pages erreichbar. Wenn Sie so weit sind (erst PDF und Layer prüfen!):
1. `out/geojson/baumverlust_final.geojson` nach `docs/geojson/` kopieren und `out/styles/baumverlust_final.style.json` dorthin, wo die anderen Styles in `docs/` liegen (gleiche Stelle wie `baumverlust_ueber_1ha.style.json`).
2. Die Änderungen committen und pushen.
3. Nach kurzer Zeit ist der Layer über GitHub Pages erreichbar; die Adresse steht im Style (`data`).
Machen Sie das erst, wenn Sie bewusst entschieden haben, die Daten öffentlich zu zeigen.

## Hinweise
- Die Bestätigung ist eine Sichtprüfung, keine Geländeprüfung, und keine Gesamtbilanz des Baumbestands.
- Die Daten im Tool (`daten.js`) kommen aus `scripts/build_pruef_daten.py`; nur neu erzeugen, wenn sich die 73 Flächen ändern (Nummern ändern sich dann möglicherweise!).
