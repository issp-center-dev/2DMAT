import numpy as np

import py2dmat
import py2dmat.algorithm.min_search as min_search
from booth import Booth

info = py2dmat.Info.from_file("input.toml")
solver = Booth(info)
runner = py2dmat.Runner(solver, info)

alg = min_search.Algorithm(info, runner)
alg.main()
