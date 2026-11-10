"""Bilder fuer die Erklaerseite docs/baummaske/index.html (Schritt 1-3) -> docs/baummaske/*.png"""
import json, io, re, requests, numpy as np, rasterio, geopandas as gpd
from rasterio.features import rasterize
from rasterio.windows import from_bounds
from PIL import Image
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
O = "docs/baummaske/"; X0, Y1 = 354000, 5688000
t = json.load(open("out/report/baummaske_test.json"))["_hart"]

# Bild 1: wie gut trennt was Baum von Acker/Wiese?
lab = [("EVI 2025\n(unsere erste Karte)", t["EVI 2025"]), ("NDVI 2025", t["NDVI 2025"]),
       ("Schwankung von\nSommer zu Sommer", t["EVI Schwankung (Std) 11 Jahre"]), ("Alles zusammen\n(angelernt)", t["Kombination"]["auc"])]
fig, ax = plt.subplots(figsize=(10, 4.8)); cols = ["#EF6C00", "#F9A825", "#7CB342", "#2E7D32"]
b = ax.bar([l for l, _ in lab], [(v - .5) * 200 for _, v in lab], color=cols)
ax.set_ylim(0, 100); ax.set_ylabel("Trefferquote über Raten (%)\n0 = wie Würfeln, 100 = perfekt", fontsize=11)
for r, (_, v) in zip(b, lab): ax.text(r.get_x() + r.get_width() / 2, r.get_height() + 2, f"{(v - .5) * 200:.0f} %", ha="center", fontsize=15, fontweight="bold")
ax.set_title("Wie gut unterscheidet das Merkmal einen Baum von Acker oder Wiese?", fontsize=13, fontweight="bold", loc="left")
for s in ("top", "right"): ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig(O + "schritt1_trennung.png", dpi=80); plt.close()

# Bild 2: eine Kachel in vier Schritten
tiles = json.load(open("data/ndom/auswahl.json")); name = "ndom50_32371_5679_1_nw_2025.tif" if "ndom50_32371_5679_1_nw_2025.tif" in tiles else tiles[0]
m = re.match(r"ndom50_32(\d{3})_(\d{4})_", name); e0, n0 = int(m[1]) * 1000, int(m[2]) * 1000
with rasterio.open("data/ndom/" + name) as s: h = s.read(1)
bld = gpd.read_file("data/osm_buildings.gpkg").geometry.buffer(2).union_all()
bm = rasterize([(bld, 1)], out_shape=h.shape, transform=rasterio.transform.from_origin(e0, n0 + 1000, .5, .5), fill=0, dtype="uint8").astype(bool)
tree = ((h >= 3) & ~bm & (h > -100)).reshape(100, 20, 100, 20).mean((1, 3)); bf = bm.reshape(100, 20, 100, 20).mean((1, 3))
ref = np.full(tree.shape, 0); ref[(tree <= .05) & (bf < .1)] = 1; ref[(tree >= .6) & (bf < .1)] = 2; ref[bf >= .1] = 3      # 0 unklar,1 Nicht-Baum,2 Baum,3 Gebaeude
with rasterio.open("data/baumprob_B.tif") as s: pr = s.read(1, window=from_bounds(e0, n0, e0 + 1000, n0 + 1000, s.transform))
u = ("https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=nw_hist_dop_2023&STYLES="
     f"&CRS=EPSG:25832&BBOX={e0},{n0},{e0+1000},{n0+1000}&WIDTH=800&HEIGHT=800&FORMAT=image/jpeg")
fig, ax = plt.subplots(1, 4, figsize=(20, 5.8)); ext = (0, 1000, 0, 1000)
ax[0].imshow(np.asarray(Image.open(io.BytesIO(requests.get(u, timeout=60).content)).convert("RGB")), extent=ext); ax[0].set_title("1  Luftbild (1 km × 1 km)", fontsize=14, fontweight="bold", loc="left")
im = ax[1].imshow(np.where(h > -100, h, np.nan), cmap="viridis", vmin=0, vmax=30, extent=ext); ax[1].set_title("2  Höhe über Boden\nhell = hoch, bis 30 m", fontsize=14, fontweight="bold", loc="left")
ax[2].imshow(ref, cmap=ListedColormap(["#ffffff", "#d7ccc8", "#1B5E20", "#455A64"]), vmin=0, vmax=3, extent=ext, interpolation="nearest")
ax[2].set_title("3  Referenz (Musterlösung): dunkelgrün = Baum,\nbeige = kein Baum, grau-blau = Gebäude, weiß = unklar", fontsize=14, fontweight="bold", loc="left")
im4 = ax[3].imshow(np.where(pr >= 0, pr, np.nan), cmap="Greens", vmin=0, vmax=1, extent=ext); ax[3].set_title("4  Was der Satellit allein sagt\nweiß = kein Baum, dunkelgrün = Baum", fontsize=14, fontweight="bold", loc="left")
cb = fig.colorbar(im4, ax=ax[3], fraction=.046, pad=.02); cb.set_label("Wie sicher ist 'Baum'? (0 = gar nicht, 1 = sehr)", fontsize=10)
for a in ax: a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); plt.savefig(O + "schritt2_probe.png", dpi=70); plt.close()
print("Kachel", name)

# Bild 3: wie sieht ein 'gruener Nicht-Baum' im Lauf der Jahre aus?
E = []
for y in range(2015, 2026):
    with rasterio.open(f"data/composite_{y}.tif") as s: a = s.read().astype("float32")
    E.append(np.where(a[0] > -1, 2.5 * (a[3] - a[2]) / (a[3] + 6 * a[2] - 7.5 * a[0] + 1), np.nan))
E = np.stack(E); G, N = [], []
for nm in tiles:
    m = re.match(r"ndom50_32(\d{3})_(\d{4})_", nm); e, n = int(m[1]) * 1000, int(m[2]) * 1000
    with rasterio.open("data/ndom/" + nm) as s: hh = s.read(1)
    bb = rasterize([(bld, 1)], out_shape=hh.shape, transform=rasterio.transform.from_origin(e, n + 1000, .5, .5), fill=0, dtype="uint8").astype(bool)
    tr_ = ((hh >= 3) & ~bb & (hh > -100)).reshape(100, 20, 100, 20).mean((1, 3)); bfr = bb.reshape(100, 20, 100, 20).mean((1, 3))
    r0, c0 = (Y1 - (n + 1000)) // 10, (e - X0) // 10
    if r0 < 0 or c0 < 0 or r0 + 100 > E.shape[1] or c0 + 100 > E.shape[2]: continue
    sl = E[:, r0:r0 + 100, c0:c0 + 100]
    G.append(sl[:, (tr_ >= .6) & (bfr < .1)].T); N.append(sl[:, (tr_ <= .05) & (bfr < .1) & (sl[-1] > .45)].T)
G, N = np.concatenate(G), np.concatenate(N); G, N = G[np.isfinite(G).all(1)], N[np.isfinite(N).all(1)]
print("Pixel Baum", len(G), "gruene Nicht-Baeume", len(N))
yrs = np.arange(2015, 2026); fig, ax = plt.subplots(figsize=(10, 5.2))
for d, c, l in ((G, "#2E7D32", f"Bäume (Referenz)"), (N, "#EF6C00", "'Grüne' Nicht-Bäume (Acker, Wiese)")):
    ax.fill_between(yrs, *np.percentile(d, [10, 90], axis=0), color=c, alpha=.25); ax.plot(yrs, np.median(d, 0), color=c, lw=3, label=l)
ax.axhline(.45, color="k", ls="--", lw=1); ax.text(2015.05, .465, "unsere bisherige Grenze 'viel Grün'", fontsize=10)
ax.set_xticks(yrs); ax.set_ylabel("Grün-Wert (EVI) im Sommer"); ax.legend(loc="lower right", fontsize=11); ax.grid(alpha=.3)
ax.set_title("Äcker und Wiesen schwanken stärker von Jahr zu Jahr als Bäume\n(Linie = Mitte, Band = 80 % der Pixel)", fontsize=13, fontweight="bold", loc="left")
plt.tight_layout(); plt.savefig(O + "schritt3_jahre.png", dpi=80)
