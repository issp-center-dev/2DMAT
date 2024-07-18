import numpy as np

import py2dmat
import py2dmat.algorithm.mapper_mpi as mapper
from py2dmat.extra.function import Himmelblau

info = py2dmat.Info.from_file("input.toml")
solver = Himmelblau(info)
runner = py2dmat.Runner(solver, info)

alg = mapper.Algorithm(info, runner)
alg.main()
