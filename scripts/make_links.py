"""Schreibt die ausgeschriebenen Style-JSON-Links ins README und erzeugt docs/index.html (Links zum Ziehen)."""
import os, re
BASE = "https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/"
names = sorted(f for f in os.listdir("docs/styles") if f.endswith(".json"))
def label(n):
    if n.startswith("baumverlust_final"): return "Baumverlust bestätigt (51 Flächen, 144,5 ha, von Hand an Luftbildern 2016/2025 geprüft; Infobox mit Fläche in ha)"
    if n.startswith("baumverlust"): return "Baumverlust über 1 ha (73 Flächen, Sichtprüfung: rot wahrscheinlich, orange unsicher)"
    if n.startswith("luftbild_"): return "Luftbild " + n.split("_")[1].split(".")[0] + " (Geobasis NRW)"
    if n.startswith("vegetation_zeitreihe_or"): return "Zeitreihe 2015–2025, Test: Mehrfachauswahl (OR)"
    if n.startswith("vegetation_zeitreihe"): return "Zeitreihe 2015–2025 mit Jahres-Buttons"
    if n.startswith("vegetation_"): return "Vegetation " + n.split("_")[1].split(".")[0]
    if n.startswith("aenderung_"): a, b = n.split("_")[1], n.split("_")[2].split(".")[0]; return f"Veränderung {a} → {b} (Verlust rot, Zuwachs blau)"
    return "Geländeschummerung (DGM1)"
groups = [("Baumverlust (große Flächen, Luftbild-geprüft)", [n for n in names if n.startswith("baumverlust")]),
          ("Zeitreihe mit Filter-Buttons (eine Datei, 11 Jahre)", [n for n in names if n.startswith("vegetation_zeitreihe")]),
          ("Vegetation je Jahr", [n for n in names if n.startswith("vegetation_2")]),
          ("Veränderung", [n for n in names if n.startswith("aenderung_")]),
          ("Untergrund", [n for n in names if n.startswith("schummerung")]),
          ("Historische Luftbilder (Jahrgänge für Wuppertal)", [n for n in names if n.startswith("luftbild_")])]

PDF = "https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/Methodik_Vegetation_Wuppertal_2015_2016.pdf"
ERK = "https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/erklaerung/"
LOG = "https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/logbuch/Logbuch_Baumverlust.pdf"
BAUM = "https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/baummaske/"
md = "## Methodik\n[Verständliche Erklärung in Bildern (für Laien, mit Prüfbeispielen)](" + ERK + ")\n\n[Wie finden wir Bäume im Satellitenbild? Schritt für Schritt (für Laien)](" + BAUM + ")\n\n[Test: Welche Satellitengröße trennt Bäume? (NDVI, Jahresschwankung, nDOM-Referenz)](METHODIK_Baummaske.md)\n\n[Logbuch Baumverlust als PDF (51 bestätigte Flächen, Foto von 2016 und von 2025 nebeneinander, 27 MB)](" + LOG + ")\n\n[Methodik als PDF (Workflow am Beispiel 2015 und 2016)](" + PDF + ")\n\n## Einbinden\nLink auf das Portalfenster ziehen (https://digital-twin-wuppertal-live.github.io/geoportal/#/) oder die URL kopieren.\n\n"
for g, ns in groups:
    md += f"**{g}**\n\n" + "".join(f"- [{label(n)}]({BASE}{n}) \n  `{BASE}{n}`\n" for n in ns) + "\n"
r = open("README.md").read()
r = re.sub(r"## (Methodik\n.*?## )?Einbinden\n.*?(?=\n## Methode)", md.rstrip() + "\n", r, flags=re.S)
open("README.md", "w").write(r)

html = """<!doctype html><meta charset=utf-8><title>Vegetation Wuppertal – Sentinel-2</title>
<style>body{font:16px system-ui;max-width:48em;margin:2em auto;padding:0 1em}li{margin:.5em 0}code{font-size:.8em;color:#555;word-break:break-all}</style>
<h1>Vegetation Wuppertal 2015–2025</h1>
<p>Link auf das <a href="https://digital-twin-wuppertal-live.github.io/geoportal/#/">Geoportal</a>-Fenster ziehen oder die URL kopieren. <b>Neu:</b> <a href="{ERK}">Verständliche Erklärung in Bildern</a> (was die Karten zeigen und was nicht) und <a href="{BAUM}">Wie finden wir Bäume im Satellitenbild?</a> (Schritt für Schritt). <b>Logbuch:</b> <a href="{LOG}">Baumverlust 2016 und 2025 (PDF)</a>. Methodik: <a href="{PDF}">PDF (Workflow 2015/2016)</a>. Methode und Grenzen: <a href="https://github.com/benjamin-bleske/wuppertal-vegetation-sentinel2#readme">README</a>.</p>
"""
for g, ns in groups:
    html += f"<h2>{g}</h2><ul>" + "".join(f'<li><a href="{BASE}{n}">{label(n)}</a><br><code>{BASE}{n}</code></li>' for n in ns) + "</ul>"
html = html.replace("{PDF}", PDF).replace("{ERK}", ERK).replace("{BAUM}", BAUM).replace("{LOG}", LOG)
open("docs/index.html", "w").write(html)
print(md[:600])
