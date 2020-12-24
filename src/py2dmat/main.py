import os
from sys import exit
import time
import toml


from .solver import factory as SolverFactory
from .runner import runner as Runner


def main():
    import sys

    MPI_flag = False
    try:
        from mpi4py import MPI

        MPI_flag = True
    except ImportError:
        print("Warning: failed to import mpi4py")
        MPI_flag = False

    if len(sys.argv) != 2:
        print("Usage: python3 main.py <toml_file_name>.")
        exit(1)

    file_name = sys.argv[1]
    maindir = os.getcwd()
    input = toml.load(file_name)
    method = input["base"]["method"]

    # Define algorithm
    if method == "mapper":
        from .algorithm import mapper_mpi as mapper_mpi_alg

        algorithm = mapper_mpi_alg
    elif method == "min_search":
        from .algorithm import min_search as min_search_alg

        algorithm = min_search_alg
        MPI_flag = False
    elif method == "exchange":
        from .algorithm import exchange as exchange_alg

        algorithm = exchange_alg
        MPI_flag = True
    else:
        print("method:{} is not implemented.".format(method))
        exit(1)

    # Get parameters
    param = algorithm.Init_Param()
    info = param.from_toml(file_name)
    rank = 0
    size = 1
    if method != "min_search":
        if MPI_flag:
            # Get info["mpi"]
            info = algorithm.MPI_Init(info)
            size = info["mpi"]["size"]
        for idx in range(size):
            sub_folder_name = str(idx)
            os.makedirs(sub_folder_name, exist_ok=True)

    input_solver = input["solver"]
    info["solver"] = input_solver
    factory = SolverFactory.SolverFactory()
    solver = factory.solver(input_solver["type"], info)
    runner = Runner.Runner(solver, info["mpi"])
    alg = algorithm.Algorithm(Runner=runner)

    time_sta = time.perf_counter()
    alg.prepare(info)
    time_end = time.perf_counter()
    info["log"]["time"]["prepare"]["total"] = time_end - time_sta
    if MPI_flag:
        info["mpi"]["comm"].Barrier()

    time_sta = time.perf_counter()
    alg.run(info)
    time_end = time.perf_counter()
    info["log"]["time"]["run"]["total"] = time_end - time_sta
    print("end of run")
    if MPI_flag:
        info["mpi"]["comm"].Barrier()

    time_sta = time.perf_counter()
    alg.post(info)
    time_end = time.perf_counter()
    info["log"]["time"]["post"]["total"] = time_end - time_sta

    with open("time_rank{}.log".format(rank), "w") as fw:

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
