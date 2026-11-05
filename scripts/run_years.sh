#!/bin/bash
# Mosaike fuer die Zwischenjahre; zwei Laeufe parallel
cd "$(dirname "$0")/.."
(for y in 2016 2017 2018 2019; do .venv/bin/python scripts/composite.py $y > data/log_$y.txt 2>&1; echo "$y exit $?"; done) &
(for y in 2021 2022 2023 2024; do .venv/bin/python scripts/composite.py $y > data/log_$y.txt 2>&1; echo "$y exit $?"; done) &
wait
