from io import open
import numpy as np
import os
from . import algorithm


class Init_Param(algorithm.Param):
    def from_dict(cls, dict):
        # Set basic information
        info = {}
        info["base"] = {}
        info["base"]["dimension"] = dict["base"].get("dimension", 2)
        info["base"]["normalization"] = dict["base"].get("normalization", "TOTAL")
        if info["base"]["normalization"] not in ["TOTAL", "MAX"]:
            raise ValueError("normalization must be TOTAL or MAX.")
        info["base"]["label_list"] = dict["base"].get(
            "label_list", ["z1(Si)", "z2(Si)"]
        )
        info["base"]["string_list"] = dict["base"].get(
            "string_list", ["value_01", "value_02"]
        )
        info["base"]["surface_input_file"] = dict["base"].get(
            "surface_input_file", "surf.txt"
        )
        info["base"]["bulk_output_file"] = dict["base"].get(
            "bulk_output_file", "bulkP.b"
        )
        info["base"]["surface_output_file"] = dict["base"].get(
            "surface_output_file", "surf-bulkP.s"
        )
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
        info["file"]["calculated_first_line"] = dict["file"].get(
            "calculated_first_line", 5
        )
        info["file"]["calculated_last_line"] = dict["file"].get(
            "calculated_last_line", 60
        )
        info["file"]["row_number"] = dict["file"].get("row_number", 8)

        # Set experiment information
        experiment_path = dict["experiment"].get("path", "experiment.txt")
        firstline = dict["experiment"].get("first", 1)
        lastline = dict["experiment"].get("last", 56)

        # Set log information
        info["log"] = {}
        info["log"]["Log_number"] = 0
        info["log"]["time"] = {}
        info["log"]["time"]["prepare"] = {}
        info["log"]["time"]["run"] = {}
        info["log"]["time"]["post"] = {}
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
