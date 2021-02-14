from pathlib import Path
from io import open
import numpy as np
import os
import time

import py2dmat


class Algorithm(py2dmat.algorithm.AlgorithmBase):
    mesh_list: np.ndarray

    def __init__(self, info: py2dmat.Info, runner: py2dmat.Runner = None) -> None:
        super().__init__(info=info, runner=runner)
        self.mesh_list, actions = self._meshgrid(info, split=True)

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
                file_CM.write(f"{label} ")
            file_CM.write("fval\n")
            time_end = time.perf_counter()

            self.timer["run"]["file_CM"] = time_end - time_sta
            self.timer["run"]["submit"] = 0.0

            message = py2dmat.Message([], 0, 0)
            iterations = len(self.mesh_list)
            for iteration_count, mesh in enumerate(self.mesh_list):
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
            print(self.mesh_list[fx_order[0]])
            for index in range(1, dimension + 1):
                minimum_point.append(self.mesh_list[fx_order[0]][index])

            time_sta = time.perf_counter()
            file_CM.write("#Minimum point :")
            for value in minimum_point:
                file_CM.write(" {:8f}".format(value))
            file_CM.write("\n")
            file_CM.write("#R-factor : {:8f}\n".format(fx_list[fx_order[0]]))
            file_CM.write("#see Log{}\n".format(round(self.mesh_list[fx_order[0]][0])))
            time_end = time.perf_counter()
            self.timer["run"]["file_CM"] += time_end - time_sta

        print(
            "complete main process : rank {:08d}/{:08d}".format(
                self.mpirank, self.mpisize
            )
        )

    def _prepare(self) -> None:
        # do nothing
        pass

    def _post(self) -> None:
        if self.mpirank == 0:
            with open("ColorMap.txt", "w") as file_output:
                for i in range(self.mpisize):
                    with open(os.path.join(str(i), "ColorMap.txt"), "r") as file_input:
                        for line in file_input:
                            line = line.lstrip()
                            if not line.startswith("#"):
                                file_output.write(line)
