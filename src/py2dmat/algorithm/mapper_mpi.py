from typing import List

from io import open
import numpy as np
import os
import time

from . import algorithm

# for type hints
from ..info import Info


class Algorithm(algorithm.AlgorithmBase):
    mesh_list: List[float]

    def __init__(self, info):
        super().__init__(info=info)
        info_alg = info["algorithm"].get("param", {})
        mesh_path = info_alg.get("mesh_path", "MeshData.txt")
        self.mesh_list = self._get_mesh_list_from_file(mesh_path)

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
        super().run(run_info)
        original_dir = os.getcwd()
        os.chdir(str(self.rank))
        # Make ColorMap
        label_list = self.label_list
        dimension = self.dimension
        run = self.runner
        print("Make ColorMap")
        with open("ColorMap.txt", "w") as file_CM:
            fx_list = []
            time_sta = time.perf_counter()
            file_CM.write("#")
            for label in label_list:
                file_CM.write("{} ".format(label))
            file_CM.write("R-factor\n")
            time_end = time.perf_counter()

            run_info["log"]["time"]["run"]["file_CM"] = time_end - time_sta
            run_info["log"]["time"]["run"]["submit"] = 0.0

            mesh_list = self._get_mesh_list_from_file()
            iterations = len(mesh_list)
            for iteration_count, mesh in enumerate(mesh_list):
                print("Iteration : {}/{}".format(iteration_count + 1, iterations))
                print("mesh before:", mesh)

                time_sta = time.perf_counter()
                for value in mesh[1:]:
                    file_CM.write("{:8f} ".format(value))
                time_end = time.perf_counter()
                run_info["log"]["time"]["run"]["file_CM"] += time_end - time_sta

                # update information
                run_info["log"]["Log_number"] = round(mesh[0])
                run_info["calc"]["x_list"] = mesh[1:]
                run_info["base"]["base_dir"] = os.getcwd()

                time_sta = time.perf_counter()
                fx = run.submit(update_info=run_info)
                time_end = time.perf_counter()
                run_info["log"]["time"]["run"]["submit"] += time_end - time_sta

                fx_list.append(fx)
                time_sta = time.perf_counter()
                file_CM.write("{:8f}\n".format(fx))
                time_end = time.perf_counter()
                run_info["log"]["time"]["run"]["file_CM"] += time_end - time_sta

                print("mesh after:", mesh)

            fx_order = np.argsort(fx_list)
            minimum_point = []
            print("mesh_list[fx_order[0]]:")
            print(mesh_list[fx_order[0]])
            for index in range(1, dimension + 1):
                minimum_point.append(mesh_list[fx_order[0]][index])

            time_sta = time.perf_counter()
            file_CM.write("#Minimum point :")
            for value in minimum_point:
                file_CM.write(" {:8f}".format(value))
            file_CM.write("\n")
            file_CM.write("#R-factor : {:8f}\n".format(fx_list[fx_order[0]]))
            file_CM.write("#see Log{}\n".format(round(mesh_list[fx_order[0]][0])))
            time_end = time.perf_counter()
            run_info["log"]["time"]["run"]["file_CM"] += time_end - time_sta

        os.chdir(original_dir)
        print("complete main process : rank {:08d}/{:08d}".format(self.rank, self.size))

    def prepare(self, prepare_info):
        super().prepare(prepare_info)
        os.makedirs(str(self.rank), exist_ok=True)
        if self.rank == 0:
            lines = []
            with open("MeshData.txt", "r") as file_input:
                for line in file_input:
                    if not line.lstrip().startswith("#"):
                        lines.append(line)
            mesh_total = np.array(lines)
            mesh_divided = np.array_split(mesh_total, self.size)
            for index, mesh in enumerate(mesh_divided):
                sub_folder_name = str(index)
                with open(
                    os.path.join(sub_folder_name, "MeshData.txt"), "w"
                ) as file_output:
                    for data in mesh:
                        file_output.write(data)

    def post(self, post_info):
        super().post(post_info)
        if self.rank == 0:
            with open("ColorMap.txt", "w") as file_output:
                for i in range(self.size):
                    with open(os.path.join(str(i), "ColorMap.txt"), "r") as file_input:
                        for line in file_input:
                            line = line.lstrip()
                            if not line.startswith("#"):
                                file_output.write(line)
