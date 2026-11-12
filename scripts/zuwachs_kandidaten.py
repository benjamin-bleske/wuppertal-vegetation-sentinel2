"""Zuwachs-Kandidaten >= 1 ha: Flaechen, die 2015-2019 keine und 2021-2025 Baum waren (Baummaske, scripts/baummaske.py).
Nahe beieinanderliegende Teile (<= 20 m) werden zusammengefasst; die Flaeche zaehlt nur die Zuwachs-Pixel selbst.
Schreibt data/zuwachs_gross.gpkg (Spalte a = Flaeche m2), sortiert nach Flaeche. Keine Veroeffentlichung."""
import geopandas as gpd
g = gpd.read_file("out/geojson/baumveraenderung_2015_2019__2021_2025.geojson").to_crs(25832)
z = g[g.klasse == "Zuwachs"].copy()
z = z[z.geometry.area >= 400]                                   # Kleinstteile (< 4 Pixel) ignorieren
merged = gpd.GeoSeries([z.buffer(10).union_all()], crs=25832).explode(index_parts=False).reset_index(drop=True)
cl = gpd.GeoDataFrame(geometry=merged.buffer(-10)); cl = cl[~cl.geometry.is_empty].explode(index_parts=False).reset_index(drop=True)
j = gpd.sjoin(z[["geometry"]], cl.reset_index().rename(columns={"index": "cid"}), predicate="intersects")
flaeche = j.groupby("cid").apply(lambda d: d.geometry.area.sum())
cl["a"] = cl.index.map(flaeche).fillna(0)
cl = cl[cl.a >= 10000].sort_values("a", ascending=False).reset_index(drop=True)
cl.to_file("data/zuwachs_gross.gpkg", driver="GPKG")
print(len(cl), "Kandidaten >= 1 ha, zusammen", round(cl.a.sum() / 1e4), "ha; groesste", [round(x / 1e4, 1) for x in cl.a[:8]])
