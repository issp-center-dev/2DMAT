from sys import exit

import py2dmat
import py2dmat.mpi

try:
    from tomli import load as toml_load
except ImportError:
    try:
        from toml import load as toml_load
        if py2dmat.mpi.rank() == 0:
            print("WARNING: tomli is not found and toml is found.")
            print("         use of toml package is left for compatibility.")
            print("         please install tomli package.")
            print("HINT: python3 -m pip install tomli")
            print()
    except ImportError:
        if py2dmat.mpi.rank() == 0:
            print("ERROR: tomli is not found")
            print("HINT: python3 -m pip install tomli")
        exit(1)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Data-analysis software of quantum beam "
            "diffraction experiments for 2D material structure"
        )
    )
    parser.add_argument("inputfile", help="input file with TOML format")
    parser.add_argument("--version", action="version", version=py2dmat.__version__)

    args = parser.parse_args()

    file_name = args.inputfile
    inp = {}
    if py2dmat.mpi.rank() == 0:
        with open(file_name) as f:
            inp = toml_load(f)
    if py2dmat.mpi.size() > 1:
        inp = py2dmat.mpi.comm().bcast(inp, root=0)
    info = py2dmat.Info(inp)

    algname = info.algorithm["name"]
    if algname == "mapper":
        from .algorithm.mapper_mpi import Algorithm
    elif algname == "minsearch":
        from .algorithm.min_search import Algorithm
    elif algname == "exchange":
        from .algorithm.exchange import Algorithm
    elif algname == "pamc":
        from .algorithm.pamc import Algorithm
    elif algname == "bayes":
        from .algorithm.bayes import Algorithm
    else:
        print(f"ERROR: Unknown algorithm ({algname})")
        exit(1)

    solvername = info.solver["name"]
    if solvername == "surface":
        if py2dmat.mpi.rank() == 0:
            print(
                'WARNING: solver name "surface" is deprecated and will be unavailable in future.'
                ' Use "sim-trhepd-rheed" instead.'
            )
        from .solver.sim_trhepd_rheed import Solver
    elif solvername == "sim-trhepd-rheed":
        from .solver.sim_trhepd_rheed import Solver
    elif solvername == "sxrd":
        from .solver.sxrd import Solver
    elif solvername == "analytical":
        from .solver.analytical import Solver
    else:
        print(f"ERROR: Unknown solver ({solvername})")
        exit(1)

    solver = Solver(info)
    runner = py2dmat.Runner(solver, info)
    alg = Algorithm(info, runner)
    alg.main()
