"""Alle Baumverlust-Flaechen >= 1 ha: Luftbild 2016 | 2023 nebeneinander, nummeriert (nach Groesse), zur Sichtpruefung -> out/report/gross_*.png"""
import io, requests, numpy as np, geopandas as gpd
from PIL import Image
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
d = gpd.read_file("out/geojson/baumveraenderung_2015_2019__2021_2025.geojson").to_crs(25832)
v = d[d.klasse == "Verlust"].copy(); v["a"] = v.area; v = v[v.a >= 10000].sort_values("a", ascending=False).reset_index(drop=True)
def dop(y, b):
    u = ("https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=nw_hist_dop_%d&STYLES="
         "&CRS=EPSG:25832&BBOX=%f,%f,%f,%f&WIDTH=330&HEIGHT=330&FORMAT=image/jpeg" % ((y,) + b))
    return np.asarray(Image.open(io.BytesIO(requests.get(u, timeout=60).content)).convert("RGB")) / 255
def job(i):
    g = v.geometry[i]; x0, y0, x1, y1 = g.bounds; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; h = max(x1 - x0, y1 - y0) / 2 + 100; b = (cx - h, cy - h, cx + h, cy + h)
    return i, b, dop(2016, b), dop(2023, b)
with ThreadPoolExecutor(6) as ex: res = list(ex.map(job, range(len(v))))
PER = 25
for s in range(0, len(res), PER):
    chunk = res[s:s + PER]; fig, ax = plt.subplots(5, 5, figsize=(20, 11.5))
    for a in ax.flat: a.axis("off")
    for k, (i, b, a16, a23) in enumerate(chunk):
        a = ax.flat[k]; both = np.concatenate([a16, np.ones((330, 6, 3)), a23], 1); a.imshow(both, extent=(0, 666, 0, 330))
        g = v.geometry[i]
        for q in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
            xs, ys = q.exterior.xy
            for off in (0, 336): a.plot((np.array(xs) - b[0]) / (b[2] - b[0]) * 330 + off, (np.array(ys) - b[1]) / (b[3] - b[1]) * 330, color="red", lw=1)
        a.set_title(f"#{i+1}  {v.a[i]/1e4:.1f} ha   (links 2016 | rechts 2023)", fontsize=9); a.set_xlim(0, 666); a.set_ylim(0, 330)
    plt.tight_layout(); plt.savefig(f"out/report/gross_{s//PER+1}.png", dpi=62); plt.close()
v[["a", "geometry"]].to_file("data/verlust_gross.gpkg", driver="GPKG"); print(len(v), "Flaechen,", (len(v) + PER - 1) // PER, "Blaetter")
