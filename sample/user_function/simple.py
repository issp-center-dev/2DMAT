import numpy as np

import py2dmat
import py2dmat.util.toml
import py2dmat.algorithm.mapper_mpi as pm_alg
import py2dmat.solver.function


def my_objective_fn(x: np.ndarray) -> float:
    return np.mean(x * x)


file_name = "input.toml"
inp = py2dmat.util.toml.load(file_name)
info = py2dmat.Info(inp)

solver = py2dmat.solver.function.Solver(info)
solver.set_function(my_objective_fn)

runner = py2dmat.Runner(solver, info)

alg = pm_alg.Algorithm(info, runner)
alg.main()
