#!/bin/sh

mpiexec -np 4 python3 ../../../src/py2dmat_main.py input.toml
python3 ./plot_colormap_2d.py
