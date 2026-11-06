"""Methoden-PDF: Workflow am Beispiel 2015 und 2016."""
import json, os, matplotlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

fd = os.path.join(matplotlib.get_data_path(), "fonts/ttf/")
pdfmetrics.registerFont(TTFont("DV", fd + "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("DV-B", fd + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I", fd + "DejaVuSans-Oblique.ttf")); pdfmetrics.registerFont(TTFont("DVM", fd + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-B")

st = json.load(open("out/report/stats.json"))
G = colors.HexColor("#2E7D32")
body = ParagraphStyle("b", fontName="DV", fontSize=9, leading=13.2, spaceAfter=5)
h1 = ParagraphStyle("h1", keepWithNext=1, fontName="DV-B", fontSize=13, leading=17, textColor=G, spaceBefore=10, spaceAfter=5)
title = ParagraphStyle("t", fontName="DV-B", fontSize=20, leading=25, textColor=G, spaceAfter=4)
sub = ParagraphStyle("s", fontName="DV", fontSize=10, leading=14, textColor=colors.HexColor("#555555"), spaceAfter=10)
cap = ParagraphStyle("c", fontName="DV-I", fontSize=7.5, leading=10, textColor=colors.HexColor("#555555"), spaceAfter=8)
code = ParagraphStyle("k", fontName="DVM", fontSize=7.8, leading=10.5, backColor=colors.HexColor("#F3F3F3"), borderPadding=4, spaceAfter=8)
box = ParagraphStyle("x", parent=body, backColor=colors.HexColor("#FFF8E1"), borderColor=colors.HexColor("#F9A825"), borderWidth=.6, borderPadding=6, spaceBefore=4, spaceAfter=10)
cell = ParagraphStyle("cell", fontName="DV", fontSize=8, leading=10.5)
cellb = ParagraphStyle("cellb", parent=cell, fontName="DV-B")

def d(i):
    x = i.split('_')[2][:8]; return f'{x[6:]}.{x[4:6]}.{x[:4]}'
def P(t, s=body): return Paragraph(t, s)
def img(name, w=16.4):
    p = f"out/report/{name}"; iw, ih = PILImage.open(p).size
    return Image(p, width=w * cm, height=w * cm * ih / iw)
def fig(name, caption, w=16.4): return KeepTogether([img(name, w), P(caption, cap)])
def tbl(rows, widths, head=True):
    t = Table([[P(str(c), cellb if (head and i == 0) else cell) for c in r] for i, r in enumerate(rows)], colWidths=[x * cm for x in widths])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#BBBBBB")), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8F5E9")),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t

o15, o16 = st["options"]["2015"], st["options"]["2016"]; ch = st["change"]
S = []
S += [P("Vegetation Wuppertal aus Sentinel-2", title), P("Methodisches Vorgehen, exemplarisch für die Sommer 2015 und 2016", sub)]
S += [P("Dieses Dokument zeigt den Workflow, mit dem aus Sentinel-2-Satellitenbildern die Vegetationsflächen für den Digital Twin Wuppertal entstehen. "
        "Die acht Schritte sind für 2015 und 2016 durchgespielt, alle Abbildungen stammen aus den echten Daten. Dieselben Schritte laufen für alle Jahre 2015 bis 2025; "
        "Skripte und Ergebnisse liegen im Repository <b>github.com/benjamin-bleske/wuppertal-vegetation-sentinel2</b>."),
      img("workflow.png", 16.4),
      P("Kurzfassung: Aus allen wolkenfreien Beobachtungen eines Sommers (25. Juli bis 15. September) wird pro Pixel der Median gebildet. Daraus berechnet "
        "der Enhanced Vegetation Index (EVI) die Dichte des Blätterdachs. Pixel mit EVI &gt; 0,45 gelten als dichte Vegetation, werden zu Polygonen umgewandelt, "
        "zwischen den Jahren verglichen und als GeoJSON mit Style-JSON veröffentlicht.", body)]

S += [P("1 Datengrundlage und Szenensuche", h1),
      P("Sentinel-2 (Copernicus) liefert alle 5 bis 10 Tage Aufnahmen mit 10 m Pixelgröße in 13 Spektralbändern. Genutzt wird das Produkt <b>L2A</b> (atmosphärisch korrigiert, "
        "Oberflächenreflektanz) über die Planetary-Computer-Schnittstelle (STAC), ohne Konto. Wuppertal liegt an der Grenze der UTM-Zonen 31 und 32; deshalb werden die Kacheln 32ULB, 31UGT und 31UGS "
        "zusammen verwendet und auf ein gemeinsames Raster (EPSG:25832, 10 m) umgerechnet."),
      tbl([["", "2015", "2016"], ["Suchfenster", "25.07.–15.09.", "25.07.–15.09."], ["Gefundene Aufnahmen (alle Kacheln, &lt; 80 % Wolken)", "33", "25"],
           ["Erfolgreich verarbeitet (mit Stadtanteil)", "23", "19"], ["Sensor", "nur Sentinel-2A", "nur Sentinel-2A"], ["Mittlere klare Beobachtungen je Pixel (Median)", "8", "12"]], [8.2, 4, 4]),
      Spacer(1, 6),
      fig("verfuegbarkeit.png", "Abb. 1: Aufnahmen der Kachel 32ULB im Suchfenster und ihre Wolkenbedeckung. Grün: unter 40 %, gelb: 40 bis 80 %, rot: über 80 %."),
      P("<b>Besonderheit 2015:</b> Die Mission startete im Juni 2015; über Wuppertal liegen erst ab 30. Juli Daten vor, und es fliegt nur ein Satellit (2A). Die Archivdaten dieses Jahres sind von der ESA rückwirkend "
        "neu prozessiert worden (Baseline 02.12). Wegen des späten Starts gilt das Fenster 25.07.–15.09. für alle Jahre, damit Laub mit Laub verglichen wird.", box)]

S += [P("2 Wolkenmaske mit der Szenenklassifikation (SCL)", h1),
      P("Jede L2A-Aufnahme enthält eine Szenenklassifikation (SCL) mit 12 Klassen. Gültig sind die Klassen 2 (dunkle Flächen), 4 (Vegetation), 5 (unbewachsen), 6 (Wasser) und 7 (unklassifiziert). "
        "Verworfen werden Wolkenschatten (3), Wolken (8, 9), Zirren (10), Schnee (11), gesättigte Pixel (1) und Pixel ohne Wert. Die verworfene Fläche wird um 2 Pixel (20 m) aufgeweitet, "
        "weil Wolkenränder und Dunst die Klassifikation unscharf machen."),
      fig("scl.png", f"Abb. 2: Wolkenmaske an je einer Beispielszene. 2015: {d(st['scl']['2015'][0])} (Kachelwolken {st['scl']['2015'][1]:.0f} %), 2016: {d(st['scl']['2016'][0])} ({st['scl']['2016'][1]:.0f} %). "
          "Links Echtfarben, Mitte SCL, rechts gültige (grün) und verworfene (rot) Pixel.", 15.6)]

S += [P("Fehler und Korrektur: SCL-Klasse 2", h1),
      P("Zunächst wurde Klasse 2 („dunkle Flächen“) mit verworfen. Das erzeugte im ersten 2015-Mosaik Lücken von <b>4,8 %</b> der Stadtfläche, vor allem in der dicht bebauten Talachse. "
        "Die ältere Prozessierung (Baseline 02.xx) stuft dort Dächer, Straßen und Schatten als „dunkel“ ein, die neuere (05.xx) kaum. Der Fehler war also nicht gleichmäßig über die Jahre verteilt und hätte "
        "den Vergleich verzerrt (2025: nur 0,02 %). Seit Klasse 2 gültig ist, liegen die Lücken bei <b>0,06 %</b> (2015)."),
      fig("luecken.png", "Abb. 3: Lücken im 2015-Mosaik (weniger als 2 klare Beobachtungen) vor und nach der Korrektur; rechts die Zahl klarer Beobachtungen je Pixel. Der Norden hat mehr Beobachtungen, weil dort zwei Orbits überlappen.", 16.4)]

S += [P("3 Median-Mosaik", h1),
      P("Für jedes Pixel werden alle gültigen Beobachtungen des Fensters genommen und der <b>Median</b> je Spektralband gebildet (B02 Blau, B03 Grün, B04 Rot, B08 Nahinfrarot, B11 Kurzwelleninfrarot). "
        "Der Median unterdrückt Restwolken, Schatten und Ausreißer besser als ein Mittelwert. Pixel mit weniger als zwei gültigen Beobachtungen bleiben leer. Bei neueren Prozessierungs-Baselines (ab 04.00) "
        "wird der Reflektanz-Offset von −1000 vor der Umrechnung (÷ 10 000) berücksichtigt."),
      fig("mosaik.png", "Abb. 4: Median-Mosaike 2015 und 2016 in Echtfarben (links) und die Zahl klarer Beobachtungen je Pixel (rechts).", 15.6)]

S += [P("4 Vegetationsindex: Auswahl und Berechnung", h1),
      P("Gesunde Blätter absorbieren rotes Licht und reflektieren Nahinfrarot stark. Daraus lassen sich Indizes bilden. Drei Varianten wurden verglichen:"),
      tbl([["Option", "Formel", "Zeigt", f"2015", "2016"],
           ["A: NDVI &gt; 0,65", "(NIR − Rot) / (NIR + Rot)", "wie grün; sättigt bei dichtem Laub", f"{o15[0]:.1f} %", f"{o16[0]:.1f} %"],
           ["<b>B: EVI &gt; 0,45</b> (gewählt)", "2,5 · (NIR − Rot) / (NIR + 6·Rot − 7,5·Blau + 1)", "Dichte des Blätterdachs; Blau-Band korrigiert Dunst und Untergrund", f"{o15[1]:.1f} %", f"{o16[1]:.1f} %"],
           ["C: NDVI + NDMI + Textur", "NDMI = (NIR − SWIR) / (NIR + SWIR); NIR-Textur 3×3", "Näherung für Gehölz; Schwelle je Jahr als Perzentil, daher nicht streng vergleichbar", f"{o15[2]:.1f} %", f"{o16[2]:.1f} %"]],
          [3.4, 5.3, 5.0, 1.4, 1.4]),
      Spacer(1, 4), fig("optionen.png", "Abb. 5: Die drei Optionen am Mosaik 2015 (grün = Vegetation).", 15.6),
      P("Gewählt wurde <b>EVI</b>: weniger sättigungsanfällig als NDVI und über die Jahre besser vergleichbar als Option C. "
        "NIR, Rot und Blau entsprechen den Bändern B08, B04 und B02; SWIR dem Band B11."),
      fig("evi.png", "Abb. 6: EVI-Karte und Häufigkeitsverteilung für 2015 und 2016 mit der Schwelle 0,45 (rot gestrichelt).", 15.6)]

vec_txt = f"Die Gesamtfläche ändert sich dadurch kaum ({st['vector'][0]:,} auf {st['vector'][1]:,} Pixel in 2015), die Ränder werden ruhiger. ".replace(",", ".")
S += [P("5 Schwelle und Filter, 6 Vektorisierung", h1),
      P("Die Vegetationsmaske ist <b>EVI &gt; 0,45</b>. Ein 3×3-Medianfilter entfernt Einzelpixel-Rauschen, Flächen unter 4 Pixeln (400 m²) werden gelöscht. " + vec_txt +
        "Die Maske wird mit <font name='DVM'>rasterio.features.shapes</font> in Polygone umgewandelt, auf 5 m vereinfacht, nach EPSG:4326 (WGS 84) umgerechnet und mit 6 Nachkommastellen als GeoJSON gespeichert. "
        "Ergebnis: je Jahr etwa 2 000 bis 2 500 Polygone, rund 3 MB."),
      fig("vektor.png", "Abb. 7: Ausschnitt um die Elberfelder Innenstadt (3 × 3 km), 2015. Von links: rohe Schwelle, nach Filter, vektorisierte Polygone.", 16.4)]

S += [P("7 Vergleich der Jahre am Beispiel 2015 → 2016", h1),
      P("Der Änderungslayer vergleicht die beiden Vegetationsmasken, aber nur an Pixeln, die in <b>beiden</b> Jahren gültig beobachtet wurden. "
        "Daraus entstehen zwei Klassen: <b>Verlust</b> (Vegetation 2015, nicht 2016) und <b>Zuwachs</b> (neu 2016)."),
      tbl([["Klasse", "Fläche"], ["Stabile Vegetation", f"{ch['stable']:.1f} km²"], ["Verlust 2015 → 2016", f"{ch['loss']:.1f} km²"], ["Zuwachs 2015 → 2016", f"{ch['gain']:.1f} km²"],
           ["Anteil Vegetation an der Stadtfläche", f"{ch['share'][0]:.1f} % → {ch['share'][1]:.1f} %"]], [8, 4]),
      Spacer(1, 4), fig("aenderung.png", "Abb. 8: Veränderung der dichten Vegetation 2015 → 2016 (Stadtgrenze Wuppertal).", 11.2),
      P("<b>Wie das Ergebnis zu lesen ist:</b> Große eckige Flächen sind meist Ackerland, dessen Bewuchs je nach Fruchtfolge und Erntetermin wechselt; schmale Streifen an Straßen und Waldrändern sind Randeffekte. "
        "Ein Unterschied zwischen zwei Jahren ist daher noch kein Beleg für Baumverlust.", box)]

S += [P("8 Veröffentlichung", h1),
      P("Für jedes Jahr und jede Differenz gibt es eine <b>Style-JSON</b> (MapLibre, Version 8) mit <font name='DVM'>metadata.carmaConf.layerInfo</font> (Titel, Beschreibung, Quellenhinweis) und einer GeoJSON-Quelle als URL. "
        "Die Dateien liegen im Ordner <font name='DVM'>docs/</font> und werden über GitHub Pages ausgeliefert (CORS offen). Im Portal wird die Style-URL per Drag &amp; Drop auf das Fenster gezogen. "
        "Eine Startseite mit allen Links steht unter <b>benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/</b>."),
      P("Die Geländeschummerung (DGM1 NRW, mehrere Beleuchtungsrichtungen) ist als eigene Raster-Style-JSON beigelegt.")]

S += [P("Qualitätssicherung und Grenzen", h1),
      tbl([["Punkt", "Maßnahme / Einschränkung"],
           ["Auflösung", "10 m: dichte Vegetation insgesamt (Bäume und dichte Wiesen), keine Einzelbäume."],
           ["Witterung", "Feste Schwellen hängen vom Wetter der Aufnahmewochen ab (z. B. Dürresommer 2018 und 2020); 2015 nur ein Satellit."],
           ["Gültigkeit", "Differenzen nur auf Pixeln, die in beiden Jahren beobachtet wurden; Lücken in den Mosaiken unter 0,1 %."],
           ["Szenen-Download", "Zugriffs-Links verfallen bei langen Läufen (HTTP 403); je Versuch wird neu signiert."],
           ["Nächster Schritt", "Auswertung auf Wald und Gehölze beschränken (OSM-Wald oder Baumkataster), um Ackerland auszuschließen."]], [3.4, 13])]

S += [P("Quellen und Lizenzen", h1),
      P("Copernicus Sentinel-2 L2A, bereitgestellt über Microsoft Planetary Computer (Copernicus-Datenlizenz). Stadtgrenze © OpenStreetMap contributors (ODbL 1.0). "
        "Geländedaten DGM1 © Geobasis NRW (dl-de/zero-2-0). Skripte: <font name='DVM'>search_scenes.py, composite.py, options.py, vectorize.py, build_styles.py</font> im Ordner <font name='DVM'>scripts/</font>.")]

def footer(c, d):
    c.setFont("DV", 7); c.setFillColor(colors.HexColor("#888888"))
    c.drawString(2 * cm, 1.1 * cm, "Vegetation Wuppertal aus Sentinel-2 – Methodik"); c.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Seite {d.page}")

doc = SimpleDocTemplate("out/Methodik_Vegetation_Wuppertal_2015_2016.pdf", pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                        title="Vegetation Wuppertal aus Sentinel-2 – Methodik", author="Benjamin Bleske")
doc.build(S, onFirstPage=footer, onLaterPages=footer)
print("ok")
