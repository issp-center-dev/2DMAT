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
import time

import numpy as np
from scipy.optimize import minimize

import py2dmat
import py2dmat.domain


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

    iter_history: List[List[Union[int,float]]]
    fev_history: List[List[Union[int,float]]]

    def __init__(self, info: py2dmat.Info,
                 runner: py2dmat.Runner = None,
                 domain = None) -> None:
        super().__init__(info=info, runner=runner)

        if domain and isinstance(domain, py2dmat.domain.Region):
            self.domain = domain
        else:
            self.domain = py2dmat.domain.Region(info)

        self.min_list = self.domain.min_list
        self.max_list = self.domain.max_list
        self.unit_list = self.domain.unit_list

        self.domain.initialize(rng=self.rng, limitation=runner.limitation)
        self.initial_list = self.domain.initial_list[0]

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

        min_list = self.min_list
        max_list = self.max_list
        unit_list = self.unit_list
        label_list = self.label_list

        step = [0]
        iter_history = []
        fev_history = []

        f0 = run.submit(self.initial_list, (0, 0))
        iter_history.append([*self.initial_list, f0])

        def _cb(intermediate_result):
            x = intermediate_result.x
            fun = intermediate_result.fun
            print("eval: x={}, fun={}".format(x, fun))
            iter_history.append([*x, fun])

        def _f_calc(x_list: np.ndarray, iset) -> float:
            # check if within region -> boundary option in minimize
            # in_range = np.all((min_list < x_list) & (x_list < max_list))
            # if not in_range:
            #     print("Warning: out of range: {}".format(x_list))
            #     return float("inf")

            # check if limitation satisfied
            in_limit = self.runner.limitation.judge(x_list)
            if not in_limit:
                print("Warning: variables do not satisfy the constraint formula")
                return float("inf")

            x_list /= unit_list

            step[0] += 1
            args = (step[0], iset)
            y = run.submit(x_list, args)
            if iset == 0:
                fev_history.append([step[0], *x_list, y])
            return y

        time_sta = time.perf_counter()
        optres = minimize(
            _f_calc,
            self.initial_list,
            method="Nelder-Mead",
            args=(0,),
            bounds=[(a,b) for a,b in zip(min_list, max_list)],
            options={
                "xatol": self.xtol,
                "fatol": self.ftol,
                "return_all": True,
                "disp": True,
                "maxiter": self.maxiter,
                "maxfev": self.maxfev,
                "initial_simplex": self.initial_simplex_list,
            },
            callback=_cb,
        )

        self.xopt = optres.x
        self.fopt = optres.fun
        self.itera = optres.nit
        self.funcalls = optres.nfev
        self.allvecs = optres.allvecs
        time_end = time.perf_counter()
        self.timer["run"]["min_search"] = time_end - time_sta

        self.iter_history = iter_history
        self.fev_history = fev_history

    def _prepare(self):
        # make initial simplex
        #   [ v0, v0+a_1*e_1, v0+a_2*e_2, ... v0+a_d*e_d ]
        # where a = ( a_1 a_2 a_3 ... a_d ) and e_k is a unit vector along k-axis
        v = np.array(self.initial_list)
        a = np.array(self.initial_scale_list)
        self.initial_simplex_list = np.vstack((v, v + np.diag(a)))

    def _post(self):
        label_list = self.label_list

        with open("SimplexData.txt", "w") as fp:
            fp.write("#step " + " ".join(label_list) + " R-factor\n")
            for i, v in enumerate(self.iter_history):
                fp.write(str(i) + " " + " ".join(map(str,v)) + "\n")

        with open("History_FunctionCall.txt", "w") as fp:
            fp.write("#No " + " ".join(label_list) + "\n")
            for i, v in enumerate(self.fev_history):
                fp.write(" ".join(map(str,v)) + "\n")

        print("Current function value:", self.fopt)
        print("Iterations:", self.itera)
        print("Function evaluations:", self.funcalls)
        print("Solution:")
        for x, y in zip(label_list, self.xopt):
            print(f"{x} = {y}")

        with open("res.txt", "w") as fp:
            fp.write(f"fx = {self.fopt}\n")
            for x, y in zip(label_list, self.xopt):
                fp.write(f"{x} = {y}\n")
