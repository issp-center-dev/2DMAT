import os
import shutil
from argparse import ArgumentParser
from io import open
from sys import exit

import numpy as np

try:
    from mpi4py import MPI

    MPI_flag = True
except ImportError:
    print("Warning: failed to import mpi4py")
    MPI_flag = False

import solver.sol_surface as Solver
import runner.runner as Runner

def get_info(args):
    if len(args.llist) != args.dimension:
        print("Error: len(llist) is not equal to dimension")
        exit(1)
    if len(args.slist) != args.dimension:
        print("Error: len(slist) is not equal to dimension")
        exit(1)

    info = {}
    info["base"] = {}
    info["base"]["dimension"] = args.dimension
    info["base"]["normalization"] = args.norm  # "TOTAL" or "MAX"
    info["base"]["label_list"] = args.llist
    info["base"]["string_list"] = args.slist
    info["base"]["surface_input_file"] = args.sinput
    info["base"]["bulk_output_file"] = args.boutput
    info["base"]["surface_output_file"] = args.soutput
    info["base"]["Rfactor_type"] = args.rfactor  # "A":General or "B":Pendry
    info["base"]["omega"] = args.omega  # half width of convolution
    info["base"]["main_dir"] = os.getcwd()
    info["file"] = {}
    info["file"]["calculated_first_line"] = args.cfirst
    info["file"]["calculated_last_line"] = args.clast
    info["file"]["row_number"] = args.rnumber  # row number of 00 spot in .s file
    info["base"]["degree_max"] = args.dmax
    info["log"] = {}
    info["log"]["Log_number"] = 0

    # Read experiment-data
    # TODO: make a function
    print("Read experiment.txt")
    degree_list = []
    I_experiment_list = []
    firstline = args.efirst
    lastline = args.elast
    nline = lastline - firstline + 1
    assert nline > 0

    with open("experiment.txt", "r") as fp:
        for _ in range(firstline - 1):
            fp.readline()
        for _ in range(nline):
            line = fp.readline()
            words = line.split()
            degree_list.append(float(words[0]))
            I_experiment_list.append(float(words[1]))
    info["base"]["degree_list"] = degree_list

    if info["base"]["normalization"] == "TOTAL":
        I_experiment_norm = sum(I_experiment_list)
    elif info["base"]["normalization"] == "MAX":
        I_experiment_norm = max(I_experiment_list)
    else:
        # TODO: error handling
        # TODO: redundant?
        print("ERROR: Unknown normalization", info["normalization"])
        exit(1)
    I_experiment_list_normalized = [
        I_exp / I_experiment_norm for I_exp in I_experiment_list
    ]

    info["experiment"] = {}
    info["experiment"]["I"] = I_experiment_list
    info["experiment"]["I_normalized"] = I_experiment_list_normalized
    info["experiment"]["I_norm"] = I_experiment_norm
    return info


def get_mesh_list_from_file(filename="MeshData.txt"):
    print("Read", filename)
    mesh_list = []
    with open(filename, "r") as file_MD:
        for line in file_MD:
            line = line.lstrip()
            if line.startswith("#"):
                continue
            mesh = []
            for value in line.split():
                mesh.append(float(value))
            mesh_list.append(mesh)
    return mesh_list


def main(info):
    solver = Solver.sol_surface(info)
    # Make ColorMap
    label_list = info["base"]["label_list"]
    dimension = info["base"]["dimension"]
    mpi_info = info ["mpi"]

    run = Runner.Runner(solver, mpi_info)
    print("Make ColorMap")
    with open("ColorMap.txt", "w") as file_CM:
        fx_list = []
        file_CM.write("#")
        for label in label_list:
            file_CM.write("{} ".format(label))
        file_CM.write("R-factor\n")
        mesh_list = get_mesh_list_from_file()
        iterations = len(mesh_list)
        for iteration_count, mesh in enumerate(mesh_list):
            print("Iteration : {}/{}".format(iteration_count + 1, iterations))
            print("mesh before:", mesh)
            for value in mesh[1:]:
                file_CM.write("{:8f} ".format(value))
            #update information
            info["log"]["Log_number"] = round(mesh[0])
            info["calc"]["x_list"] = mesh[1:]
            info["base"]["base_dir"] = os.getcwd()
            print(info["base"]["base_dir"])
            #update_info = solver.input.update_info(info)
            #solver.output.update_info(update_info)
            fx = run.submit(update_info=info)
            ##Run surf.exe
            #solver.run()
            #fx = solver.output.get_results()
            fx_list.append(fx)
            file_CM.write("{:8f}\n".format(fx))
            print("mesh after:", mesh)

        fx_order = np.argsort(fx_list)
        minimum_point = []
        print("mesh_list[fx_order[0]]:")
        print(mesh_list[fx_order[0]])
        for index in range(1, dimension + 1):
            minimum_point.append(mesh_list[fx_order[0]][index])
        file_CM.write("#Minimum point :")
        for value in minimum_point:
            file_CM.write(" {:8f}".format(value))
        file_CM.write("\n")
        file_CM.write("#R-factor : {:8f}\n".format(fx_list[fx_order[0]]))
        file_CM.write("#see Log{}\n".format(round(mesh_list[fx_order[0]][0])))


if __name__ == "__main__":
    ###### Parameter Settings ######
    parser = ArgumentParser()
    parser.add_argument(
        "--dimension", type=int, default=2, help="(default: %(default)s)"
    )
    parser.add_argument(
        "--llist",
        type=str,
        nargs="*",
        default=["z1(Si)", "z2(Si)"],
        help="(default: %(default)s)",
    )
    parser.add_argument(
        "--slist",
        type=str,
        nargs="*",
        default=["value_01", "value_02"],
        help="(default: %(default)s)",
    )
    parser.add_argument(
        "--sinput", type=str, default="surf.txt", help="(default: %(default)s)"
    )
    parser.add_argument(
        "--boutput", type=str, default="bulkP.b", help="(default: %(default)s)"
    )
    parser.add_argument(
        "--soutput", type=str, default="surf-bulkP.s", help="(default: %(default)s)"
    )
    parser.add_argument(
        "--norm",
        type=str,
        default="TOTAL",
        choices=["TOTAL", "MAX"],
        help="(default: %(default)s)",
    )
    parser.add_argument(
        "--rfactor",
        type=str,
        default="A",
        choices=["A", "B"],
        help="type of R factor(default: %(default)s)",
    )
    parser.add_argument("--efirst", type=int, default=1, help="(default: %(default)s)")
    parser.add_argument("--elast", type=int, default=56, help="(default: %(default)s)")
    parser.add_argument("--cfirst", type=int, default=5, help="(default: %(default)s)")
    parser.add_argument("--clast", type=int, default=60, help="(default: %(default)s)")
    parser.add_argument(
        "--dmax", type=float, default=6.0, help="(default: %(default)s)"
    )
    parser.add_argument("--rnumber", type=int, default=8, help="(default: %(default)s)")
    parser.add_argument(
        "--omega", type=float, default=0.5, help="(default: %(default)s)"
    )
    args = parser.parse_args()

    rank = 0
    size = 1
    if MPI_flag:
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()
    maindir2 = os.getcwd()

    # Mesh data is devided.
    if rank == 0:
        lines = []
        with open("MeshData.txt", "r") as file_input:
            for line in file_input:
                if not line.lstrip().startswith("#"):
                    lines.append(line)

        mesh_total = np.array(lines)
        mesh_divided = np.array_split(mesh_total, size)
        for index, mesh in enumerate(mesh_divided):
            with open("devided_MeshData{:08d}.txt".format(index), "w") as file_output:
                for data in mesh:
                    file_output.write(data)

        for i in range(size):
            sub_folder_name = "mapper{:08d}".format(i)
            os.mkdir(sub_folder_name)
            for item in [
                "surf.exe",
                "template.txt",
                "experiment.txt",
                args.boutput,
            ]:
                shutil.copy(item, os.path.join(sub_folder_name, item))
            shutil.copy(
                "devided_MeshData{:08d}.txt".format(i),
                os.path.join(sub_folder_name, "MeshData.txt"),
            )

    if MPI_flag:
        comm.Barrier()

    os.chdir("mapper{:08d}".format(rank))

    info = get_info(args)
    info["mpi"]={}
    info["mpi"]["comm"] = comm
    info["mpi"]["nprocs_per_solver"] = None
    info["mpi"]["nthreads_per_proc"] = None
    main(info)

    print("complete main process : rank {:08d}/{:08d}".format(rank, size))

    if MPI_flag:
        comm.Barrier()

    # gather colormaps
    if rank == 0:
        os.chdir(maindir2)
        all_data = []
        with open("ColorMap.txt", "w") as file_output:
            for i in range(size):
                with open(
                    os.path.join("mapper{:08d}".format(i), "ColorMap.txt"), "r"
                ) as file_input:
                    for line in file_input:
                        line = line.lstrip()
                        if not line.startswith("#"):
                            file_output.write(line)
        print("complete")
