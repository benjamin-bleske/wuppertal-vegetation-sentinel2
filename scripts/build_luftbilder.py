"""Styles fuer historische Luftbilder (WMS NW Hist DOP, Geobasis NRW) in den Jahrgaengen, die Wuppertal abdecken."""
import json
from build_styles import style

WMS = ("https://www.wms.nrw.de/geobasis/wms_nw_hist_dop?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=nw_hist_dop_{y}"
       "&STYLES=&CRS=EPSG:3857&BBOX={{bbox-epsg-3857}}&WIDTH=256&HEIGHT=256&FORMAT=image/jpeg")
YEARS = [2010, 2013, 2016, 2019, 2021, 2023]      # Wuppertal-Abdeckung per GetMap geprueft; andere Jahre sind dort leer

for y in YEARS:
    s = style(f"luftbild_{y}", f"Luftbild {y} (Geobasis NRW, historische DOP)",
              f"Digitales Orthophoto {y} aus dem WMS NW Hist DOP. Die Befliegung deckt nicht jedes Jahr ganz NRW ab; "
              f"fuer Wuppertal liegen Bilder aus {', '.join(map(str, YEARS))} vor. Zum Vergleich mit den Vegetationslayern "
              "(Bildflugzeitpunkt und Laubzustand weichen vom Sentinel-Sommermosaik ab). Quelle: Geobasis NRW, dl-de/zero-2-0.",
              ["Luftbild", "Orthophoto", str(y)],
              {f"dop{y}": {"type": "raster", "tiles": [WMS.format(y=y)], "tileSize": 256,
                           "attribution": "Geobasis NRW (dl-de/zero-2-0)"}},
              [{"id": f"dop{y}-raster", "type": "raster", "source": f"dop{y}"}])
    json.dump(s, open(f"out/styles/luftbild_{y}.style.json", "w"), ensure_ascii=False, indent=1)
print(YEARS)
