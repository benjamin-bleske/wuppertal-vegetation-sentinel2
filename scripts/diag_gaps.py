import numpy as np, rasterio, geopandas as gpd
from rasterio.features import geometry_mask
from scipy.ndimage import label
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
city = gpd.read_file("data/wuppertal_boundary.geojson").to_crs("EPSG:25832")
fig, ax = plt.subplots(1, 3, figsize=(18, 6))
for k, y in enumerate([2015, 2020, 2025]):
    with rasterio.open(f"data/composite_{y}.tif") as s:
        n = s.read(6); tr = s.transform
    ins = geometry_mask(city.geometry, out_shape=n.shape, transform=tr, invert=True)
    gap = (n < 2) & ins
    lab, cnt = label(gap)
    sizes = np.bincount(lab.ravel())[1:]
    print(y, f"Luecken {100*gap.sum()/ins.sum():.2f}% der Stadt, {cnt} Cluster, groesste:", sorted(sizes)[-5:],
          " n_obs in Stadt: p5/p50:", np.percentile(n[ins], [5, 50]))
    ax[k].imshow(np.where(ins, np.clip(n, 0, 20), np.nan), cmap="viridis"); ax[k].set_title(f"{y} n_obs"); ax[k].axis("off")
plt.tight_layout(); plt.savefig("out/diag_nobs.png", dpi=60)
