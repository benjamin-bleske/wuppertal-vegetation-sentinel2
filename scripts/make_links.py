"""Schreibt die ausgeschriebenen Style-JSON-Links ins README und erzeugt docs/index.html (Links zum Ziehen)."""
import os, re
BASE = "https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/styles/"
names = sorted(f for f in os.listdir("docs/styles") if f.endswith(".json"))
def label(n):
    if n.startswith("vegetation_"): return "Vegetation " + n.split("_")[1].split(".")[0]
    if n.startswith("aenderung_"): a, b = n.split("_")[1], n.split("_")[2].split(".")[0]; return f"Veränderung {a} → {b} (Verlust rot, Zuwachs blau)"
    return "Geländeschummerung (DGM1)"
groups = [("Vegetation je Jahr", [n for n in names if n.startswith("vegetation_")]),
          ("Veränderung", [n for n in names if n.startswith("aenderung_")]),
          ("Untergrund", [n for n in names if n.startswith("schummerung")])]

md = "## Einbinden\nLink auf das Portalfenster ziehen (https://digital-twin-wuppertal-live.github.io/geoportal/#/) oder die URL kopieren.\n\n"
for g, ns in groups:
    md += f"**{g}**\n\n" + "".join(f"- [{label(n)}]({BASE}{n}) \n  `{BASE}{n}`\n" for n in ns) + "\n"
r = open("README.md").read()
r = re.sub(r"## Einbinden\n.*?(?=\n## Methode)", md.rstrip() + "\n", r, flags=re.S)
open("README.md", "w").write(r)

html = """<!doctype html><meta charset=utf-8><title>Vegetation Wuppertal – Sentinel-2</title>
<style>body{font:16px system-ui;max-width:48em;margin:2em auto;padding:0 1em}li{margin:.5em 0}code{font-size:.8em;color:#555;word-break:break-all}</style>
<h1>Vegetation Wuppertal 2015–2025</h1>
<p>Link auf das <a href="https://digital-twin-wuppertal-live.github.io/geoportal/#/">Geoportal</a>-Fenster ziehen oder die URL kopieren. Methode und Grenzen: <a href="https://github.com/benjamin-bleske/wuppertal-vegetation-sentinel2#readme">README</a>.</p>
"""
for g, ns in groups:
    html += f"<h2>{g}</h2><ul>" + "".join(f'<li><a href="{BASE}{n}">{label(n)}</a><br><code>{BASE}{n}</code></li>' for n in ns) + "</ul>"
open("docs/index.html", "w").write(html)
print(md[:600])
