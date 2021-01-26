from sys import exit, argv
import toml

import py2dmat
import py2dmat.runner


def main():
    if len(argv) != 2:
        print(f"Usage: python3 {argv[0]} <toml_file_name>.")
        exit(1)

    file_name = argv[1]
    info = py2dmat.Info(toml.load(file_name))
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

    solver = Solver(info)
    runner = py2dmat.runner.Runner(solver)
    alg = Algorithm(info)
    alg.set_runner(runner)
    alg.main()
