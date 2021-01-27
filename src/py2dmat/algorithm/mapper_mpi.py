from pathlib import Path
from io import open
import numpy as np
import os
import time

import py2dmat


class Algorithm(py2dmat.algorithm.AlgorithmBase):
    mesh_path: Path

    def __init__(self, info: py2dmat.Info, runner: py2dmat.Runner = None) -> None:
        super().__init__(info=info, runner=runner)
        info_param = info.algorithm.get("param", {})
        self.mesh_path = self.root_dir / info_param.get("mesh_path", "MeshData.txt")

    def _run(self) -> None:
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

            self.timer["run"]["file_CM"] = time_end - time_sta
            self.timer["run"]["submit"] = 0.0

            message = py2dmat.Message([], 0, 0)
            mesh_list = np.loadtxt("MeshData.txt")
            iterations = len(mesh_list)
            for iteration_count, mesh in enumerate(mesh_list):
                print("Iteration : {}/{}".format(iteration_count + 1, iterations))
                print("mesh before:", mesh)

                time_sta = time.perf_counter()
                for value in mesh[1:]:
                    file_CM.write("{:8f} ".format(value))
                time_end = time.perf_counter()
                self.timer["run"]["file_CM"] += time_end - time_sta

                # update information
                message.step = int(mesh[0])
                message.x = mesh[1:]

                time_sta = time.perf_counter()
                fx = run.submit(message)
                time_end = time.perf_counter()
                self.timer["run"]["submit"] += time_end - time_sta

                fx_list.append(fx)
                time_sta = time.perf_counter()
                file_CM.write("{:8f}\n".format(fx))
                time_end = time.perf_counter()
                self.timer["run"]["file_CM"] += time_end - time_sta

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
            self.timer["run"]["file_CM"] += time_end - time_sta

        print(
            "complete main process : rank {:08d}/{:08d}".format(
                self.mpirank, self.mpisize
            )
        )

    def _prepare(self) -> None:
        # scatter MeshData
        if self.mpirank == 0:
            lines = []
            with open(self.mesh_path, "r") as file_input:
                for line in file_input:
                    if not line.lstrip().startswith("#"):
                        lines.append(line)
            mesh_total = np.array(lines)
            mesh_divided = np.array_split(mesh_total, self.mpisize)
            for index, mesh in enumerate(mesh_divided):
                wdir = self.output_dir / str(index)
                with open(wdir / "MeshData.txt", "w") as file_output:
                    for data in mesh:
                        file_output.write(data)

    def _post(self) -> None:
        if self.mpirank == 0:
            with open("ColorMap.txt", "w") as file_output:
                for i in range(self.mpisize):
                    with open(os.path.join(str(i), "ColorMap.txt"), "r") as file_input:
                        for line in file_input:
                            line = line.lstrip()
                            if not line.startswith("#"):
                                file_output.write(line)
