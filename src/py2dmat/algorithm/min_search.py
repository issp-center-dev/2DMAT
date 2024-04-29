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

from typing import List
import time

import numpy as np
from scipy.optimize import minimize

import py2dmat


class Algorithm(py2dmat.algorithm.AlgorithmBase):

    # inputs
    label_list: np.ndarray
    initial_list: np.ndarray
    min_list: np.ndarray
    max_list: np.ndarray
    unit_list: np.ndarray

    # hyperparameters of Nelder-Mead
    initial_simplex_list: List[List[float]]
    xtol: float
    ftol: float

    # results
    xopt: np.ndarray
    fopt: float
    itera: int
    funcalls: int
    allvecs: List[np.ndarray]
    fx_for_simplex_list: List[float]
    callback_list: List[List[int]]

    def __init__(self, info: py2dmat.Info, runner: py2dmat.Runner = None) -> None:
        super().__init__(info=info, runner=runner)

        (
            self.initial_list,
            self.min_list,
            self.max_list,
            self.unit_list,
        ) = self._read_param(info)
        self.initial_list = self.initial_list.flatten()

        info_minimize = info.algorithm.get("minimize", {})
        self.initial_scale_list = info_minimize.get(
            "initial_scale_list", [0.25] * self.dimension
        )
        self.xtol = info_minimize.get("xatol", 0.0001)
        self.ftol = info_minimize.get("fatol", 0.0001)
        self.maxiter = info_minimize.get("maxiter", 10000)
        self.maxfev = info_minimize.get("maxfev", 100000)

    def _run(self) -> None:
        run = self.runner
        callback_list = []

        min_list = self.min_list
        max_list = self.max_list
        unit_list = self.unit_list
        label_list = self.label_list
        dimension = self.dimension

        step = [0]

        def _f_calc(x_list: np.ndarray, extra_data: bool = False) -> float:
            out_of_range = False
            for index in range(dimension):
                if x_list[index] < min_list[index] or x_list[index] > max_list[index]:
                    print(
                        "Warning: {} = {} is out of range [{}, {}].".format(
                            label_list[index],
                            x_list[index],
                            min_list[index],
                            max_list[index],
                        )
                    )
                    out_of_range = True
            
            if not self.runner.limitation.judge(x_list):
                msg ="Warning: "
                msg+="Variables do not satisfy the constraint formula.\n"
                for index in range(dimension):
                    msg+="{} = {}\n".format(label_list[index],x_list[index])
                print(msg,end="")
                out_of_range = True

            for index in range(dimension):
                x_list[index] /= unit_list[index]
            y = float("inf")
            if not out_of_range:
                step[0] += 1
                set = 1 if extra_data else 0
                args = (step[0], set)
                y = run.submit(x_list, args)
                if not extra_data:
                    callback_list.append([step[0], *x_list, y])
            return y

        time_sta = time.perf_counter()
        optres = minimize(
            _f_calc,
            self.initial_list,
            method="Nelder-Mead",
            options={
                "xatol": self.xtol,
                "fatol": self.ftol,
                "return_all": True,
                "disp": True,
                "maxiter": self.maxiter,
                "maxfev": self.maxfev,
                "initial_simplex": self.initial_simplex_list,
            },
        )
        self.xopt = optres.x
        self.fopt = optres.fun
        self.itera = optres.nit
        self.funcalls = optres.nfev
        self.allvecs = optres.allvecs
        time_end = time.perf_counter()
        self.timer["run"]["min_search"] = time_end - time_sta

        extra_data = True
        fx_for_simplex_list = []
        step[0] = 0
        print("iteration:", self.itera)
        print("len(allvecs):", len(self.allvecs))

        time_sta = time.perf_counter()
        for _ in range(self.itera):
            print("step:", step[0])
            print("allvecs[step]:", self.allvecs[step[0]])
            fx_for_simplex_list.append(_f_calc(self.allvecs[step[0]], extra_data))
        time_end = time.perf_counter()
        self.timer["run"]["recalc"] = time_end - time_sta

        self.fx_for_simplex_list = fx_for_simplex_list
        self.callback_list = callback_list

    def _prepare(self):
        # make initial simplex
        initial_simplex_list = []
        initial_list = self.initial_list
        initial_scale_list = self.initial_scale_list
        initial_simplex_list.append(initial_list)

        for index in range(self.dimension):
            initial_list2 = []
            for index2 in range(self.dimension):
                if index2 == index:
                    initial_list2.append(
                        initial_list[index2] + initial_scale_list[index2]
                    )
                else:
                    initial_list2.append(initial_list[index2])
            initial_simplex_list.append(initial_list2)

        self.initial_list = initial_list
        self.initial_simplex_list = initial_simplex_list

    def _post(self):
        dimension = self.dimension
        label_list = self.label_list
        with open("SimplexData.txt", "w") as file_SD:
            file_SD.write("#step")
            for label in label_list:
                file_SD.write(" ")
                file_SD.write(label)
            file_SD.write(" R-factor\n")
            for step in range(self.itera):
                file_SD.write(str(step))
                for v in self.allvecs[step]:
                    file_SD.write(f" {v}")
                file_SD.write(f" {self.fx_for_simplex_list[step]}\n")

        with open("History_FunctionCall.txt", "w") as file_callback:
            file_callback.write("#No")
            for label in label_list:
                file_callback.write(" ")
                file_callback.write(label)
            file_callback.write("\n")
            for callback in self.callback_list:
                for v in callback[0 : dimension + 2]:
                    file_callback.write(str(v))
                    file_callback.write(" ")
                file_callback.write("\n")

        print("Current function value:", self.fopt)
        print("Iterations:", self.itera)
        print("Function evaluations:", self.funcalls)
        print("Solution:")
        for x, y in zip(label_list, self.xopt):
            print(x, "=", y)
        with open("res.txt", "w") as f:
            f.write(f"fx = {self.fopt}\n")
            for x, y in zip(label_list, self.xopt):
                f.write(f"{x} = {y}\n")
