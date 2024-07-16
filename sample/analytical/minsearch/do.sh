#!/bin/sh

python3 ../../../src/py2dmat_main.py input.toml

python3 ../plot_himmel.py --xcol=1 --ycol=2 --output=output/res.pdf output/SimplexData.txt
# python3 ../plot_himmel.py --xcol=1 --ycol=2 --output=output/res.png output/SimplexData.txt
