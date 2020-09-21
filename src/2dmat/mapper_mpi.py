import os
from sys import exit
import algorithm.mapper_mpi as mapper_mpi_alg

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
    param = mapper_mpi_alg.MapperMPI_Param()
    info = param.from_toml(file_name)
    rank = 0
    size = 1
    if MPI_flag:
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        # Check size ?: size * nprocs_per_solver
        size = comm.Get_size()
        info["mpi"]["comm"] = comm
        info["mpi"]["rank"] = rank
        info["mpi"]["size"] = size

    solver = Solver.sol_surface(info)
    runner = Runner.Runner(solver, info ["mpi"])
    alg = mapper_mpi_alg.MapperMPI(Runner=runner)

    #Make directories at each rank
    for idx in range(size):
        sub_folder_name = str(idx)
        os.makedirs(sub_folder_name, exist_ok=True)
    alg.prepare(info)
    if MPI_flag:
        comm.Barrier()

    alg.run(info)
    if MPI_flag:
        comm.Barrier()

    alg.post(info)
    if rank == 0:
        print("complete")
