"""Abbildungen fuer das Methoden-PDF (Beispieljahre 2015 und 2016)."""
import sys, json
sys.path.insert(0, "scripts")
import numpy as np, rasterio, geopandas as gpd
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.features import geometry_mask
from scipy.ndimage import binary_dilation, median_filter, label
from pystac_client import Client
import planetary_computer as pc
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, FancyBboxPatch
from pyproj import Transformer
import options

YEARS = [2015, 2016]
OUT = "out/report/"
X0, Y0, X1, Y1 = 354000, 5663000, 382000, 5688000
W, H = (X1 - X0) // 10, (Y1 - Y0) // 10
TR = from_origin(X0, Y1, 10, 10)
EXT = (X0, X1, Y0, Y1)
CITY = gpd.read_file("data/wuppertal_boundary.geojson").to_crs(25832)
INSIDE = geometry_mask(CITY.geometry, out_shape=(H, W), transform=TR, invert=True)
plt.rcParams.update({"font.size": 9, "figure.dpi": 110, "savefig.bbox": "tight"})

def comp(y, folder="data"):
    with rasterio.open(f"{folder}/composite_{y}.tif") as s:
        return s.read()

def crop(a):  # Ausschnitt auf Stadt (bbox)
    r, c = np.where(INSIDE); return a[r.min():r.max() + 1, c.min():c.max() + 1]
def ext_city():
    r, c = np.where(INSIDE)
    return (X0 + c.min() * 10, X0 + (c.max() + 1) * 10, Y1 - (r.max() + 1) * 10, Y1 - r.min() * 10)
EC = ext_city()
def rgb_of(b4, b3, b2, ok):
    v = np.clip(np.dstack([b4, b3, b2]) / 0.16, 0, 1) ** 0.7
    v[~ok | ~INSIDE] = 1; return v

# ---- 1) Workflow-Diagramm
def fig_workflow():
    steps = ["1 Szenen\nsuchen", "2 Wolken-\nmaske (SCL)", "3 Median-\nMosaik", "4 EVI\nberechnen",
             "5 Schwelle,\nFilter", "6 Vektori-\nsieren", "7 Vergleich\n(Differenz)", "8 Style-JSON,\nGitHub Pages"]
    fig, ax = plt.subplots(figsize=(7.2, 1.9)); ax.axis("off"); ax.set_xlim(0, 8); ax.set_ylim(0, 1)
    for i, s in enumerate(steps):
        ax.add_patch(FancyBboxPatch((i + 0.06, 0.2), 0.88, 0.6, boxstyle="round,pad=0.02", fc="#E8F5E9", ec="#2E7D32"))
        ax.text(i + 0.5, 0.5, s, ha="center", va="center", fontsize=7.2)
        if i < 7: ax.annotate("", (i + 1.06, 0.5), (i + 0.96, 0.5), arrowprops=dict(arrowstyle="->", color="#2E7D32"))
    plt.savefig(OUT + "workflow.png", dpi=200); plt.close()

# ---- 2) Szenenverfuegbarkeit
cat = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1", modifier=pc.sign_inplace)
def items_for(y):
    return list(cat.search(collections=["sentinel-2-l2a"], bbox=[6.98, 51.14, 7.37, 51.36],
                           datetime=f"{y}-07-25/{y}-09-15").items())

def fig_availability(items_by_year):
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.6), sharey=True)
    for a, y in zip(ax, YEARS):
        its = [i for i in items_by_year[y] if "T32ULB" in i.id]
        for i in its:
            cc = i.properties["eo:cloud_cover"]
            a.scatter(i.datetime, cc, c="#2E7D32" if cc < 40 else ("#F9A825" if cc < 80 else "#B71C1C"), s=28, zorder=3)
        a.axhline(80, color="#B71C1C", ls=":", lw=1); a.set_title(f"{y}: {len(its)} Aufnahmen der Kachel 32ULB")
        a.set_ylabel("Wolkenbedeckung der Kachel (%)" if y == YEARS[0] else ""); a.grid(alpha=.3)
        a.tick_params(axis="x", rotation=45)
    plt.tight_layout(); plt.savefig(OUT + "verfuegbarkeit.png", dpi=200); plt.close()

# ---- 3) SCL-Beispiel
def readband(item, asset, resampling):
    href = pc.sign(item.assets[asset].href)
    with rasterio.open(href) as src, WarpedVRT(src, crs="EPSG:25832", transform=TR, width=W, height=H,
                                               resampling=resampling, nodata=0) as v:
        return v.read(1)

SCLC = ["#000000", "#E53935", "#616161", "#795548", "#43A047", "#FDD835", "#1E88E5", "#BDBDBD", "#9E9E9E", "#FAFAFA", "#81D4FA", "#80DEEA"]
SCLN = ["0 kein Wert", "1 gesättigt", "2 dunkel", "3 Wolkenschatten", "4 Vegetation", "5 unbewachsen", "6 Wasser",
        "7 unklassifiziert", "8 Wolke (mittel)", "9 Wolke (hoch)", "10 Zirrus", "11 Schnee"]
def fig_scl(items_by_year):
    fig, ax = plt.subplots(2, 3, figsize=(7.2, 5.4))
    info = {}
    for row, y in enumerate(YEARS):
        # Szene waehlen, die ueber der Stadt teilweise bewoelkt ist (ca. 25 %), ohne Nodata/Saettigung
        best, bs = None, 9
        for i in items_by_year[y]:
            if "T32ULB" not in i.id and "T31UGT" not in i.id: continue
            try: sc = readband(i, "SCL", Resampling.nearest)[INSIDE]
            except Exception: continue
            f = lambda cl: np.isin(sc, cl).mean()
            if f([0, 1]) > 0.02: continue
            score = abs(f([3, 8, 9, 10]) - 0.25)
            if score < bs: best, bs = i, score
        it = best
        scl = readband(it, "SCL", Resampling.nearest)
        b4, b3, b2 = [readband(it, b, Resampling.bilinear).astype("float32") / 10000 for b in ["B04", "B03", "B02"]]
        raw0 = b4 == 0
        good = np.isin(scl, [2, 4, 5, 6, 7]) & ~raw0
        good2 = ~binary_dilation(~good & (scl > 0), iterations=2) & good
        info[y] = (it.id, it.properties["eo:cloud_cover"])
        ok = np.ones_like(INSIDE)
        v = rgb_of(b4, b3, b2, ok); ax[row, 0].imshow(crop(v), extent=EC)
        s = np.where(INSIDE, scl, 0)
        ax[row, 1].imshow(crop(s), extent=EC, cmap=ListedColormap(SCLC), norm=BoundaryNorm(range(13), 12), interpolation="nearest")
        m = np.where(INSIDE, np.where(good2, 1, 2), 0)
        ax[row, 2].imshow(crop(m), extent=EC, cmap=ListedColormap(["white", "#2E7D32", "#B71C1C"]), vmin=0, vmax=2, interpolation="nearest")
        ax[row, 0].set_ylabel(f"{y}\n{it.datetime.date()}  ({it.properties['eo:cloud_cover']:.0f} % Wolken)")
        for a in ax[row]: a.set_xticks([]); a.set_yticks([])
    ax[0, 0].set_title("Echtfarben (B04/B03/B02)"); ax[0, 1].set_title("Szenenklassifikation SCL"); ax[0, 2].set_title("gültig (grün) / verworfen (rot)")
    fig.legend(handles=[Patch(color=c, label=n) for c, n in zip(SCLC, SCLN)], ncol=4, loc="lower center", fontsize=6.5, frameon=False)
    plt.tight_layout(rect=(0, .08, 1, 1)); plt.savefig(OUT + "scl.png", dpi=200); plt.close()
    return info

# ---- 4) Lueckenfehler (SCL-Klasse 2)
def fig_gaps():
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.8))
    for a, (lab, folder) in zip(ax[:2], [("Maske ohne Klasse 2 (v1)", "data/v1"), ("Klasse 2 gültig (final)", "data")]):
        n = comp(2015, folder)[5]
        gap = (n < 2) & INSIDE
        a.imshow(crop(np.where(INSIDE, np.where(gap, 2, 1), 0)), extent=EC, cmap=ListedColormap(["white", "#C8E6C9", "#B71C1C"]), vmin=0, vmax=2, interpolation="nearest")
        a.set_title(f"{lab}\nLücken: {100 * gap.sum() / INSIDE.sum():.2f} % der Stadt", fontsize=8); a.axis("off")
    n = comp(2015)[5]
    im = ax[2].imshow(crop(np.where(INSIDE, np.clip(n, 0, 20), np.nan)), extent=EC, cmap="viridis")
    ax[2].set_title("Klare Beobachtungen pro Pixel (n_obs)\nfinal, 2015", fontsize=8); ax[2].axis("off"); plt.colorbar(im, ax=ax[2], shrink=.7)
    plt.tight_layout(); plt.savefig(OUT + "luecken.png", dpi=200); plt.close()

# ---- 5) Mosaike
def fig_mosaic():
    fig, ax = plt.subplots(2, 2, figsize=(7.2, 6))
    for row, y in enumerate(YEARS):
        b2, b3, b4, b8, b11, n = comp(y)
        ax[row, 0].imshow(crop(rgb_of(b4, b3, b2, n >= 2)), extent=EC); ax[row, 0].set_title(f"Median-Mosaik {y} (Echtfarben)")
        im = ax[row, 1].imshow(crop(np.where(INSIDE, np.clip(n, 0, 25), np.nan)), extent=EC, cmap="viridis"); ax[row, 1].set_title(f"{y}: klare Beobachtungen pro Pixel")
        plt.colorbar(im, ax=ax[row, 1], shrink=.7)
        for a in ax[row]: a.axis("off")
    plt.tight_layout(); plt.savefig(OUT + "mosaik.png", dpi=200); plt.close()

# ---- 6) EVI + Histogramm
def fig_evi():
    fig, ax = plt.subplots(2, 2, figsize=(7.2, 6), gridspec_kw={"width_ratios": [1.2, 1]})
    for row, y in enumerate(YEARS):
        d = options.indices(y)
        evi = np.where(INSIDE & d["ok"], d["evi"], np.nan)
        im = ax[row, 0].imshow(crop(evi), extent=EC, cmap="YlGn", vmin=0, vmax=0.9); ax[row, 0].axis("off")
        ax[row, 0].set_title(f"EVI {y}"); plt.colorbar(im, ax=ax[row, 0], shrink=.7)
        v = evi[~np.isnan(evi)]
        ax[row, 1].hist(v, bins=80, range=(-0.1, 1.0), color="#66BB6A"); ax[row, 1].axvline(0.45, color="#B71C1C", ls="--")
        ax[row, 1].set_title(f"{y}: Verteilung, Schwelle 0,45"); ax[row, 1].set_xlabel("EVI"); ax[row, 1].set_yticks([])
    plt.tight_layout(); plt.savefig(OUT + "evi.png", dpi=200); plt.close()

# ---- 7) Optionen A/B/C
def option_shares():
    res = {}
    for y in YEARS:
        d = options.indices(y); d["ok"] &= INSIDE
        thr = np.nanpercentile(d["tex"][INSIDE & d["ok"]], 40)
        A, B, C = options.masks(d, thr)
        res[y] = [100 * m[INSIDE].sum() / INSIDE.sum() for m in (A, B, C)]
    return res

def fig_options():
    d = options.indices(2015); d["ok"] &= INSIDE
    thr = np.nanpercentile(d["tex"][INSIDE & d["ok"]], 40)
    A, B, C = options.masks(d, thr)
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.6))
    for a, m, t in zip(ax, (A, B, C), ["A: NDVI > 0,65", "B: EVI > 0,45 (gewählt)", "C: NDVI+NDMI+Textur"]):
        a.imshow(crop(np.where(INSIDE, np.where(m, 1, 2), 0)), extent=EC, cmap=ListedColormap(["white", "#2E7D32", "#ECEBE6"]), vmin=0, vmax=2, interpolation="nearest")
        a.set_title(f"{t}\n{100 * m[INSIDE].sum() / INSIDE.sum():.1f} % (2015)", fontsize=8); a.axis("off")
    plt.tight_layout(); plt.savefig(OUT + "optionen.png", dpi=200); plt.close()

# ---- 8) Vektorisierung im Ausschnitt
def fig_vector():
    import vectorize
    m, ok, tr, crs = vectorize.veg_mask(2015)
    evi, ok2, _, _ = vectorize.load(2015)
    raw = (evi > vectorize.EVI_THR) & ok2
    t = Transformer.from_crs(4326, 25832, always_xy=True); cx, cy = t.transform(7.13, 51.255); half = 1500
    c0, c1 = int((cx - half - X0) / 10), int((cx + half - X0) / 10); r0, r1 = int((Y1 - cy - half) / 10), int((Y1 - cy + half) / 10)
    ex = (X0 + c0 * 10, X0 + c1 * 10, Y1 - r1 * 10, Y1 - r0 * 10)
    g = gpd.read_file("out/geojson/vegetation_2015.geojson").to_crs(25832)
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.7))
    cm = ListedColormap(["#ECEBE6", "#2E7D32"])
    ax[0].imshow(raw[r0:r1, c0:c1], extent=ex, cmap=cm, interpolation="nearest"); ax[0].set_title("EVI > 0,45 (roh)", fontsize=8)
    ax[1].imshow(m[r0:r1, c0:c1], extent=ex, cmap=cm, interpolation="nearest"); ax[1].set_title("Medianfilter + min. 400 m²", fontsize=8)
    ax[2].imshow(m[r0:r1, c0:c1], extent=ex, cmap=ListedColormap(["#ECEBE6", "#C8E6C9"]), interpolation="nearest")
    g.boundary.plot(ax=ax[2], color="#1B5E20", lw=.5); ax[2].set_xlabel(""); ax[2].set_ylabel(""); ax[2].set_xlim(ex[0], ex[1]); ax[2].set_ylim(ex[2], ex[3]); ax[2].set_title("Polygone (GeoJSON, 5 m vereinfacht)", fontsize=8)
    for a in ax: a.set_xticks([]); a.set_yticks([])
    plt.tight_layout(); plt.savefig(OUT + "vektor.png", dpi=200); plt.close()
    return raw[INSIDE].sum(), m[INSIDE].sum()

# ---- 9) Differenz 2015 -> 2016
def fig_change():
    import vectorize
    m1, ok1, _, _ = vectorize.veg_mask(2015); m2, ok2, _, _ = vectorize.veg_mask(2016)
    valid = ok1 & ok2
    loss = m1 & ~m2 & valid; gain = ~m1 & m2 & valid; stable = m1 & m2 & valid
    code = np.where(INSIDE, 1, 0); code[stable] = 2; code[loss] = 3; code[gain] = 4
    fig, ax = plt.subplots(1, 1, figsize=(7.2, 5.4))
    ax.imshow(crop(code), extent=EC, cmap=ListedColormap(["white", "#ECEBE6", "#C8E6C9", "#D32F2F", "#1976D2"]), vmin=0, vmax=4, interpolation="nearest")
    ax.axis("off"); ax.legend(handles=[Patch(color=c, label=l) for c, l in [("#C8E6C9", "stabil Vegetation"), ("#D32F2F", "Verlust 2015→2016"), ("#1976D2", "Zuwachs 2015→2016"), ("#ECEBE6", "keine Vegetation")]], loc="lower left", fontsize=7, frameon=False)
    plt.tight_layout(); plt.savefig(OUT + "aenderung.png", dpi=200); plt.close()
    return dict(loss=loss.sum() / 1e4, gain=gain.sum() / 1e4, stable=stable.sum() / 1e4, share=[100 * m1[INSIDE].sum() / INSIDE.sum(), 100 * m2[INSIDE].sum() / INSIDE.sum()])

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "scl":
        ib = {y: items_for(y) for y in YEARS}; print(fig_scl(ib)); fig_vector(); sys.exit()
    fig_workflow()
    ib = {y: items_for(y) for y in YEARS}
    fig_availability(ib)
    stats = {"scl": {str(k): v for k, v in fig_scl(ib).items()}}
    fig_gaps(); fig_mosaic(); fig_evi(); fig_options()
    stats["options"] = {str(k): v for k, v in option_shares().items()}
    stats["vector"] = [int(x) for x in fig_vector()]
    stats["change"] = {k: (float(v) if not isinstance(v, list) else v) for k, v in fig_change().items()}
    stats["counts"] = {str(y): len([i for i in ib[y] if True]) for y in YEARS}
    json.dump(stats, open(OUT + "stats.json", "w"), indent=1, default=float)
    print(json.dumps(stats, indent=1, default=float))
