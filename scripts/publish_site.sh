#!/bin/bash
# Kopiert die ausgelieferten Dateien nach docs/ (GitHub Pages, Quelle: main /docs)
cd "$(dirname "$0")/.."
rm -rf docs/geojson docs/styles docs/tiles
mkdir -p docs
cp -R out/geojson docs/geojson
cp -R out/styles docs/styles
cp -R out/tiles docs/tiles
touch docs/.nojekyll
du -sh docs
