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

from typing import List, Union, Dict

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

            fx_list.append([mesh[0], fx])
            # print("mesh after:", mesh)

        self.fx_list = fx_list

        if iterations > 0:
            opt_index = np.argsort(fx_list, axis=0)[0][1]
            opt_id, opt_fx = fx_list[opt_index]
            opt_mesh = self.mesh_list[opt_index]

            # assert opt_id == opt_mesh[0]

            self.opt_fx = opt_fx
            self.opt_mesh = opt_mesh

            print(f"[{self.mpirank}] minimum_value: {opt_fx:12.8e} at {opt_mesh[1:]} (mesh {opt_mesh[0]})")

        self._output_results()

        print("complete main process : rank {:08d}/{:08d}".format(self.mpirank, self.mpisize))

    def _output_results(self):
        print("Make ColorMap")
        time_sta = time.perf_counter()

        with open("ColorMap.txt", "w") as fp:
            fp.write("#" + " ".join(self.label_list) + " fval\n")

            for x, (idx, fx) in zip(self.mesh_list, self.fx_list):
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

    def _post(self) -> Dict:
        if self.mpisize > 1:
            fx_lists = self.mpicomm.allgather(self.fx_list)
            results = [v for vs in fx_lists for v in vs]
        else:
            results = self.fx_list

        if self.mpirank == 0:
            with open("ColorMap.txt", "w") as fp:
                for x, (idx, fx) in zip(self.domain.grid, results):
                    assert x[0] == idx
                    fp.write(" ".join(
                        map(lambda v: "{:8f}".format(v), (*x[1:], fx))
                    ) + "\n")

        return {}

