import os
import sys
import shutil
import numpy as np

from pathlib import Path


from . import solver_base
from .. import exception

# for type hints
from typing import Dict, Optional, Any, List
from ..info import Info


class surface(solver_base.Solver_Base):
    root_dir: Path
    output_dir: Path
    path_to_solver: Path
    info_solver: Dict[str, Any]

    def __init__(self, info: Info):
        """
        Initialize the solver.

        Parameters
        ----------
        """

        self.root_dir = info["base"]["root_dir"]
        self.output_dir = info["base"]["output_dir"]

        self.info_solver = info["solver"]

        p2solver = "surf.exe"
        self.path_to_solver = self.root_dir / Path(p2solver).expanduser().resolve()
        if not self.path_to_solver.exists():
            raise exception.InputError(
                f"ERROR: solver ({self.path_to_solver}) does not exist"
            )
        self.input = surface.Input(info)
        self.output = surface.Output(info)
        self.base_info = info["base"]

    def get_run_scheme(self):
        """
        Return
        -------
        str
            run_scheme.
        """
        return "subprocess"

    def get_path_to_solver(self):
        """
        Return
        -------
        str
            Path to solver.
        """
        return str(self.path_to_solver)

    def get_name(self):
        """
        Return
        -------
        str
            surf.exe
        """
        return "surf.exe"

    class Input(object):
        """
        Input manager.

        Attributes
        ----------
        base_info : Any
            Common parameter.
        """

        root_dir: Path
        output_dir: Path
        dimension: int
        string_list: List[str]
        bulk_output_file: Path
        surface_input_file: Path
        surface_template_file: Path

        def __init__(self, info):
            self.base_info = info["base"]
            self.log_info = info["log"]
            self.calc_info = info["calc"]

            self.dimension = info["base"]["dimension"]
            self.root_dir = info["base"]["root_dir"]
            self.output_dir = info["base"]["output_dir"]

            info_s = info["solver"]

            info_param = info_s.get("param", {})
            v = info_param.setdefault("string_list", ["value_01", "value_02"])
            if len(v) != self.dimension:
                raise exception.InputError(
                    f"ERROR: len(string_list) != dimension ({len(v)} != {self.dimension})"
                )
            self.string_list = v

            info_config = info_s.get("config", {})
            self.surface_input_file = Path(info_config.get("surface_input_file", "surf.txt"))

            filename = info_config.get("surface_template_file", "template.txt")
            filename = Path(filename).expanduser().resolve()
            self.surface_template_file = self.root_dir / filename
            if not self.surface_template_file.exists():
                raise exception.InputError(
                    f"ERROR: surface_template_file ({self.surface_template_file}) does not exist"
                )

            filename = info_config.get("bulk_output_file", "bulkP.b")
            filename = Path(filename).expanduser().resolve()
            self.bulk_output_file = self.root_dir / filename
            if not self.bulk_output_file.exists():
                raise exception.InputError(
                    f"ERROR: bulk_output_file ({self.bulk_output_file}) does not exist"
                )

        def update_info(self, update_info=None):
            """
            Update information.

            Parameters
            ----------
            update_info : dict
                Atomic structure.

            """
            if update_info is not None:
                self.log_info["Log_number"] = update_info["log"]["Log_number"]
                self.log_info["ExtraRun"] = update_info["log"].get("ExtraRun", False)
                self.calc_info["x_list"] = update_info["calc"]["x_list"]
                self.base_info["base_dir"] = update_info["base"]["base_dir"]
            # Make fitted x_list and value
            # Move subdir
            fitted_x_list, fitted_value, folder_name = self._prepare(
                self.calc_info["x_list"], self.log_info["ExtraRun"]
            )
            self.calc_info["fitted_x_list"] = fitted_x_list
            self.calc_info["fitted_value"] = fitted_value
            self.base_info["output_dir"] = os.path.join(
                self.base_info["base_dir"], folder_name
            )
            update_info["calc"] = self.calc_info
            update_info["base"] = self.base_info
            update_info["log"] = self.log_info
            return update_info

        def _prepare(self, x_list, extra=False):
            dimension = self.dimension
            string_list = self.string_list
            bulk_output_file = self.bulk_output_file
            solver_input_file = self.surface_input_file
            fitted_x_list = []
            for index in range(dimension):
                fitted_value = " " if x_list[index] >= 0 else ""
                fitted_value += format(x_list[index], ".8f")
                fitted_value = fitted_value[: len(string_list[index])]
                fitted_x_list.append(fitted_value)
            for index in range(dimension):
                print(string_list[index], "=", fitted_x_list[index])
            folder_name = self._pre_bulk(
                self.log_info["Log_number"], bulk_output_file, solver_input_file, extra
            )
            self._replace(fitted_x_list, folder_name)
            return fitted_x_list, fitted_value, folder_name

        def _replace(self, fitted_x_list, folder_name):
            with open(self.surface_template_file, "r") as file_input, open(
                os.path.join(folder_name, self.surface_input_file), "w"
            ) as file_output:
                for line in file_input:
                    for index in range(self.dimension):
                        if line.find(self.string_list[index]) != -1:
                            line = line.replace(
                                self.string_list[index],
                                fitted_x_list[index],
                            )
                    file_output.write(line)

        def _pre_bulk(self, Log_number, bulk_output_file, surface_input_file, extra):
            if extra:
                folder_name = "Extra_Log{:08d}".format(Log_number)
            else:
                folder_name = "Log{:08d}".format(Log_number)
            os.makedirs(folder_name, exist_ok=True)
            shutil.copy(bulk_output_file, os.path.join(folder_name, bulk_output_file.name))
            return folder_name

        def write_input(self, workdir):
            """
            Generate input files of the solver program.

            Parameters
            ----------
            workdir : str
                Path to working directory.
            """
            pass

        def from_directory(self, base_input_dir):
            """
            Set information from files in the base_input_dir

            Parameters
            ----------
            base_input_dir : str
                Path to the directory including base input files.
            """
            # set information of base_input and pos_info from files in base_input_dir
            raise NotImplementedError()

        def cl_args(self, nprocs, nthreads, workdir):
            """
            Generate command line arguments of the solver program.

            Parameters
            ----------
            nprocs : int
                The number of processes.
            nthreads : int
                The number of threads.
            workdir : str
                Path to the working directory.

            Returns
            -------
            args : list[str]
                Arguments of command
            """
            return []

    class Output(object):
        """
        Output manager.
        """

        dimension: int
        string_list: List[str]
        surface_output_file: str
        normalization: str
        Rfactor_type: str
        calculated_first_line: int
        calculated_last_line: int
        row_number: int
        degree_max: float
        degree_list: List[float]

        reference: List[float]
        reference_norm: float
        reference_normalized: List[float]
        degree_list: List[float]

        def __init__(self, info):
            self.dimension = info["base"]["dimension"]
            info_s = info["solver"]

            # maybe redundunt
            self.base_info = info["base"]
            self.calc_info = info["calc"]

            # solver.config
            info_config = info_s.get("config", {})
            self.surface_output_file = info_config.get(
                "surface_output_file", "surf-bulkP.s"
            )

            v = info_config.get("calculated_first_line", 5)
            if not (isinstance(v, int) and v >= 0):
                raise exception.InputError(
                    "ERROR: calculated_first_line should be non-negative integer"
                )
            self.calculated_first_line = v

            v = info_config.get("calculated_last_line", 60)
            if not (isinstance(v, int) and v >= 0):
                raise exception.InputError(
                    "ERROR: calculated_last_line should be non-negative integer"
                )
            self.calculated_last_line = v

            v = info_config.get("row_number", 8)
            if not (isinstance(v, int) and v >= 0):
                raise exception.InputError(
                    "ERROR: row_number should be non-negative integer"
                )
            self.row_number = v

            # solver.post
            info_post = info_s.get("post", {})

            v = info_post.get("normalization", "TOTAL")
            if v not in ["TOTAL", "MAX"]:
                raise exception.InputError("ERROR: normalization must be TOTAL or MAX")
            self.normalization = v

            v = info_post.get("Rfactor_type", "A")
            if v not in ["A", "B"]:
                raise exception.InputError("ERROR: Rfactor_type must be A or B")
            self.Rfactor_type = v

            v = info_post.get("omega", 0.5)
            if v <= 0.0:
                raise exception.InputError("ERROR: omega should be positive")
            self.omega = v

            # solver.param
            info_param = info_s.get("param", {})
            v = info_param.setdefault("string_list", ["value_01", "value_02"])
            if len(v) != self.dimension:
                raise exception.InputError(
                    f"ERROR: len(string_list) != dimension ({len(v)} != {dimension})"
                )
            self.string_list = v

            v = info_s.get("degree_max", 6.0)
            self.degree_max = v

            # solver.reference
            info_ref = info_s.get("reference", {})
            reference_path = info_ref.get("path", "experiment.txt")

            v = info_ref.setdefault("first", 1)
            if not (isinstance(v, int) and v >= 0):
                raise exception.InputError(
                    "ERROR: reference_first_line should be non-negative integer"
                )
            firstline = v

            v = info_ref.setdefault("last", 56)
            if not (isinstance(v, int) and v >= firstline):
                raise exception.InputError(
                    "ERROR: reference_last_line < reference_first_line"
                )
            lastline = v

            # Read experiment-data
            nline = lastline - firstline + 1
            self.degree_list = []
            self.reference = []
            with open(reference_path, "r") as fp:
                for _ in range(firstline - 1):
                    fp.readline()
                for _ in range(nline):
                    line = fp.readline()
                    words = line.split()
                    self.degree_list.append(float(words[0]))
                    self.reference.append(float(words[1]))

            self.reference_norm = 0.0
            if self.normalization == "TOTAL":
                self.reference_norm = sum(self.reference)
            else:  # self.normalization == "MAX":
                self.reference_norm = max(self.reference)

            self.reference_normalized = [
                I_exp / self.reference_norm for I_exp in self.reference
            ]

        def update_info(self, updated_info):
            self.calc_info = updated_info["calc"]
            self.base_info = updated_info["base"]

        def get_results(self) -> float:
            """
            Get Rfactor obtained by the solver program.

            Parameters
            ----------
            output_info : dict

            Returns
            -------
            """

            # Calculate Rfactor and Output numerical results
            os.chdir(self.base_info["output_dir"])
            print(self.calc_info["fitted_x_list"])
            Rfactor = self._post(self.calc_info["fitted_x_list"])
            os.chdir(self.base_info["base_dir"])
            return Rfactor

        def _post(self, fitted_x_list):
            degree_list = self.degree_list
            I_experiment_norm = self.reference_norm
            I_experiment_list = self.reference

            (
                convolution_I_calculated_list_normalized,
                I_calculated_norm,
                I_calculated_list,
                convolution_I_calculated_list,
            ) = self._calc_I_from_file()

            Rfactor = self._calc_Rfactor(convolution_I_calculated_list_normalized)

            print("R-factor =", Rfactor)

            dimension = self.base_info["dimension"]
            string_list = self.string_list

            with open("RockingCurve.txt", "w") as file_RC:
                I_experiment_list_normalized = self.reference_normalized
                # Write headers
                file_RC.write("#")
                for index in range(dimension):
                    file_RC.write(
                        "{} = {} ".format(string_list[index], fitted_x_list[index])
                    )
                file_RC.write("\n")
                file_RC.write("#R-factor = {}\n".format(Rfactor))
                if self.normalization == "TOTAL":
                    file_RC.write("#I_calculated_total={}\n".format(I_calculated_norm))
                    file_RC.write("#I_experiment_total={}\n".format(I_experiment_norm))
                else:  # self.normalization == "MAX"
                    file_RC.write("#I_calculated_max={}\n".format(I_calculated_norm))
                    file_RC.write("#I_experiment_max={}\n".format(I_experiment_norm))
                file_RC.write("#")
                for xname in (
                    "degree",
                    "convolution_I_calculated",
                    "I_experiment",
                    "convolution_I_calculated(normalized)",
                    "I_experiment(normalized)",
                    "I_calculated",
                ):
                    file_RC.write(xname)
                    file_RC.write(" ")
                file_RC.write("\n")

                # Write rocking curve
                for index in range(len(degree_list)):
                    file_RC.write(
                        "{} {} {} {} {} {}\n".format(
                            degree_list[index],
                            convolution_I_calculated_list[index],
                            I_experiment_list[index],
                            convolution_I_calculated_list_normalized[index],
                            I_experiment_list_normalized[index],
                            I_calculated_list[index],
                        )
                    )
            return Rfactor

        def _g(self, x):
            g = (0.939437 / self.omega) * np.exp(
                -2.77259 * (x ** 2.0 / self.omega ** 2.0)
            )
            return g

        def _calc_I_from_file(self):
            surface_output_file = self.surface_output_file
            calculated_first_line = self.calculated_first_line
            calculated_last_line = self.calculated_last_line
            row_number = self.row_number
            degree_max = self.degree_max
            degree_list = self.degree_list

            nlines = calculated_last_line - calculated_first_line + 1
            # TODO: handling error
            assert 0 < nlines

            # TODO: nlines == len(degree_list) ?
            # assert nlines == len(degree_list)

            I_calculated_list = []
            with open(surface_output_file, "r") as file_result:
                for _ in range(calculated_first_line - 1):
                    file_result.readline()
                for _ in range(nlines):
                    line = file_result.readline()
                    words = line.replace(",", "").split()
                    I_calculated_list.append(float(words[row_number - 1]))
                # TODO: degree_calc == degree_exp should be checked for every line?
                degree_last = round(float(words[0]), 1)
                if degree_last == degree_max:
                    print("PASS : degree in lastline = {}".format(degree_last))
                else:
                    print(
                        "WARNING : degree in lastline = {}, but {} expected".format(
                            degree_last, degree_max
                        )
                    )

            ##### convolution #####
            convolution_I_calculated_list = []
            for index in range(len(I_calculated_list)):
                integral = 0.0
                degree_org = degree_list[index]
                for index2 in range(len(I_calculated_list)):
                    integral += (
                        I_calculated_list[index2]
                        * self._g(degree_org - degree_list[index2])
                        * 0.1
                    )
                convolution_I_calculated_list.append(integral)

            # TODO: Is the following statement trivially true?
            if len(I_calculated_list) == len(convolution_I_calculated_list):
                print(
                    "PASS : len(calculated_list) {} == len(convolution_I_calculated_list){}".format(
                        len(I_calculated_list), len(convolution_I_calculated_list)
                    )
                )
            else:
                print(
                    "WARNING : len(calculated_list) {} != len(convolution_I_calculated_list) {}".format(
                        len(I_calculated_list), len(convolution_I_calculated_list)
                    )
                )

            if self.normalization == "TOTAL":
                I_calculated_norm = sum(convolution_I_calculated_list)
            else:  # self.normalization == "MAX"
                I_calculated_norm = max(convolution_I_calculated_list)
            convolution_I_calculated_list_normalized = [
                c / I_calculated_norm for c in convolution_I_calculated_list
            ]
            return (
                convolution_I_calculated_list_normalized,
                I_calculated_norm,
                I_calculated_list,
                convolution_I_calculated_list,
            )

        def _calc_Rfactor(self, calc_result):
            I_experiment_list_normalized = self.reference_normalized
            if self.Rfactor_type == "A":
                R = 0.0
                for I_exp, I_calc in zip(I_experiment_list_normalized, calc_result):
                    R += (I_exp - I_calc) ** 2
                R = np.sqrt(R)
            else:  # self.Rfactor_type == "B"
                y1 = 0.0
                y2 = 0.0
                y3 = 0.0
                for I_exp, I_calc in zip(I_experiment_list_normalized, calc_result):
                    y1 += (I_exp - I_calc) ** 2
                    y2 += I_exp ** 2
                    y3 += I_calc ** 2
                R = y1 / (y2 + y3)
            return R
