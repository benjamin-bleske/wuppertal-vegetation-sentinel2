# Prüf-Tool Baumzuwachs (Wuppertal)
Gleiche Bedienung wie `tools/pruef_tool/ANLEITUNG.md`, aber für 58 Zuwachs-Kandidaten ab 1 ha (Baum 2021–2025, kein Baum 2015–2019 laut Sentinel-2).
1. `cd tools/pruef_tool_zuwachs && python3 -m http.server 8766`, dann http://localhost:8766/index.html öffnen.
2. Links Luftbild 2016, rechts 2025. Ja (J) = Baumzuwachs, Nein (N), Unsicher (U). Auf Beschriftung des Bildes achten: ein Sommerbild links und rechts vergleichen.
3. „Entscheidungen exportieren“ liefert `entscheidungen.json`. Daraus: `.venv/bin/python scripts/logbuch_zuwachs.py entscheidungen.json` (finaler Layer und Logbuch-PDF).
Der Zuwachs wurde früher nach Stichprobe als unzuverlässig eingestuft (0 von 9 überzeugend); dies ist die Prüfung mit Luftbildern dazu.
