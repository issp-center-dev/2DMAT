import os
from sys import exit
import time
import toml


from . import mpi
from .info import Info
from .solver import factory as SolverFactory
from .runner import runner as Runner


def main():
    import sys

    if len(sys.argv) != 2:
        print("Usage: python3 main.py <toml_file_name>.")
        exit(1)

    file_name = sys.argv[1]
    maindir = os.getcwd()
    info = Info(toml.load(file_name))
    method = info["algorithm"]["name"]

    require_MPI = False

    # Define algorithm
    if method == "mapper":
        from .algorithm import mapper_mpi as algorithm
    elif method == "minsearch":
        from .algorithm import min_search as algorithm
    elif method == "exchange":
        from .algorithm import exchange as algorithm

        require_MPI = True
    elif method == "bayes":
        from .algorithm import bayes as algorithm
    else:
        print(f"ERROR: Unknown method ({method})")
        exit(1)

    # Get parameters
    info["mpi"] = {"comm": mpi.comm(), "size": mpi.size(), "rank": mpi.rank()}
    if require_MPI and not mpi.enabled():
        print(
            f"ERROR: algorithm '{method}' requires mpi4py, but mpi4py cannot be imported"
        )
        exit(1)

    if method != "minsearch" and method != "bayes":
        for idx in range(mpi.size()):
            sub_folder_name = str(idx)
            os.makedirs(sub_folder_name, exist_ok=True)

    factory = SolverFactory.SolverFactory()
    solver = factory.solver(info["solver"]["name"], info)
    runner = Runner.Runner(solver, info["mpi"])
    alg = algorithm.Algorithm(info=info, runner=runner)

    time_sta = time.perf_counter()
    alg.prepare(info)
    time_end = time.perf_counter()
    info["log"]["time"]["prepare"]["total"] = time_end - time_sta
    if mpi.size() > 1:
        info["mpi"]["comm"].Barrier()

    time_sta = time.perf_counter()
    alg.run(info)
    time_end = time.perf_counter()
    info["log"]["time"]["run"]["total"] = time_end - time_sta
    print("end of run")
    if mpi.size() > 1:
        info["mpi"]["comm"].Barrier()

    time_sta = time.perf_counter()
    alg.post(info)
    time_end = time.perf_counter()
    info["log"]["time"]["post"]["total"] = time_end - time_sta

    with open(f"time_rank{mpi.rank}.log", "w") as fw:

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
