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

def main():
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

    dimension = args.dimension
    if len(args.llist) != dimension:
        print("Error: len(llist) is not equal to dimension")
        exit(1)
    if len(args.slist) != dimension:
        print("Error: len(slist) is not equal to dimension")
        exit(1)
    label_list = args.llist
    string_list = args.slist
    surface_input_file = args.sinput
    bulk_output_file = args.boutput
    surface_output_file = args.soutput
    normalization = args.norm  # "TOTAL" or "MAX"
    Rfactor = args.rfactor  # "A":General or "B":Pendry
    experiment_first_line = args.efirst
    experiment_last_line = args.elast
    calculated_first_line = args.cfirst
    calculated_last_line = args.clast
    degree_max = args.dmax
    row_number = args.rnumber  # row number of 00 spot in .s file
    omega = args.omega  # half width of convolution

    ###### define functions ######
    def replace(fitted_x_list):
        with open("template.txt", "r") as file_input, open(surface_input_file, "w") as file_output:
            for line in file_input:
                for index in range(dimension):
                    if line.find(string_list[index]) != -1:
                        line = line.replace(string_list[index], fitted_x_list[index])
                file_output.write(line)

    def g(x):
        g = (0.939437 / omega) * np.exp(-2.77259 * (x ** 2.0 / omega ** 2.0))
        return g

    def f(x_list):
        Log_number = round(x_list[0])
        x_list = x_list[1:]
        fitted_x_list = []
        for index in range(dimension):
            if x_list[index] < 0:
                fitted_value = "%.8f" % (x_list[index])
            else:
                fitted_value = " " + "%.8f" % (x_list[index])
            fitted_value = fitted_value[: len(string_list[index])]
            fitted_x_list.append(fitted_value)
        for index in range(dimension):
            print(label_list[index], "=", fitted_x_list[index])
        replace(fitted_x_list)
        folder_name = "Log%08d" % Log_number
        os.makedirs(folder_name, exist_ok=True)
        shutil.copy("%s" % bulk_output_file, "%s/%s" % (folder_name, bulk_output_file))
        shutil.copy(
            "%s" % surface_input_file, "%s/%s" % (folder_name, surface_input_file)
        )
        os.chdir(folder_name)

        for _ in range(100):
            print("Perform surface-calculation")
            os.system("%s/surf.exe" % main_dir)

            NaN_exist = False
            with open(surface_output_file, "r") as file_check:
                lines = file_check.readlines()
                for line in lines[calculated_first_line-1:calculated_last_line]:
                        if line.find("NaN") != -1:
                            NaN_exist = True
            if not NaN_exist:
                print("PASS : %s does not have NaN." % surface_output_file)
                break
            else:
                print(
                    "WARNING : %s has NaN. Perform surface-calculation one more time."
                    % surface_output_file
                )

        ##### post procedure #####
        I_calculated_list = []
        with open(surface_output_file, "r") as file_result:
            lines = file_result.readlines()
            for line in lines[calculated_first_line-1:calculated_last_line]:
                line = line.replace(",", "").split()
                I_calculated_list.append(float(line[row_number - 1]))
            value = float(lines[calculated_last_line-1].replace(",", "").split()[0])
            if round(value, 1) == degree_max:
                print("PASS : degree_max = %s" % value)
            else:
                print("WARNING : degree_max = %s" % value)

        ##### convolution #####
        convolution_I_calculated_list = []
        for index in range(len(I_calculated_list)):
            integral = 0.0
            for index2 in range(len(I_calculated_list)):
                integral += (
                    I_calculated_list[index2]
                    * g(degree_list[index] - degree_list[index2])
                    * 0.1
                )
            convolution_I_calculated_list.append(integral)
        if len(I_calculated_list) == len(convolution_I_calculated_list):
            print(
                "PASS : len(calculated_list)%d = len(convolution_I_calculated_list)%d"
                % (len(I_calculated_list), len(convolution_I_calculated_list))
            )
        else:
            print(
                "WARNING : len(calculated_list)%d != len(convolution_I_calculated_list)%d"
                % (len(I_calculated_list), len(convolution_I_calculated_list))
            )
        #####################

        convolution_I_calculated_list_normalized = []
        if normalization == "TOTAL":
            I_calculated_total = sum(convolution_I_calculated_list)
            for i in range(len(convolution_I_calculated_list)):
                convolution_I_calculated_list_normalized.append(
                    (convolution_I_calculated_list[i]) / I_calculated_total
                )
        elif normalization == "MAX":
            I_calculated_max = max(convolution_I_calculated_list)
            for i in range(len(convolution_I_calculated_list)):
                convolution_I_calculated_list_normalized.append(
                    convolution_I_calculated_list[i] / I_calculated_max
                )

        #Calculate Rfactor
        if Rfactor == "A":
            y1 = 0.0
            for i in range(len(degree_list)):
                y1 += (I_experiment_list_normalized[i] - convolution_I_calculated_list_normalized[i]) ** 2.0
            y = np.sqrt(y1)
        elif Rfactor == "B":
            y1 = 0.0
            y2 = 0.0
            y3 = 0.0
            for i in range(len(degree_list)):
                y1 += (I_experiment_list_normalized[i] - convolution_I_calculated_list_normalized[i]) ** 2.0
                y2 += I_experiment_list_normalized[i] ** 2.0
                y3 += convolution_I_calculated_list_normalized[i] ** 2.0
            y = y1 / (y2 + y3)
        print("R-factor =", y)

        #Output numerical results
        with open("RockingCurve.txt", "w") as file_RC:
            file_RC.write("#")
            for index in range(dimension-1):
                file_RC.write("%s = %s" % (label_list[index], fitted_x_list[index]))
                file_RC.write(" ")
            file_RC.write("%s = %s\n" % (label_list[dimension-1], fitted_x_list[dimension-1]))
            file_RC.write("#R-factor = %f\n" % y)
            if normalization == "TOTAL":
                file_RC.write("#I_calculated_total=%f\n" % I_calculated_total)
                file_RC.write("#I_experiment_total=%f\n" % I_experiment_total)
            elif normalization == "MAX":
                file_RC.write("#I_calculated_max=%f\n" % I_calculated_max)
                file_RC.write("#I_experiment_max=%f\n" % I_experiment_max)
            file_RC.write(
                "#degree convolution_I_calculated I_experiment convolution_I_calculated(normalized) I_experiment(normalized) I_calculated\n"
            )
            for index in range(len(degree_list)):
                file_RC.write("{} {} {} {} {}\n".format(
                    degree_list[index],
                    convolution_I_calculated_list[index],
                    I_experiment_list[index],
                    convolution_I_calculated_list_normalized[index],
                    I_calculated_list[index]
                ))
        os.chdir(main_dir)
        return y
    ############################

    main_dir = os.getcwd()

    # Read experiment-data
    print("Read experiment.txt")
    degree_list = []
    I_experiment_list = []
    with open("experiment.txt", "r") as fp:
        lines = fp.readlines()
        for line in lines[experiment_first_line-1:experiment_last_line]:
            line = line.split()
            degree_list.append(float(line[0]))
            I_experiment_list.append(float(line[1]))

    I_experiment_list_normalized = []
    if normalization == "TOTAL":
        I_experiment_total = sum(I_experiment_list)
        for i in range(len(I_experiment_list)):
            I_experiment_list_normalized.append(
                (I_experiment_list[i]) / I_experiment_total
            )
    elif normalization == "MAX":
        I_experiment_max = max(I_experiment_list)
        for i in range(len(I_experiment_list)):
            I_experiment_list_normalized.append(I_experiment_list[i] / I_experiment_max)

    # Perform bulk-calculation
    print("Perform bulk-calculation")
    os.system("%s/bulk.exe" % main_dir)

    # Make ColorMap
    print("Read MeshData.txt")
    mesh_list = []
    with open(("MeshData.txt", "r")) as file_MD:
        for line in file_MD:
            if line[0] == "#":
                continue
            line = line.split()
            mesh = []
            for value in line:
                mesh.append(float(value))
            mesh_list.append(mesh)

    # print("check read mesh")
    # for mesh in mesh_list:
    #    print(mesh)

    print("Make ColorMap")
    fx_list = []
    file_CM = open("ColorMap.txt", "w")
    file_CM.write("#")
    for label in label_list:
        file_CM.write("%s " % label)
    file_CM.write("R-factor\n")
    iterations = len(mesh_list)
    iteration_count = 0
    for mesh in mesh_list:
        iteration_count += 1
        print("Iteration : %d/%d" % (iteration_count, iterations))
        print("mesh before:", mesh)
        for value in mesh[1:]:
            file_CM.write("%f " % value)
        fx = f(mesh)
        fx_list.append(fx)
        file_CM.write("%f\n" % fx)
        print("mesh after:", mesh)
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
    file_CM.write("#R-factor : %f" % fx_list[fx_order[0]])
    file_CM.write("\n")
    file_CM.write("#see Log%d" % round(mesh_list[fx_order[0]][0]))
    file_CM.close()


rank = 0
size = 1
if MPI_flag:
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
maindir2 = os.getcwd()

if rank == 0:
    pieces = size
    lines = []
    file_input = open("MeshData.txt", "r")
    for line in file_input:
        if not line[0] == "#":
            lines.append(line)
    file_input.close()

    total = len(lines)
    elements = total // pieces

    for index in range(pieces):
        file_output = open("devided_MeshData%08d.txt" % (index), "w")
        for index2 in range(elements):
            file_output.write(lines[index2])
        del lines[0:elements]
        if index == pieces - 1:
            for index3 in range(len(lines)):
                file_output.write(lines[index3])
        file_output.close()

    for i in range(pieces):
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

# sys.stdout = open(u"output_from_rank%08d.txt"%(rank), u"w")

os.chdir("mapper%08d" % (rank))
main()

# sys.stdout.close()
# sys.stdout = sys.__stdout__

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
