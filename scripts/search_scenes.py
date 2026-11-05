"""Listet Sentinel-2-Szenen über Wuppertal je Jahr (Earth Search, ohne Account)."""
import sys
from pystac_client import Client

BBOX = [7.00, 51.15, 7.35, 51.34]
cat = Client.open("https://earth-search.aws.element84.com/v1")
for year in sys.argv[1:]:
    for coll in ["sentinel-2-l2a", "sentinel-2-l1c"]:
        s = cat.search(collections=[coll], bbox=BBOX, datetime=f"{year}-05-01/{year}-10-31",
                       query={"eo:cloud_cover": {"lt": 30}})
        items = list(s.items())
        print(f"== {year} {coll}: {len(items)} Szenen <30% Wolken")
        for it in sorted(items, key=lambda i: i.datetime)[:40]:
            print(" ", it.datetime.date(), it.properties.get("grid:code"), f"{it.properties['eo:cloud_cover']:.1f}%", it.id)
