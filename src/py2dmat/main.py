import os
from sys import exit
import time
import toml

from typing import Optional

from . import mpi
from .info import Info
from .algorithm.algorithm import AlgorithmBase
from .solver.solver_base import SolverBase
from .runner.runner import Runner


def main(
    algorithm: AlgorithmBase,
    solver: SolverBase,
    info: Info,
    runner: Optional[Runner] = None,
):
    if runner is None:
        runner = Runner(solver, info)
    algorithm.set_runner(runner)

    time_sta = time.perf_counter()
    algorithm.prepare(info)
    time_end = time.perf_counter()
    info["log"]["time"]["prepare"]["total"] = time_end - time_sta
    if mpi.size() > 1:
        mpi.comm().Barrier()

    time_sta = time.perf_counter()
    algorithm.run(info)
    time_end = time.perf_counter()
    info["log"]["time"]["run"]["total"] = time_end - time_sta
    print("end of run")
    if mpi.size() > 1:
        mpi.comm().Barrier()

    time_sta = time.perf_counter()
    algorithm.post(info)
    time_end = time.perf_counter()
    info["log"]["time"]["post"]["total"] = time_end - time_sta

    with open(f"time_rank{mpi.rank()}.log", "w") as fw:

        def output_file(type):
            tmp_dict = info["log"]["time"][type]
            fw.write("#{}\n total = {} [s]\n".format(type, tmp_dict["total"]))
            for key, t in tmp_dict.items():
                if key == "total":
                    continue
                fw.write(" - {} = {}\n".format(key, t))

        output_file("prepare")
        output_file("run")
        output_file("post")


def main_script():
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 main.py <toml_file_name>.")
        exit(1)

    file_name = sys.argv[1]
    info = Info(toml.load(file_name))
    algname = info["algorithm"]["name"]

    # Define algorithm
    if algname == "mapper":
        from .algorithm.mapper_mpi import Algorithm
    elif algname == "minsearch":
        from .algorithm.min_search import Algorithm
    elif algname == "exchange":
        from .algorithm.exchange import Algorithm
    elif algname == "bayes":
        from .algorithm.bayes import Algorithm
    else:
        print(f"ERROR: Unknown algorithm ({algname})")
        exit(1)

    solvername = info["solver"]["name"]
    if solvername == "surface":
        from .solver.surface import Solver
    elif solvername == "analytical":
        from .solver.analytical import Solver
    else:
        print(f"ERROR: Unknown solver ({solvername})")
        exit(1)

    alg = Algorithm(info)
    solver = Solver(info)

    main(alg, solver, info)
