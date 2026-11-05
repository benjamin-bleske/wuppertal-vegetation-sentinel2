import sys, numpy as np, rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from pystac_client import Client
import planetary_computer as pc
X0,Y0,X1,Y1=354000,5663000,382000,5688000; W,H=(X1-X0)//10,(Y1-Y0)//10; TR=from_origin(X0,Y1,10,10)
cat=Client.open("https://planetarycomputer.microsoft.com/api/stac/v1",modifier=pc.sign_inplace)
for year,date in [(2015,"2015-09-11"),(2020,"2020-08-05"),(2025,"2025-08-14")]:
    with rasterio.open(f"data/composite_{year}.tif") as s: gap=s.read(6)<2
    its=[i for i in cat.search(collections=["sentinel-2-l2a"],bbox=[7.1,51.2,7.2,51.3],datetime=f"{date}/{date}").items() if "32ULB" in i.id or "31UGT" in i.id]
    if not its: print(year,date,"keine Szene"); continue
    it=its[0]
    with rasterio.open(it.assets["SCL"].href) as src, WarpedVRT(src,crs="EPSG:25832",transform=TR,width=W,height=H,resampling=Resampling.nearest,nodata=0) as v:
        scl=v.read(1)
    g=gap&(scl>0)
    h=np.bincount(scl[g],minlength=12)
    print(year,it.id,"cloud",it.properties["eo:cloud_cover"],"baseline",it.properties.get("s2:processing_baseline"))
    print("  SCL in Luecken-Pixeln:",{c:int(n) for c,n in enumerate(h) if n},"von",int(g.sum()))
