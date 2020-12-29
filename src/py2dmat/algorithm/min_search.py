from typing import List, MutableMapping

import os
import time

import numpy as np
from scipy.optimize import minimize

from . import algorithm

# for type hints
from ..info import Info


class Algorithm(algorithm.Algorithm):

    # inputs
    label_list: List[str]
    initial_list: List[float]
    min_list: List[float]
    max_list: List[float]
    unit_list: List[float]

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

    def __init__(self, info: Info, runner) -> None:
        super().__init__(info=info, runner=runner)

        info_alg = info["algorithm"]

        # TODO: change default values
        # TODO: error check
        
        info_param = info_alg.get("param", {})
        self.initial_list = info_param.get("initial_list", [5.25, 4.25, 3.50])
        self.unit_list = info_param.get("unit_list", [1.0, 1.0, 1.0])
        self.min_list = info_param.get("min_list", [-100.0, -100.0, -100.0])
        self.max_list = info_param.get("max_list", [100.0, 100.0, 100.0])

        info_minimize = info_alg.get("minimize", {})
        self.initial_scale_list = info_minimize.get("initial_scale_list", [0.25, 0.25, 0.25])
        self.xtol = info_minimize.get("xatol", 0.0001)
        self.ftol = info_minimize.get("fatol", 0.0001)
        self.maxiter = info_minimize.get("maxiter", 10000)
        self.maxfev = info_minimize.get("maxfev", 100000)


    def run(self, run_info: Info) -> None:
        run = self.runner
        callback_list = []
        run_info["base"]["base_dir"] = os.getcwd()

        min_list = self.min_list
        max_list = self.max_list
        unit_list = self.unit_list
        label_list = self.label_list
        dimension = self.dimension

        def _f_calc(
            x_list: np.ndarray, info: Info, extra_data: bool = False
        ) -> float:

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

            for index in range(dimension):
                x_list[index] /= unit_list[index]
            if out_of_range:
                y = 100.0
            else:
                run_info["log"]["Log_number"] += 1
                run_info["log"]["ExtraRun"] = extra_data
                run_info["calc"]["x_list"] = x_list
                run_info["base"]["base_dir"] = os.getcwd()
                y = run.submit(update_info=run_info)
                if not extra_data:
                    callback = [run_info["log"]["Log_number"]]
                    for index in range(dimension):
                        callback.append(x_list[index])
                    callback.append(y)
                    callback_list.append(callback)
            return y

        time_sta = time.perf_counter()
        optres = minimize(
            _f_calc,
            self.initial_list,
            args=(run_info,),
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
        run_info["log"]["time"]["run"]["min_search"] = time_end - time_sta

        extra_data = True
        fx_for_simplex_list = []
        run_info["log"]["Log_number"] = 0
        print("iteration:", self.itera)
        print("len(allvecs):", len(self.allvecs))

        time_sta = time.perf_counter()
        for step in range(self.itera):
            print("step:", step)
            print("allvecs[step]:", self.allvecs[step])
            fx_for_simplex_list.append(
                _f_calc(self.allvecs[step], run_info, extra_data)
            )
        time_end = time.perf_counter()
        run_info["log"]["time"]["run"]["recalc"] = time_end - time_sta

        self.fx_for_simplex_list = fx_for_simplex_list
        self.callback_list = callback_list

    def prepare(self, prepare_info):

        # make initial simple
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

    def post(self, post_info):
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
