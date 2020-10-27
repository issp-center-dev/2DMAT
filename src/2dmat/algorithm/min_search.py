from io import open
import subprocess
import numpy as np
import os
from . import algorithm

class Algorithm(algorithm.Algorithm):

    def run(self, run_info):
        run = self.runner
        callback_list = []
        run_info["base"]["base_dir"] = os.getcwd()
        from scipy.optimize import fmin

        def _f_calc(x_list, info, extra_data=False):
            min_list = info["param"]["min_list"]
            max_list = info["param"]["max_list"]
            unit_list = info["param"]["unit_list"]
            label_list = info["base"]["label_list"]
            dimension = info["base"]["dimension"]
            ##### judge value #####
            out_of_range = False
            for index in range(dimension):
                if x_list[index] < min_list[index] or x_list[index] > max_list[index]:
                    print(
                        "Warning: {} = {} is out of range [{}, {}].".format(
                            label_list[index], x_list[index], min_list[index], max_list[index]
                        )
                    )
                    out_of_range = True

            ##### unit modify #####
            for index in range(dimension):
                x_list[index] /= unit_list[index]
            print(len(x_list), dimension)
            if out_of_range:
                y = 100.0  # TODO: is it sufficient? -> cutoff value
            else:
                run_info["log"]["Log_number"] = run_info["log"]["Log_number"] + 1
                run_info["calc"]["x_list"] = x_list
                run_info["base"]["base_dir"] = os.getcwd()
                y = run.submit(update_info=run_info)
                # TODO: callback_list seems not to be used. -> used.
                if not extra_data:
                    callback = [run_info["log"]["Log_number"]]
                    for index in range(dimension):
                        callback.append(x_list[index])
                    callback.append(y)
                    callback_list.append(callback)
            return y

        self.xopt, self.fopt, self.itera, self.funcalls, self.warnflag, self.allvecs = fmin(
            _f_calc,
            self.initial_list,
            args=(run_info,),
            xtol=run_info["param"]["xtol"],
            ftol=run_info["param"]["ftol"],
            retall=True,
            full_output=True,
            maxiter=10000,
            maxfun=100000,
            initial_simplex=self.initial_simplex_list,
        )

        extra_data = True
        fx_for_simplex_list = []
        run_info["log"]["Log_number"] = 0
        print("iteration:", self.itera)
        print("len(allvecs):", len(self.allvecs))
        for step in range(self.itera):
            print("step:", step)
            print("allvecs[step]:", self.allvecs[step])
            fx_for_simplex_list.append(_f_calc(self.allvecs[step], run_info, extra_data))
        self.fx_for_simplex_list = fx_for_simplex_list
        self.callback_list = callback_list

        # original_dir = os.getcwd()
        # Log_number = 0
        # extra_data = False
        #
        # run_info["degree_max"] = run_info["degree_list"][-1]
        # dimension = run_info["dimension"]

    def prepare(self, prepare_info):
        # TODO: Is it right ? arg.degree_max is ignored.
        # TODO: Delete arg.degree_max
        prepare_info["base"]["degree_max"] = prepare_info["base"]["degree_list"][-1]
        dimension = prepare_info["base"]["dimension"]
        # TODO: check bulk.P exists.

        # make initial simple
        initial_simplex_list = []
        initial_list = prepare_info["param"]["initial_list"]
        initial_scale_list = prepare_info["param"]["initial_scale_list"]
        initial_simplex_list.append(initial_list)

        for index in range(dimension):
            initial_list2 = []
            for index2 in range(dimension):
                if index2 == index:
                    initial_list2.append(initial_list[index2] + initial_scale_list[index2])
                else:
                    initial_list2.append(initial_list[index2])
            initial_simplex_list.append(initial_list2)

        self.initial_list = initial_list
        self.initial_simplex_list = initial_simplex_list


    def post(self, post_info):
        dimension = post_info["base"]["dimension"]
        label_list = post_info["base"]["label_list"]
        with open("SimplexData.txt", "w") as file_SD:
            file_SD.write("#step")
            for label in label_list:
                file_SD.write(" ")
                file_SD.write(label)
            file_SD.write(" R-factor\n")
            for step in range(self.itera):
                file_SD.write(str(step))
                for v in self.allvecs[step]:
                    file_SD.write(" {}".format(v))
                file_SD.write(" {}\n".format(self.fx_for_simplex_list[step]))

        with open("History_FunctionCall.txt", "w") as file_callback:
            file_callback.write("#No")
            for label in label_list:
                file_callback.write(" ")
                file_callback.write(label)
            file_callback.write("\n")
            for callback in self.callback_list:
                for v in callback[0: dimension + 2]:
                    file_callback.write(str(v))
                    file_callback.write(" ")
                file_callback.write("\n")

        print("Current function value:", self.fopt)
        print("Iterations:", self.itera)
        print("Function evaluations:", self.funcalls)
        print("Solution:")
        for x, y in zip(label_list, self.xopt):
            print(x, "=", y)

class Init_Param(algorithm.Param):
    def from_dict(cls, dict):
        # Set basic information
        info = {}
        info["base"] = {}
        info["base"]["dimension"] = dict["base"].get("dimension", 2)
        info["base"]["normalization"] = dict["base"].get("normalization", "TOTAL")
        if info["base"]["normalization"] not in ["TOTAL", "MAX"]:
            raise ValueError("normalization must be TOTAL or MAX.")
        info["base"]["label_list"] = dict["base"].get("label_list", ["z1(Si)", "z2(Si)"])
        info["base"]["string_list"] = dict["base"].get("string_list", ["value_01", "value_02"])
        info["base"]["surface_input_file"] = dict["base"].get("surface_input_file", "surf.txt")
        info["base"]["bulk_output_file"] = dict["base"].get("bulk_output_file", "bulkP.b")
        info["base"]["surface_output_file"] = dict["base"].get("surface_output_file", "surf-bulkP.s")
        info["base"]["Rfactor_type"] = dict["base"].get("Rfactor_type", "A")
        if info["base"]["Rfactor_type"] not in ["A", "B"]:
            raise ValueError("Rfactor_type must be A or B.")
        info["base"]["omega"] = dict["base"].get("omega", 0.5)
        info["base"]["main_dir"] = dict["base"].get("main_dir", os.getcwd())
        info["base"]["degree_max"] = dict["base"].get("degree_max", 6.0)

        if len(info["base"]["label_list"]) != info["base"]["dimension"]:
            print("Error: len(label_list) is not equal to dimension")
            exit(1)
        if len(info["base"]["string_list"]) != info["base"]["dimension"]:
            print("Error: len(slstring_list) is not equal to dimension")
            exit(1)

        # Set file information
        info["file"] = {}
        info["file"]["calculated_first_line"] = dict["file"].get("calculated_first_line", 5)
        info["file"]["calculated_last_line"] = dict["file"].get("calculated_last_line", 60)
        info["file"]["row_number"] = dict["file"].get("row_number", 8)

        # Set experiment information
        experiment_path = dict["experiment"].get("path", "experiment.txt")
        firstline = dict["experiment"].get("first", 1)
        lastline = dict["experiment"].get("last", 56)

        # Set log information
        info["log"] = {}
        info["log"]["Log_number"] = 0

        # Set Default value
        info["mpi"] = {}
        info["mpi"]["comm"] = None
        info["mpi"]["nprocs_per_solver"] = None
        info["mpi"]["nthreads_per_proc"] = None

        # Set Parameters
        info["param"]={}
        dict_param = dict.get("param", {})
        info["param"]["initial_list"] = dict_param.get("initial_list", [5.25,4.25,3.50])
        info["param"]["unit_list"] = dict_param.get("unit_list", [1.0, 1.0, 1.0])
        info["param"]["min_list"] = dict_param.get("min_list", [-100.0, -100.0, -100.0])
        info["param"]["max_list"] = dict_param.get("max_list", [100.0, 100.0, 100.0])
        info["param"]["initial_scale_list"] = dict_param.get("initial_scale_list", [0.25, 0.25, 0.25])
        info["param"]["xtol"] = dict_param.get("xtol", 0.0001)
        info["param"]["ftol"] = dict_param.get("ftol", 0.0001)

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
        elif info["base"]["normalization"] == "MAX":
            I_experiment_norm = max(I_experiment_list)
        else:
            # TODO: error handling
            # TODO: redundant?
            print("ERROR: Unknown normalization", info["normalization"])
            exit(1)
        I_experiment_list_normalized = [
            I_exp / I_experiment_norm for I_exp in I_experiment_list
        ]

        info["experiment"] = {}
        info["experiment"]["I"] = I_experiment_list
        info["experiment"]["I_normalized"] = I_experiment_list_normalized
        info["experiment"]["I_norm"] = I_experiment_norm
        return info

    def from_toml(cls, file_name):
        import toml
        return cls.from_dict(toml.load(file_name))
