from io import open
try:
    from mpi4py import MPI
    MPI_flag = True
except ImportError:
    MPI_flag = False
import numpy as np
import os
import shutil
from argparse import ArgumentParser
import Solver_Surface as Solver
def get_info(args):
    if len(args.llist) != args.dimension:
        print("Error: len(llist) is not equal to dimension")
        exit(1)
    if len(args.slist) != args.dimension:
        print("Error: len(slist) is not equal to dimension")
        exit(1)

    info = {}
    info["dimension"] = args.dimension
    info["normalization"] = args.norm  # "TOTAL" or "MAX"
    info["label_list"] = args.llist
    info["string_list"] = args.slist
    info["surface_input_file"] = args.sinput
    info["bulk_output_file"] = args.boutput
    info["surface_output_file"] = args.soutput
    info["Rfactor"] = args.rfactor  # "A":General or "B":Pendry
    info["file"] = {}
    info["file"]["calculated_first_line"] = args.cfirst
    info["file"]["calculated_last_line"] = args.clast
    info["file"]["row_number"] = args.rnumber  # row number of 00 spot in .s file
    info["degree_max"] = args.dmax
    info["omega"] = args.omega  # half width of convolution
    info["main_dir"] = os.getcwd()

    # Read experiment-data
    print("Read experiment.txt")
    degree_list = []
    I_experiment_list = []
    experiment_first_line = args.efirst
    experiment_last_line = args.elast
    with open("experiment.txt", "r") as fp:
        lines = fp.readlines()
        for line in lines[experiment_first_line - 1:experiment_last_line]:
            line = line.split()
            degree_list.append(float(line[0]))
            I_experiment_list.append(float(line[1]))
    info["degree_list"] = degree_list

    I_experiment_list_normalized = []
    if info["normalization"] == "TOTAL":
        I_experiment_total = sum(I_experiment_list)
        for i in range(len(I_experiment_list)):
            I_experiment_list_normalized.append(
                (I_experiment_list[i]) / I_experiment_total
            )
    elif info["normalization"] == "MAX":
        I_experiment_max = max(I_experiment_list)
        for i in range(len(I_experiment_list)):
            I_experiment_list_normalized.append(I_experiment_list[i] / I_experiment_max)

    info["experiment"] = {}
    info["experiment"]["I"] = I_experiment_list
    info["experiment"]["I_normalized"] = I_experiment_list_normalized
    info["experiment"]["I_total"] = I_experiment_total
    return info


def get_mesh_list_from_file(filename="MeshData.txt"):
    print("Read MeshData.txt")
    mesh_list = []
    with open(filename, "r") as file_MD:
        for line in file_MD:
            if line[0] == "#":
                continue
            line = line.split()
            mesh = []
            for value in line:
                mesh.append(float(value))
            mesh_list.append(mesh)
    return mesh_list


def main(info):
    main_dir = info["main_dir"]
    solver = Solver.Surface(info)
    # Make ColorMap
    label_list = info["label_list"]
    dimension = info["dimension"]

    print("Make ColorMap")
    with open("ColorMap.txt", "w") as file_CM:
        fx_list = []
        file_CM.write("#")
        for label in label_list:
            file_CM.write("%s " % label)
        file_CM.write("R-factor\n")
        mesh_list = get_mesh_list_from_file()
        iterations = len(mesh_list)
        for iteration_count, mesh in enumerate(mesh_list):
            print("Iteration : %d/%d" % (iteration_count + 1, iterations))
            print("mesh before:", mesh)
            for value in mesh[1:]:
                file_CM.write("%f " % value)
            solver.set_log(round(mesh[1:][0]))
            fx = solver.f(mesh[1:])
            fx_list.append(fx)
            file_CM.write("%f\n" % fx)
            print("mesh after:", mesh)
            os.chdir(main_dir)

        fx_order = np.argsort(fx_list)
        minimum_point = []
        print("mesh_list[fx_order[0]]:")
        print(mesh_list[fx_order[0]])
        for index in range(1, dimension + 1):
            minimum_point.append(mesh_list[fx_order[0]][index])
        file_CM.write("#Minimum point :")
        for value in minimum_point:
            file_CM.write(" %f" % value)
        file_CM.write("\n")
        file_CM.write("#R-factor : %f\n" % fx_list[fx_order[0]])
        file_CM.write("#see Log%d" % round(mesh_list[fx_order[0]][0]))


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
        help="(default: %(default)s)",
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
                if not line[0] == "#":
                    lines.append(line)
        total = len(lines)
        elements = total // size

        mesh_total = np.array(lines)
        mesh_divided = np.array_split(mesh_total, size)
        for index, mesh in enumerate(mesh_divided):
            with open("devided_MeshData%08d.txt" % (index), "w") as file_output:
                for data in mesh:
                    file_output.write(data)

        for i in range(size):
            sub_folder_name = "mapper%08d" % (i)
            os.mkdir(sub_folder_name)
            for item in [
                "bulk.exe",
                "surf.exe",
                "bulk.txt",
                "template.txt",
                "experiment.txt",
            ]:
                shutil.copy(item, "%s/%s" % (sub_folder_name, item))
            shutil.copy(
                "devided_MeshData%08d.txt" % (i), "%s/MeshData.txt" % (sub_folder_name)
            )

    if MPI_flag:
        comm.Barrier()

    os.chdir("mapper%08d" % (rank))
    # Copy bulk-calculation
    os.system("cp ../{} ./".format(args.boutput))

    info = get_info(args)
    main(info)

    print("complete main process : rank%08d/%08d" % (rank, size))

    if MPI_flag:
        comm.Barrier()

    if rank == 0:
        os.chdir(maindir2)
        all_data = []
        for i in range(size):
            file_input = open("mapper%08d/ColorMap.txt" % (i), "r")
            lines = file_input.readlines()
            file_input.close()
            for line in lines:
                if line[0] == "#":
                    continue
                all_data.append(line)

        file_output = open("ColorMap.txt", "w")
        for line in all_data:
            file_output.write(line)
        file_output.close()
        print("complete")
