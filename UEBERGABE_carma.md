# Übergabe: Was wir über das carma-Geoportal gelernt haben (Stand 2026-11-12)
Für das carmawiki bzw. für jeden, der Style-JSON in den Digital Twin Wuppertal (https://digital-twin-wuppertal-live.github.io/geoportal/#/) laden will. Alles hier wurde im Portal ausprobiert, sofern nicht als „nicht getestet“ markiert. Hintergrund: Projekt `wuppertal-vegetation-sentinel2` (README).

## Style-JSON per Drag & Drop
- Ein MapLibre-Style (Version 8) mit `metadata.carmaConf.layerInfo` (`title`, `description`, `keywords`, `tags`) und `metadata.carmaConf.instant: true` lässt sich als URL ins Portal ziehen. GeoJSON-Quellen (`"type":"geojson","data":<URL>`) funktionieren; Raster-WMS mit `{bbox-epsg-3857}` im Tile-URL ebenfalls.
- Die URL muss öffentlich und per CORS erreichbar sein (GitHub Pages geht). Direkt nach dem Push ist sie oft 404, der Pages-Build dauert 3 bis 6 Minuten. Große Dateien (27 MB PDF im docs-Ordner) ließen den Deploy ins Timeout laufen („syncing_files“, Build „failure“); 14 MB gingen.
- Das Portal merkt sich geladene Layer (IndexedDB `carma-layer-catalog`, `localforage`, localStorage). Beim Testen einer geänderten Datei einen Query-Parameter an die Style-URL hängen oder den Speicher leeren, sonst sieht man den alten Stand.

## Infobox für GeoJSON-Layer (wichtig)
Ohne Konfiguration zeigt ein Klick „Zu diesem Objekt sind keine weiteren Sachdaten verfügbar“, die Properties erscheinen nicht von selbst. Lösung (im Bundle gefunden, im Portal getestet): in `metadata.carmaConf.layerInfo.keywords` Zeilen der Form
`carmaconf://infoBoxMapping:<feld>: <JS-Ausdruck>` eintragen, `p` = Properties des Objekts. Felder: `header`, `title`, `subtitle`, `additionalInfo`. Beispiel:
```
"keywords": [
 "carmaconf://infoBoxMapping:header: \"Baumverlust bestätigt, Nr. \" + p[\"Nr\"]",
 "carmaconf://infoBoxMapping:title: \"Fläche: \" + String(p[\"Fläche (ha)\"]).replace(\".\", \",\") + \" Hektar\"",
 "carmaconf://infoBoxMapping:subtitle: \"Ursache: \" + p[\"Ursache\"]"]
```
- Der Präfix muss **klein** `carmaconf://` geschrieben sein (`carmaConf://` wird ohne Fehlermeldung ignoriert), danach exakt `infoBoxMapping:`.
- Die Ausdrücke laufen in einem sandboxed iframe mit `eval`, volles JavaScript, aber ohne Zugriff auf die Seite. Zeilen mit dem Wort `function` werden als Funktionskörper behandelt.
- Property-Namen mit Umlauten und Leerzeichen (`Fläche (ha)`) funktionieren in GeoJSON.

## Filter-Buttons (Zeitreihe)
`metadata.carmaConf.filterConfig` mit `layerPattern`, `filterMode` (and/or) und Buttons mit `propertyValue` als String. Ein TimeSlider ist nur über hartkodierte Workflow-Konfiguration möglich, nicht über gezogene Styles (nicht weiter verfolgt).

## Historische Luftbilder (Geobasis NRW, dl-de/zero-2-0)
- WMS `https://www.wms.nrw.de/geobasis/wms_nw_hist_dop`, Ebenen `nw_hist_dop_JAHR`. Für Wuppertal gibt es nur 2010, 2013, 2016, 2019, 2021, 2023. 2019 ist ein Winterbild (Februar), 2023 ein Frühjahrsbild.
- Aktuelles DOP: `wms_nw_dop`, Ebene `nw_dop_rgb` (10 cm), Bildflugdaten über `nw_dop_utm_info` und GetFeatureInfo. iDOP: `wms_nw_idop`, `nw_idop_rgb`, Aufnahme 20.09.2024.
- In EPSG:25832 ist die BBOX-Reihenfolge Rechtswert, Hochwert.

## Daten und Overpass
- Overpass-API braucht einen User-Agent und Wiederholungen (406 ohne UA, 502 gelegentlich).
- nDOM50 (Baumhöhen, 0,5 m, Geobasis NRW) gibt es nur für das Jahr 2025, keine historischen Höhenmodelle; Kacheln 1 km, rund 15 MB je Kachel.

## Inhaltliche Erkenntnisse (Methode)
- EVI trennt Bäume nicht von Acker/Wiese (AUC 0,60); Jahresschwankung, NDVI und NDMI trennen deutlich besser (AUC 0,99 gegen nDOM). Verlust ab 1 ha: 73 Kandidaten, von Hand bestätigt 51 (144,5 ha). Zuwachs ab 1 ha: 58 Kandidaten, bestätigt 5 (7,2 ha, Trefferquote 9 %). Keine Gesamtbilanz des Baumbestands.
- Veröffentlichte Layer, Skripte und Methodik: siehe README und `METHODIK_Baummaske.md` im Repo.

## Nicht getestet
Ein echtes Drag & Drop mit der Maus (alle Tests dort mit simuliertem Drop-Ereignis); der Zuwachs-Layer im Portal (nicht veröffentlicht).
