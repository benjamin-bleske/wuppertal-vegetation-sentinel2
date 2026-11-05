from pystac_client import Client
BBOX = [7.00, 51.15, 7.35, 51.34]
for name, url, colls in [
    ("EarthSearch", "https://earth-search.aws.element84.com/v1", ["sentinel-2-l1c","sentinel-2-l2a"]),
    ("PlanetaryComputer", "https://planetarycomputer.microsoft.com/api/stac/v1", ["sentinel-2-l2a"]),
    ("CDSE", "https://stac.dataspace.copernicus.eu/v1", ["sentinel-2-l1c","sentinel-2-l2a"]),
]:
    try:
        cat = Client.open(url)
    except Exception as e:
        print(name, "ERR", e); continue
    for c in colls:
        try:
            items = list(cat.search(collections=[c], bbox=BBOX, datetime="2015-06-01/2016-12-31", max_items=500).items())
        except Exception as e:
            print(name, c, "ERR", str(e)[:100]); continue
        print(f"== {name} {c}: {len(items)}")
        for it in sorted(items, key=lambda i: i.datetime)[:25]:
            print("  ", it.datetime.date(), f"{it.properties.get('eo:cloud_cover', -1):.1f}%", it.id)
