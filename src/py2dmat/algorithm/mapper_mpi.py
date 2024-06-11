# 2DMAT -- Data-analysis software of quantum beam diffraction experiments for 2D material structure
# Copyright (C) 2020- The University of Tokyo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

from typing import List, Union

from pathlib import Path
from io import open
import numpy as np
import os
import time

import py2dmat
import py2dmat.domain

class Algorithm(py2dmat.algorithm.AlgorithmBase):
    #mesh_list: np.ndarray
    mesh_list: List[Union[int, float]]

    def __init__(self, info: py2dmat.Info,
                 runner: py2dmat.Runner = None,
                 domain = None) -> None:
        super().__init__(info=info, runner=runner)

        if domain and isinstance(domain, py2dmat.domain.MeshGrid):
            self.domain = domain
        else:
            self.domain = py2dmat.domain.MeshGrid(info)

        self.domain.do_split()
        self.mesh_list = self.domain.grid_local


    def _run(self) -> None:
        # Make ColorMap
        label_list = self.label_list
        dimension = self.dimension
        run = self.runner

        fx_list = []
        self.timer["run"]["submit"] = 0.0

        iterations = len(self.mesh_list)
        for iteration_count, mesh in enumerate(self.mesh_list):
            print("Iteration : {}/{}".format(iteration_count + 1, iterations))
            # print("mesh before:", mesh)

            # update information
            args = (int(mesh[0]), 0)
            x = np.array(mesh[1:])

            time_sta = time.perf_counter()
            fx = run.submit(x, args)
            time_end = time.perf_counter()
            self.timer["run"]["submit"] += time_end - time_sta

            fx_list.append(fx)
            # print("mesh after:", mesh)

        self.fx_list = fx_list

        if iterations > 0:
            fx_order = np.argsort(fx_list)
            # minimum_point = []
            # print("mesh_list[fx_order[0]]:")
            # print(self.mesh_list[fx_order[0]])
            # for index in range(1, dimension + 1):
            #     minimum_point.append(self.mesh_list[fx_order[0]][index])
            opt_index = fx_order[0]
            self.opt_fx = fx_list[opt_index]
            self.opt_mesh = np.array(self.mesh_list[opt_index])

            print("minimum_point: {}".format(self.opt_mesh))
            print("minimum_value: {}".format(self.opt_fx))

        self._output_results()

        print("complete main process : rank {:08d}/{:08d}".format(self.mpirank, self.mpisize))

    def _output_results(self):
        print("Make ColorMap")

        time_sta = time.perf_counter()

        with open("ColorMap.txt", "w") as fp:
            fp.write("#" + " ".join(self.label_list) + " fval\n")

            for x, fx in zip(self.mesh_list, self.fx_list):
                fp.write(" ".join(
                    map(lambda v: "{:8f}".format(v), (*x[1:], fx))
                    ) + "\n")

            if len(self.mesh_list) > 0:
                fp.write("#Minimum point : " + " ".join(
                    map(lambda v: "{:8f}".format(v), self.opt_mesh[1:])
                ) + "\n")
                fp.write("#R-factor : {:8f}\n".format(self.opt_fx))
                fp.write("#see Log{:d}\n".format(round(self.opt_mesh[0])))
            else:
                fp.write("# No mesh point\n")

        time_end = time.perf_counter()
        self.timer["run"]["file_CM"] = time_end - time_sta

    def _prepare(self) -> None:
        # do nothing
        pass

    def _post(self) -> None:
        if self.mpisize > 1:
            fx_lists = self.mpicomm.allgather(self.fx_list)
            results = [v for vs in fx_lists for v in vs]

            mesh_lists = self.mpicomm.allgather(self.mesh_list)
            coords = [v for vs in mesh_lists for v in vs]
        else:
            results = self.fx_list
            coords = self.mesh_list

        if self.mpirank == 0:
            with open("ColorMap.txt", "w") as fp:
                for x, fx in zip(coords, results):
                    fp.write(" ".join(
                        map(lambda v: "{:8f}".format(v), (*x[1:], fx))
                    ) + "\n")
