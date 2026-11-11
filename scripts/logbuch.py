"""Finaler Layer und Logbuch-PDF aus den im Pruef-Tool exportierten Entscheidungen.
Aufruf (im Projektordner): .venv/bin/python scripts/logbuch.py tools/pruef_tool/entscheidungen.json
Erzeugt: out/geojson/baumverlust_final.geojson, out/styles/baumverlust_final.style.json, out/Logbuch_Baumverlust.pdf
Veroeffentlicht NICHTS (kein Kopieren nach docs/, kein Git)."""
import sys, os, io, json, time, datetime, requests, numpy as np, geopandas as gpd, matplotlib
from shapely import set_precision
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_styles import BASE, QUELLE, LINKS, style     # gleiche Quellen-URLs wie die uebrigen Layer

CACHE = "data/logbuch_cache"; PX = 900
WMS = "https://www.wms.nrw.de/geobasis/wms_nw_hist_dop"
JAHR_FRUEH, JAHR_HEUTE = 2016, 2025
WMS_AKT = "https://www.wms.nrw.de/geobasis/wms_nw_dop"      # 2025: aktuelles DOP (Bildflug 2025, 10 cm)
METHODIK = "https://github.com/benjamin-bleske/wuppertal-vegetation-sentinel2/blob/main/METHODIK_Baummaske.md"
fd = os.path.join(matplotlib.get_data_path(), "fonts/ttf/")
for n, f in [("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"), ("DV-I", "DejaVuSans-Oblique.ttf")]:
    pdfmetrics.registerFont(TTFont(n, fd + f))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-B")
G = colors.HexColor("#1F3B2D")
body = ParagraphStyle("b", fontName="DV", fontSize=10, leading=14.5, spaceAfter=6)
small = ParagraphStyle("s", parent=body, fontSize=8.5, leading=11.5, textColor=colors.HexColor("#444444"))
cell = ParagraphStyle("c", fontName="DV", fontSize=9, leading=12)
cellb = ParagraphStyle("cb", parent=cell, fontName="DV-B")


# ---------- Eingabe
def lade_entscheidungen(pfad):
    d = json.load(open(pfad, encoding="utf-8"))
    liste = d["entscheidungen"] if isinstance(d, dict) else d
    return {int(x["nr"]): x for x in liste}

def lade_flaechen():
    g = gpd.read_file("data/verlust_gross.gpkg").sort_values("a", ascending=False).reset_index(drop=True)
    g["nr"] = range(1, len(g) + 1)
    return g


# ---------- Luftbilder
def hole_bild(jahr, b, nr):
    """Liefert PIL-Bild oder None (kein Bild dieses Jahrgangs). Zwischenspeicher in data/logbuch_cache/."""
    os.makedirs(CACHE, exist_ok=True)
    f = f"{CACHE}/{nr}_{jahr}_{PX}.jpg"
    if os.path.exists(f): return Image.open(f).convert("RGB")
    if os.path.exists(f + ".leer"): return None
    dienst, ebene = (WMS_AKT, "nw_dop_rgb") if jahr == 2025 else (WMS, f"nw_hist_dop_{jahr}")
    u = (f"{dienst}?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS={ebene}&STYLES=&CRS=EPSG:25832"
         f"&BBOX={b[0]:.2f},{b[1]:.2f},{b[2]:.2f},{b[3]:.2f}&WIDTH={PX}&HEIGHT={PX}&FORMAT=image/jpeg")
    for versuch in range(4):
        try:
            r = requests.get(u, timeout=60); r.raise_for_status()
            im = Image.open(io.BytesIO(r.content)).convert("RGB")
            break
        except Exception as e:
            print(f"  Fehler Nr. {nr}/{jahr} (Versuch {versuch + 1}): {e}")
            time.sleep(2 * (versuch + 1)); im = False
    if im is False: return "fehler"          # nicht zwischenspeichern, im PDF als nicht verfuegbar zeigen
    time.sleep(0.3)
    if np.asarray(im.resize((64, 64)).convert("L")).mean() / 255 > 0.97:     # weisse Kachel = kein Bild
        open(f + ".leer", "w").close(); return None
    im.save(f, quality=92); return im

def schoene_laenge(m):
    for v in (10, 20, 25, 50, 100, 200, 250, 500, 1000):
        if v >= m: return v
    return 1000

def als_jpeg(im):
    """Bild als JPEG puffern, damit das PDF klein bleibt."""
    im = im.convert("RGB"); im = im.resize((720, 720), Image.LANCZOS) if im.width > 720 else im
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=65); buf.seek(0)
    return buf


def zeichne(im, geo, b):
    """Umriss, Massstabsbalken und Nordpfeil ins Bild zeichnen."""
    im = im.copy(); dr = ImageDraw.Draw(im); s = PX / (b[2] - b[0])
    polys = geo.geoms if geo.geom_type == "MultiPolygon" else [geo]
    for p in polys:
        for ring in [p.exterior] + list(p.interiors):
            pts = [((x - b[0]) * s, (b[3] - y) * s) for x, y in ring.coords]
            dr.line(pts, fill=(0, 0, 0), width=6, joint="curve"); dr.line(pts, fill=(255, 214, 0), width=3, joint="curve")
    font = ImageFont.truetype(fd + "DejaVuSans-Bold.ttf", 22)
    laenge = schoene_laenge((b[2] - b[0]) / 6); px = laenge * s; x0, y0 = 20, PX - 30
    dr.rectangle([x0 - 10, y0 - 40, x0 + px + 95, y0 + 14], fill=(255, 255, 255))
    dr.line([x0, y0, x0 + px, y0], fill=(0, 0, 0), width=5)
    for x in (x0, x0 + px): dr.line([x, y0 - 8, x, y0 + 8], fill=(0, 0, 0), width=4)
    dr.text((x0, y0 - 36), "", font=font)
    dr.text((x0 + px + 10, y0 - 15), f"{laenge} m", fill=(0, 0, 0), font=font)
    cx, cy = PX - 40, 55                                  # Nordpfeil
    dr.ellipse([cx - 32, cy - 32, cx + 32, cy + 38], fill=(255, 255, 255))
    dr.polygon([(cx, cy - 26), (cx - 12, cy + 12), (cx, cy + 4), (cx + 12, cy + 12)], fill=(0, 0, 0))
    dr.text((cx - 8, cy + 10), "N", fill=(0, 0, 0), font=ImageFont.truetype(fd + "DejaVuSans-Bold.ttf", 20))
    return im


# ---------- PDF-Helfer
def absatz(c, text, stil, x, ytop, breite):
    p = Paragraph(text, stil); w, h = p.wrap(breite, 1000); p.drawOn(c, x, ytop - h); return ytop - h

def kopf_fuss(c, titel, seite):
    W, H = c._pagesize
    c.setFont("DV", 8); c.setFillColor(colors.HexColor("#666666"))
    c.drawString(2 * cm, 1.1 * cm, "Logbuch Baumverlust Wuppertal – Sichtprüfung, kein amtliches Ergebnis")
    c.drawRightString(W - 2 * cm, 1.1 * cm, f"Seite {seite}"); c.setFillColor(colors.black)

def de(zahl, nk=1): return f"{zahl:,.{nk}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def main():
    if len(sys.argv) < 2: sys.exit("Aufruf: logbuch.py PFAD/entscheidungen.json")
    ent = lade_entscheidungen(sys.argv[1]); g = lade_flaechen()
    gueltig = {nr for nr in ent if 1 <= nr <= len(g)}
    ja = sorted(nr for nr in gueltig if ent[nr].get("entscheidung") == "ja")
    nein = sum(1 for nr in gueltig if ent[nr].get("entscheidung") == "nein")
    unsicher = sum(1 for nr in gueltig if ent[nr].get("entscheidung") == "unsicher")
    geprueft = len(ja) + nein
    sel = g[g.nr.isin(ja)].copy(); sel["flaeche_ha"] = (sel.a / 1e4).round(1)
    ges_ha = float(sel.a.sum()) / 1e4
    print(f"{len(g)} Flaechen, {geprueft} entschieden (Ja {len(ja)}, Nein {nein}), unsicher {unsicher}")
    os.makedirs("out/geojson", exist_ok=True); os.makedirs("out/styles", exist_ok=True)

    # ---- 1. GeoJSON + Style
    # Infobox-Felder mit sprechenden Namen (Portal zeigt die Property-Namen an)
    sel["Ursache"] = sel.nr.map(lambda n: ent[n].get("ursache") or "nicht angegeben"); sel["Notiz"] = sel.nr.map(lambda n: ent[n].get("notiz") or "")
    sel["Nr"] = sel.nr; sel["Fläche (ha)"] = sel.flaeche_ha
    out = sel[["Nr", "Fläche (ha)", "Ursache", "Notiz", "geometry"]].to_crs(4326); out["geometry"] = set_precision(out.geometry.values, 1e-6)
    out.to_file("out/geojson/baumverlust_final.geojson", driver="GeoJSON", COORDINATE_PRECISION=6)
    desc = (f"Baumverlust-Flaechen von mindestens 1 Hektar, auf denen Sentinel-2 zwischen den Sommern 2015-2019 und 2021-2025 einen Baumbestand verschwinden sieht "
            f"und die vom Nutzer per Sichtpruefung an Luftbildern (Geobasis NRW, 2016 und 2025) bestaetigt wurden: {len(ja)} bestaetigte Flaechen, zusammen {de(ges_ha)} ha "
            f"({geprueft} von {len(g)} Erkennungen entschieden). Die Bestaetigung ist eine Sichtpruefung des Nutzers, keine amtliche Pruefung; die Luftbild-Jahre passen nicht genau zu den Sentinel-Zeitraeumen, "
            "die Luftbilder stammen aus 2016 und 2025 (Sommerbilder). Ursache der Verluste (Sturm, Kaefer, Einschlag) ist, soweit nicht je Flaeche angegeben, unbekannt. "
            "KEINE Gesamtbilanz des Baumbestands: kleinere Flaechen (unter 1 ha) und der Zuwachs sind nicht verlaesslich und hier nicht enthalten. "
            "Baum-Referenz: nDOM 2025 Geobasis NRW https://www.opengeodata.nrw.de/produkte/geobasis/hm/ndom50_tiff/ ; Luftbilder https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?REQUEST=GetCapabilities&SERVICE=WMS ; "
            f"Methode und Grenzen: {METHODIK} ; Schritt fuer Schritt erklaert: https://benjamin-bleske.github.io/wuppertal-vegetation-sentinel2/baummaske/ . ") + QUELLE + LINKS
    sty = style("baumverlust_final", "Baumverlust bestaetigt (Sichtpruefung, Sentinel-2 2015-2019 zu 2021-2025)", desc, ["Sentinel-2", "Baeume", "Verlust", "Sichtpruefung"],
                {"bvf": {"type": "geojson", "data": f"{BASE}/geojson/baumverlust_final.geojson"}},
                [{"id": "bvf-fill", "type": "fill", "source": "bvf", "paint": {"fill-color": "#D32F2F", "fill-opacity": 0.55}},
                 {"id": "bvf-line", "type": "line", "source": "bvf", "paint": {"line-color": "#7f0000", "line-width": 1}}])
    json.dump(sty, open("out/styles/baumverlust_final.style.json", "w"), ensure_ascii=False, indent=1)

    # ---- 2. PDF
    wgs = gpd.GeoSeries(g.geometry.representative_point(), crs=25832).to_crs(4326)
    c = canvas.Canvas("out/Logbuch_Baumverlust.pdf", pagesize=A4); c.setTitle("Logbuch Baumverlust Wuppertal"); c.setAuthor("Benjamin Bleske")
    W, H = A4; L = 2 * cm; B = W - 2 * L; seite = 1
    heute = datetime.date.today().strftime("%d.%m.%Y")

    # Titelseite
    c.setFillColor(G); c.setFont("DV-B", 26); c.drawString(L, H - 4.2 * cm, "Logbuch Baumverlust")
    c.setFont("DV", 14); c.drawString(L, H - 5.2 * cm, "Wuppertal, Flächen ab 1 Hektar – per Sichtprüfung bestätigt"); c.setFillColor(colors.black)
    c.setFont("DV", 10); c.drawString(L, H - 6.1 * cm, f"Stand: {heute}")
    y = absatz(c, "<b>Kurz erklärt:</b> Aus Sentinel-2-Satellitenbildern wurden Flächen gesucht, auf denen zwischen den Sommern 2015–2019 und 2021–2025 Baumbestand (meist Nadelwald) verschwunden ist. "
               "Die Erkennung fand 73 Flächen von mindestens 1 Hektar. Jede dieser Flächen wurde anschließend von Hand an amtlichen Luftbildern (2016 und 2025) angesehen und mit Ja, Nein oder Unsicher bewertet. "
               "Dieses Logbuch zeigt für jede mit Ja bestätigte Fläche ein Bild von früher und von heute mit eingezeichnetem Umriss.", body, L, H - 7.3 * cm, B)
    zahlen = [["Erkennungen ab 1 ha", str(len(g))], ["Davon entschieden (Ja oder Nein)", str(geprueft)], ["Bestätigt als Baumverlust (Ja)", str(len(ja))],
              ["Abgelehnt (Nein)", str(nein)], ["Unsicher / noch offen", f"{unsicher} / {len(g) - geprueft - unsicher}"],
              ["Gesamtfläche der bestätigten Flächen", f"{de(ges_ha)} ha"]]
    t = Table([[Paragraph(a, cell), Paragraph(f"<b>{v}</b>", cell)] for a, v in zahlen], colWidths=[10 * cm, 4 * cm])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#AAAAAA")), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F6F2")), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    w, h = t.wrap(B, 500); t.drawOn(c, L, y - 0.8 * cm - h)
    absatz(c, "<b>Wichtig:</b> Das ist keine Gesamtbilanz des Baumbestands in Wuppertal, sondern nur die größeren Flächen (ab 1 ha) und nur das, was auf den Luftbildern erkennbar war.", small, L, y - 1.8 * cm - h, B)
    kopf_fuss(c, "", seite); c.showPage(); seite += 1

    # Methodik und Grenzen
    c.setFillColor(G); c.setFont("DV-B", 18); c.drawString(L, H - 3 * cm, "Methode, Quellen und Grenzen"); c.setFillColor(colors.black)
    texte = [
        "<b>1. Erkennung.</b> Aus Sentinel-2 (Copernicus, 10 m Pixelgröße, Sommer-Mosaike) wird pro Sommer eine Baummaske berechnet. Verglichen werden die Zeiträume 2015–2019 und 2021–2025. Wo früher Bäume waren und später nicht mehr, entsteht eine Verlustfläche.",
        "<b>2. Sichtprüfung.</b> Jede Fläche ab 1 ha wurde mit amtlichen Luftbildern verglichen (früher: 2016, heute: 2025). Die Entscheidung Ja/Nein/Unsicher trifft der Nutzer von Hand mit dem Prüf-Tool. Der Vorschlag des Assistenten im Tool war nur eine Orientierung und ist nicht unabhängig bestätigt.",
        "<b>3. Quellen.</b><br/>"
        "• Sentinel-2 L2A: https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a (Mission: https://sentinels.copernicus.eu/copernicus/sentinel-2)<br/>"
        "• Luftbilder (Geobasis NRW, Datenlizenz dl-de/zero-2-0), WMS 2016: https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?REQUEST=GetCapabilities&amp;SERVICE=WMS ; WMS 2025 (aktuelles DOP): https://www.wms.nrw.de/geobasis/wms_nw_dop?REQUEST=GetCapabilities&amp;SERVICE=WMS<br/>"
        "• Baum-Referenz nDOM: https://www.opengeodata.nrw.de/produkte/geobasis/hm/ndom50_tiff/<br/>"
        "• Stadtgrenze: © OpenStreetMap contributors (ODbL), https://www.openstreetmap.org/copyright<br/>"
        f"• Methode und Grenzen im Projekt: {METHODIK}",
        "<b>4. Grenzen – bitte beachten:</b><br/>"
        f"• Die Luftbilder {JAHR_FRUEH} und {JAHR_HEUTE} passen <b>nicht genau</b> zu den Satelliten-Zeiträumen (2015–2019 und 2021–2025). Ein Verlust kann zwischen den Zeiträumen, aber auch vor 2016 passiert sein.<br/>"
        f"• Beide Luftbilder sind Sommerbilder: {JAHR_HEUTE}: Bildflug laut Geobasis NRW für alle 73 Flächen im Jahr 2025 (meist Juni, 5 Flächen Juli, 1 Fläche März); {JAHR_FRUEH}: in der geprüften Stichkachel 18.08.2016, kann je Kachel abweichen.<br/>"
        "• Die Bestätigung ist eine <b>Sichtprüfung</b> am Bildschirm, keine Geländeprüfung und keine amtliche Feststellung.<br/>"
        "• Es ist <b>keine Gesamtbilanz</b>: Flächen unter 1 ha und Baumzuwachs sind nicht enthalten.<br/>"
        "• Die <b>Ursache</b> (Einschlag, Sturm, Käfer, Abbau, Bebauung) ist aus den Bildern nicht sicher ablesbar. Wo sie angegeben ist, ist sie eine Vermutung des Nutzers.<br/>"
        "• Wo ein Jahrgang kein Bild liefert, steht „kein Bild verfügbar“."]
    y = H - 3.8 * cm
    for t_ in texte: y = absatz(c, t_, body, L, y, B) - 4
    kopf_fuss(c, "", seite); c.showPage(); seite += 1

    # Uebersichtstabelle
    rows = [["Nr.", "Größe (ha)", "Koordinaten (WGS84)", "Ursache"]]
    for nr in ja:
        e = ent[nr]; i = nr - 1
        rows.append([str(nr), de(g.a[i] / 1e4), f"{wgs[i].y:.5f} N, {wgs[i].x:.5f} O".replace(".", ","), e.get("ursache") or "nicht angegeben"])
    rows.append(["", f"<b>{de(ges_ha)}</b>", f"<b>Summe {len(ja)} Flächen</b>", ""])
    def tabelle_seite(chunk, erste):
        c.setFillColor(G); c.setFont("DV-B", 18); c.drawString(L, H - 3 * cm, "Übersicht der bestätigten Flächen" + ("" if erste else " (Fortsetzung)")); c.setFillColor(colors.black)
        tb = Table([[Paragraph(str(x), cellb if k == 0 and erste else cell) for x in r] for k, r in enumerate(chunk)], colWidths=[1.6 * cm, 3 * cm, 7 * cm, 5.4 * cm], repeatRows=0)
        tb.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#AAAAAA")), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E3EFE6")), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        tb.wrap(B, H); tb.drawOn(c, L, H - 3.6 * cm - tb._height)
    kopf = rows[0]; daten = rows[1:]; pro = 30; teile = [daten[i:i + pro] for i in range(0, max(len(daten), 1), pro)] or [[]]
    for k, tl in enumerate(teile):
        if not tl and len(ja) == 0:
            tl = [["", "", "Keine Fläche mit „Ja“ bestätigt.", ""]]
        tabelle_seite([kopf] + tl, k == 0); kopf_fuss(c, "", seite); c.showPage(); seite += 1

    # Flaechenseiten (Querformat)
    LW, LH = landscape(A4); c.setPageSize((LW, LH))
    for k, nr in enumerate(ja, 1):
        i = nr - 1; geo = g.geometry[i]; x0, y0, x1, y1 = geo.bounds
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; h = max(x1 - x0, y1 - y0, 250) / 2 + 120; b = (cx - h, cy - h, cx + h, cy + h)
        print(f"Logbuch-Seite {k}/{len(ja)}: Nr. {nr}")
        e = ent[nr]
        c.setFillColor(G); c.setFont("DV-B", 18); c.drawString(L, LH - 1.9 * cm, f"Nr. {nr} – {de(g.a[i] / 1e4)} ha Baumverlust"); c.setFillColor(colors.black)
        c.setFont("DV", 10)
        c.drawString(L, LH - 2.6 * cm, f"Koordinaten (WGS84): {wgs[i].y:.5f} N, {wgs[i].x:.5f} O".replace(".", ",") )
        c.setFont("DV", 7.5); c.drawRightString(LW - L, LH - 1.9 * cm, f"OpenStreetMap: openstreetmap.org/?mlat={wgs[i].y:.5f}&mlon={wgs[i].x:.5f}#map=17/{wgs[i].y:.5f}/{wgs[i].x:.5f}"); c.setFont("DV", 10)
        S = 12.2 * cm; gap = LW - 2 * L - 2 * S; ytop = LH - 3.0 * cm
        for j, (jahr, wort, notiz) in enumerate([(JAHR_FRUEH, "Früher", "Sommer (Stichprobe: 18.08.2016)"), (JAHR_HEUTE, "Heute", "Bildflug 2025, meist Juni")]):
            xx = L + j * (S + gap); im = hole_bild(jahr, b, nr)
            if isinstance(im, Image.Image):
                c.drawImage(ImageReader(als_jpeg(zeichne(im, geo, b))), xx, ytop - S, S, S)
            else:
                c.setFillColor(colors.HexColor("#EEEEEE")); c.rect(xx, ytop - S, S, S, fill=1, stroke=0); c.setFillColor(colors.HexColor("#555555")); c.setFont("DV-B", 14)
                c.drawCentredString(xx + S / 2, ytop - S / 2, "kein Bild verfügbar" if im is None else "Bild konnte nicht geladen werden"); c.setFillColor(colors.black)
            c.setStrokeColor(colors.HexColor("#888888")); c.rect(xx, ytop - S, S, S, fill=0)
            c.setFont("DV-B", 10); c.drawString(xx, ytop - S - 0.5 * cm, f"{wort}: Luftbild {jahr}")
            c.setFont("DV", 7.5); c.drawString(xx, ytop - S - 0.95 * cm, f"Quelle: Geobasis NRW, {'WMS nw_dop (aktuell)' if jahr == 2025 else f'WMS nw_hist_dop_{jahr}'} (dl-de/zero-2-0)")
            c.drawString(xx, ytop - S - 1.35 * cm, notiz)
        yy = ytop - S - 1.9 * cm
        absatz(c, f"<b>Ursache:</b> {e.get('ursache') or 'nicht angegeben'} &nbsp;&nbsp; <b>Notiz:</b> {(e.get('notiz') or 'keine').replace('&', '&amp;').replace('<', '&lt;')}"
                  " &nbsp;&nbsp; <i>(gelber Umriss = erkannte Fläche; Sichtprüfung, Bildjahre passen nicht exakt zu den Sentinel-Zeiträumen)</i>", ParagraphStyle("n", parent=body, fontSize=9.5, leading=12.5), L, yy, LW - 2 * L)
        kopf_fuss(c, "", seite); c.showPage(); seite += 1
    c.save(); print("fertig: out/Logbuch_Baumverlust.pdf,", len(ja), "Flaechenseiten")

if __name__ == "__main__":
    main()
