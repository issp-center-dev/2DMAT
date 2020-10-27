from io import open
import numpy as np
import os
from . import algorithm

class Algorithm(algorithm.Algorithm):
    def _get_mesh_list_from_file(self, filename="MeshData.txt"):
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

    def run(self, run_info):
        original_dir = os.getcwd()
        rank = run_info["mpi"]["rank"]
        size = run_info["mpi"]["size"]
        os.chdir(str(rank))
        # Make ColorMap
        label_list = run_info["base"]["label_list"]
        dimension = run_info["base"]["dimension"]
        run = self.runner
        print("Make ColorMap")
        with open("ColorMap.txt", "w") as file_CM:
            fx_list = []
            file_CM.write("#")
            for label in label_list:
                file_CM.write("{} ".format(label))
            file_CM.write("R-factor\n")
            mesh_list = self._get_mesh_list_from_file()
            iterations = len(mesh_list)
            for iteration_count, mesh in enumerate(mesh_list):
                print("Iteration : {}/{}".format(iteration_count + 1, iterations))
                print("mesh before:", mesh)
                for value in mesh[1:]:
                    file_CM.write("{:8f} ".format(value))
                # update information
                run_info["log"]["Log_number"] = round(mesh[0])
                run_info["calc"]["x_list"] = mesh[1:]
                run_info["base"]["base_dir"] = os.getcwd()
                fx = run.submit(update_info=run_info)
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
        os.chdir(original_dir)
        print("complete main process : rank {:08d}/{:08d}".format(rank, size))

    def prepare(self, prepare_info):
        # Mesh data is divided.
        import shutil

        if prepare_info["mpi"]["rank"] == 0:
            size = prepare_info["mpi"]["size"]
            lines = []
            with open("MeshData.txt", "r") as file_input:
                for line in file_input:
                    if not line.lstrip().startswith("#"):
                        lines.append(line)
            mesh_total = np.array(lines)
            mesh_divided = np.array_split(mesh_total, size)
            for index, mesh in enumerate(mesh_divided):
                sub_folder_name = str(index)
                for item in [
                    "surf.exe",
                    "template.txt",
                    prepare_info["base"]["bulk_output_file"],
                ]:
                    shutil.copy(item, os.path.join(sub_folder_name, item))
                with open(
                    os.path.join(sub_folder_name, "MeshData.txt"), "w"
                ) as file_output:
                    for data in mesh:
                        file_output.write(data)

    def post(self, post_info):
        rank = post_info["mpi"]["rank"]
        size = post_info["mpi"]["size"]
        if rank == 0:
            with open("ColorMap.txt", "w") as file_output:
                for i in range(size):
                    with open(os.path.join(str(i), "ColorMap.txt"), "r") as file_input:
                        for line in file_input:
                            line = line.lstrip()
                            if not line.startswith("#"):
                                file_output.write(line)


class Init_Param(algorithm.Param):
    def from_dict(cls, dict):
        # Set basic information
        info = cls()
        info["base"] = {}
        base_arg = d.get("base", {})
        info["base"]["dimension"] = base_arg.get("dimension", 2)
        info["base"]["normalization"] = base_arg.get("normalization", "TOTAL")
        if info["base"]["normalization"] not in ["TOTAL", "MAX"]:
            raise ValueError("normalization must be TOTAL or MAX.")
        info["base"]["label_list"] = base_arg.get(
            "label_list", ["z1(Si)", "z2(Si)"]
        )
        info["base"]["string_list"] = base_arg.get(
            "string_list", ["value_01", "value_02"]
        )
        info["base"]["surface_input_file"] = base_arg.get(
            "surface_input_file", "surf.txt"
        )
        info["base"]["bulk_output_file"] = base_arg.get(
            "bulk_output_file", "bulkP.b"
        )
        info["base"]["surface_output_file"] = base_arg.get(
            "surface_output_file", "surf-bulkP.s"
        )
        info["base"]["Rfactor_type"] = base_arg.get("Rfactor_type", "A")
        if info["base"]["Rfactor_type"] not in ["A", "B"]:
            raise ValueError("Rfactor_type must be A or B.")
        info["base"]["omega"] = base_arg.get("omega", 0.5)
        info["base"]["main_dir"] = base_arg.get("main_dir", os.getcwd())
        info["base"]["degree_max"] = base_arg.get("degree_max", 6.0)

        if len(info["base"]["label_list"]) != info["base"]["dimension"]:
            raise ValueError("Error: len(label_list) is not equal to dimension")
        if len(info["base"]["string_list"]) != info["base"]["dimension"]:
            raise ValueError("Error: len(slstring_list) is not equal to dimension")

        # Set file information
        file_arg = d.get("file", {})
        info["file"] = {}
        info["file"]["calculated_first_line"] = file_arg.get(
            "calculated_first_line", 5
        )
        info["file"]["calculated_last_line"] = file_arg.get(
            "calculated_last_line", 60
        )
        info["file"]["row_number"] = file_arg.get("row_number", 8)

        # Set experiment information
        exp_arg = d.get("experiment", {})
        experiment_path = exp_arg.get("path", "experiment.txt")
        firstline = exp_arg.get("first", 1)
        lastline = exp_arg.get("last", 56)

        # Set log information
        info["log"] = {}
        info["log"]["Log_number"] = 0

        # Set Default value
        info["mpi"] = {}
        info["mpi"]["comm"] = None
        info["mpi"]["nprocs_per_solver"] = None
        info["mpi"]["nthreads_per_proc"] = None

        # Read experiment-data
        # TODO: make a function
        print("Read experiment.txt")
        degree_list = []
        I_experiment_list = []
        nline = lastline - firstline + 1
        assert nline > 0

        with open(experiment_path, "r") as fp:
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
        else: # info["base"]["normalization"] == "MAX":
            I_experiment_norm = max(I_experiment_list)
        I_experiment_list_normalized = [
            I_exp / I_experiment_norm for I_exp in I_experiment_list
        ]

        info["experiment"] = {}
        info["experiment"]["I"] = I_experiment_list
        info["experiment"]["I_normalized"] = I_experiment_list_normalized
        info["experiment"]["I_norm"] = I_experiment_norm
        return info

    @classmethod
    def from_toml(cls, file_name):
        import toml

        return cls.from_dict(toml.load(file_name))
