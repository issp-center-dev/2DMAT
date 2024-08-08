import numpy as np

import py2dmat
import py2dmat.algorithm.mapper_mpi as mapper
import function

info = py2dmat.Info.from_file("input.toml")
solver = function.Himmelblau(info)
runner = py2dmat.Runner(solver, info)

alg = mapper.Algorithm(info, runner)
alg.main()
