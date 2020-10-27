import os
from sys import exit
import time
import toml

try:
    from mpi4py import MPI
    MPI_flag = True
except ImportError:
    print("Warning: failed to import mpi4py")
    MPI_flag = False

import solver.sol_surface as Solver
import runner.runner as Runner

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print ("Usage: python mapper_mpi.py toml_file_name.")
        exit(1)
    file_name = sys.argv[1]
    maindir = os.getcwd()
    dir = toml.load(file_name)
    method = dir["base"]["method"]

    #Define algorithm
    if method == "mapper":
        import algorithm.mapper_mpi as mapper_mpi_alg
        algorithm = mapper_mpi_alg
    elif method == "min_search":
        import algorithm.min_search as min_search_alg
        algorithm = min_search_alg
        MPI_flag = False
    else:
        print("method:{} is not implemented.".format(method))
        exit(1)

    #Get parameters
    param = algorithm.Init_Param()
    info = param.from_toml(file_name)
    rank = 0
    size = 1
    if method == "mapper":
        #TODO: Use MPI_INIT and Calculator_base
        if MPI_flag:
            comm = MPI.COMM_WORLD
            rank = comm.Get_rank()
            # Check size ?: size * nprocs_per_solver
            size = comm.Get_size()
            info["mpi"]["comm"] = comm
            info["mpi"]["rank"] = rank
            info["mpi"]["size"] = size
        for idx in range(size):
            sub_folder_name = str(idx)
            os.makedirs(sub_folder_name, exist_ok=True)

    solver = Solver.sol_surface(info)
    runner = Runner.Runner(solver, info ["mpi"])
    alg = algorithm.Algorithm(Runner=runner)

    time_sta = time.perf_counter()
    alg.prepare(info)
    time_end = time.perf_counter()
    info["log"]["time"]["prepare"]["total"] = time_end-time_sta
    if MPI_flag:
        comm.Barrier()

    time_sta = time.perf_counter()
    alg.run(info)
    time_end = time.perf_counter()
    info["log"]["time"]["run"]["total"] = time_end-time_sta
    if MPI_flag:
        comm.Barrier()

    time_sta = time.perf_counter()
    alg.post(info)
    time_end = time.perf_counter()
    info["log"]["time"]["post"]["total"] = time_end-time_sta

    with open("time_rank{}.log".format(rank), "w") as fw:
        def output_file(type):
            tmp_dict = info["log"]["time"][type]
            fw.write("#{}\n total = {} [s]\n".format(type, tmp_dict["total"]))
            for key, time in tmp_dict.items():
                if key == "total":
                    continue
                fw.write(" - {} = {}\n".format(key, time))
        output_file("prepare")
        output_file("run")
        output_file("post")
