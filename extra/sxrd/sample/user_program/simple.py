import numpy as np

import py2dmat
import py2dmat.algorithm.min_search
import sxrd

info = py2dmat.Info.from_file("input.toml")

solver = sxrd.Solver(info)
runner = py2dmat.Runner(solver, info)
alg = py2dmat.algorithm.min_search.Algorithm(info, runner)
alg.main()
