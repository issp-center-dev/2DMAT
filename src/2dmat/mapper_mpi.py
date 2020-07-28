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

class Surface(object):
    def __init__(self, info):
        self.info_file = info["file"]
        self.string_list = info["string_list"]
        self.surface_input_file = info["surface_input_file"]
        self.surface_output_file = info["surface_output_file"]
        self.dimension= info["dimension"]
        self.label_list = info["label_list"]
        self.bulk_output_file = info["bulk_output_file"]
        self.main_dir = info["main_dir"]
        self.omega = info["omega"]
        self.degree_max = info["degree_max"]
        self.degree_list = info["degree_list"]
        self.normalization = info["normalization"]
        self.Rfactor = info["Rfactor"]
        self.info_experiment = info["experiment"]

    def f(self, x_list):
        # Make fitted x_list and value
        # Move subdir
        fitted_x_list, fitted_value = self._prepare(x_list)
        # Run surf.exe
        print("Perform surface-calculation")
        os.system("%s/surf.exe" % self.main_dir)
        #Calculate Rfactor and Output numerical results
        Rfactor = self._post(fitted_x_list)
        return Rfactor

    #####[S] Prepare #####
    def _prepare(self, x_list):
        dimension = self.dimension
        string_list = self.string_list
        label_list = self.label_list
        bulk_output_file = self.bulk_output_file
        surface_input_file = self.surface_input_file

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
        self._replace(fitted_x_list)
        folder_name = "Log%08d" % Log_number
        os.makedirs(folder_name, exist_ok=True)
        shutil.copy("%s" % bulk_output_file, "%s/%s" % (folder_name, bulk_output_file))
        shutil.copy(
            "%s" % surface_input_file, "%s/%s" % (folder_name, surface_input_file)
        )
        os.chdir(folder_name)
        return fitted_x_list, fitted_value

    def _replace(self, fitted_x_list):
        with open("template.txt", "r") as file_input, open(self.surface_input_file, "w") as file_output:
            for line in file_input:
                for index in range(self.dimension):
                    if line.find(self.string_list[index]) != -1:
                        line = line.replace(self.string_list[index], fitted_x_list[index])
                file_output.write(line)
    #####[E] Prepare #####

    #####[S] Post #####
    def _post(self, fitted_x_list):
        degree_list = self.degree_list
        normalization = self.normalization
        I_experiment_total = self.info_experiment["I_total"]
        I_experiment_list = self.info_experiment["I"]

        convolution_I_calculated_list_normalized, I_calculated_total,\
        I_calculated_list, convolution_I_calculated_list = self._calc_I_from_file()
        I_calculated_max = max(convolution_I_calculated_list)

        #Calculate Rfactor
        y = self._calc_Rfactor(convolution_I_calculated_list_normalized)
        print("R-factor =", y)

        dimension = self.dimension
        label_list = self.label_list

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
        return y
    def _g(self, x):
        g = (0.939437 / self.omega) * np.exp(-2.77259 * (x ** 2.0 / self.omega ** 2.0))
        return g

    def _calc_I_from_file(self):
        surface_output_file = self.surface_output_file
        calculated_first_line = self.info_file["calculated_first_line"]
        calculated_last_line = self.info_file["calculated_last_line"]
        row_number = self.info_file["row_number"]
        degree_max = self.degree_max
        degree_list = self.degree_list
        normalization = self.normalization

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
            degree_org = degree_list[index]
            for index2 in range(len(I_calculated_list)):
                integral += (I_calculated_list[index2]* self._g(degree_org-degree_list[index2]) * 0.1)
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
        return convolution_I_calculated_list_normalized, I_calculated_total, I_calculated_list, convolution_I_calculated_list

    def _calc_Rfactor(self, calc_reslut):
        Rfactor = self.Rfactor
        degree_list = self.degree_list
        I_experiment_list_normalized = self.info_experiment["I_normalized"]
        if Rfactor == "A":
            y1 = 0.0
            for i in range(len(degree_list)):
                y1 += (I_experiment_list_normalized[i] - calc_reslut[i]) ** 2.0
            y = np.sqrt(y1)
        elif Rfactor == "B":
            y1 = 0.0
            y2 = 0.0
            y3 = 0.0
            for i in range(len(degree_list)):
                y1 += (I_experiment_list_normalized[i] - calc_reslut[i]) ** 2.0
                y2 += I_experiment_list_normalized[i] ** 2.0
                y3 += calc_reslut[i] ** 2.0
            y = y1 / (y2 + y3)
        return y
    #####[E] Post #####

def get_info(args):
    if len(args.llist) != args.dimension:
        print("Error: len(llist) is not equal to dimension")
        exit(1)
    if len(args.slist) != args.dimension:
        print("Error: len(slist) is not equal to dimension")
        exit(1)

    info = {}
    info["dimension"] = args.dimension
    info["normalization"] = args.norm # "TOTAL" or "MAX"
    info["label_list"] = args.llist
    info["dimension"] = args.dimension
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
    info["omega"] = args.omega # half width of convolution
    info["main_dir"] = os.getcwd()

    # Read experiment-data
    print("Read experiment.txt")
    degree_list = []
    I_experiment_list = []
    experiment_first_line = args.efirst
    experiment_last_line = args.elast
    with open("experiment.txt", "r") as fp:
        lines = fp.readlines()
        for line in lines[experiment_first_line-1:experiment_last_line]:
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

    info["experiment"]={}
    info["experiment"]["I"] = I_experiment_list
    info["experiment"]["I_normalized"] = I_experiment_list_normalized
    info["experiment"]["I_total"] = I_experiment_total
    return info

def get_mesh_list_from_file(filename = "MeshData.txt"):
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
    # Perform bulk-calculation
    # print("Perform bulk-calculation")
    # os.system("%s/bulk.exe" % main_dir)

    solver = Surface(info)
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
            print("Iteration : %d/%d" % (iteration_count+1, iterations))
            print("mesh before:", mesh)
            for value in mesh[1:]:
                file_CM.write("%f " % value)
            fx = solver.f(mesh)
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

    #Mesh data is devided.
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
    os.system("cp ../bulkP.b ./")

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