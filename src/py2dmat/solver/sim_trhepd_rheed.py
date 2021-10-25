from typing import List
import itertools
import os
import os.path
import shutil
import subprocess
from pathlib import Path

import numpy as np

import py2dmat
from py2dmat import exception


class Solver(py2dmat.solver.SolverBase):
    path_to_solver: Path

    def __init__(self, info: py2dmat.Info):
        super().__init__(info)

        self._name = "sim_trhepd_rheed"
        p2solver = info.solver["config"].get("surface_exec_file", "surf.exe")
        if os.path.dirname(p2solver) != "":
            # ignore ENV[PATH]
            self.path_to_solver = self.root_dir / Path(p2solver).expanduser()
        else:
            for P in itertools.chain([self.root_dir], os.environ["PATH"].split(":")):
                self.path_to_solver = Path(P) / p2solver
                if os.access(self.path_to_solver, mode=os.X_OK):
                    break
        if not os.access(self.path_to_solver, mode=os.X_OK):
            raise exception.InputError(f"ERROR: solver ({p2solver}) is not found")
        info_config = info.solver.get("config", {})

        self.input = Solver.Input(info)
        self.output = Solver.Output(info)
        self.result = None

    def prepare(self, message: py2dmat.Message) -> None:
        fitted_x_list, subdir = self.input.prepare(message)
        self.work_dir = self.proc_dir / Path(subdir)
        self.output.prepare(fitted_x_list)
        self.result = None

    def run(self, nprocs: int = 1, nthreads: int = 1) -> None:
        self._run_by_subprocess([str(self.path_to_solver)])

    def get_results(self) -> float:
        if self.result is None:
            self.result = self.output.get_results(self.work_dir)
        return self.result

    class Input(object):
        root_dir: Path
        output_dir: Path
        dimension: int
        string_list: List[str]
        bulk_output_file: Path
        surface_input_file: Path
        surface_template_file: Path

        def __init__(self, info):
            self.root_dir = info.base["root_dir"]
            self.output_dir = info.base["output_dir"]

            if "dimension" in info.solver:
                self.dimension = info.solver["dimension"]
            else:
                self.dimension = info.base["dimension"]

            info_s = info.solver

            info_param = info_s.get("param", {})
            v = info_param.setdefault("string_list", ["value_01", "value_02"])
            if len(v) != self.dimension:
                raise exception.InputError(
                    f"ERROR: len(string_list) != dimension ({len(v)} != {self.dimension})"
                )
            self.string_list = v

            info_config = info_s.get("config", {})
            self.surface_input_file = Path(
                info_config.get("surface_input_file", "surf.txt")
            )

            filename = info_config.get("surface_template_file", "template.txt")
            filename = Path(filename).expanduser().resolve()
            self.surface_template_file = self.root_dir / filename
            if not self.surface_template_file.exists():
                raise exception.InputError(
                    f"ERROR: surface_template_file ({self.surface_template_file}) does not exist"
                )

            self._check_template()

            filename = info_config.get("bulk_output_file", "bulkP.b")
            filename = Path(filename).expanduser().resolve()
            self.bulk_output_file = self.root_dir / filename
            if not self.bulk_output_file.exists():
                raise exception.InputError(
                    f"ERROR: bulk_output_file ({self.bulk_output_file}) does not exist"
                )

        def prepare(self, message: py2dmat.Message):
            x_list = message.x
            step = message.step
            iset = message.set

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
            folder_name = self._pre_bulk(step, bulk_output_file, iset)
            self._replace(fitted_x_list, folder_name)
            return fitted_x_list, folder_name

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

        def _check_template(self) -> None:
            found = [False] * self.dimension
            with open(self.surface_template_file, "r") as file_input:
                for line in file_input:
                    for index, placeholder in enumerate(self.string_list):
                        if line.find(placeholder) != -1:
                            found[index] = True
            if not np.all(found):
                msg = "ERROR: the following labels do not appear in the template file:"
                for label, f in zip(self.string_list, found):
                    if not f:
                        msg += "\n"
                        msg += label
                raise exception.InputError(msg)

        def _pre_bulk(self, Log_number, bulk_output_file, iset):
            folder_name = "Log{:08d}_{:08d}".format(Log_number, iset)
            os.makedirs(folder_name, exist_ok=True)
            shutil.copy(
                bulk_output_file, os.path.join(folder_name, bulk_output_file.name)
            )
            return folder_name

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
            if "dimension" in info.solver:
                self.dimension = info.solver["dimension"]
            else:
                self.dimension = info.base["dimension"]

            info_s = info.solver

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

            self.remove_work_dir = info_post.get("remove_work_dir", False)

            # solver.param
            info_param = info_s.get("param", {})
            v = info_param.setdefault("string_list", ["value_01", "value_02"])
            if len(v) != self.dimension:
                raise exception.InputError(
                    f"ERROR: len(string_list) != dimension ({len(v)} != {self.dimension})"
                )
            self.string_list = v

            v = info_param.get("degree_max", 6.0)
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

        def prepare(self, fitted_x_list):
            self.fitted_x_list = fitted_x_list

        def get_results(self, work_dir) -> float:
            """
            Get Rfactor obtained by the solver program.

            Returns
            -------
            """

            cwd = os.getcwd()
            # Calculate Rfactor and Output numerical results
            os.chdir(work_dir)
            Rfactor = self._post(self.fitted_x_list)
            os.chdir(cwd)
            if self.remove_work_dir:

                def rmtree_error_handler(function, path, excinfo):
                    print(f"WARNING: Failed to remove a working directory, {path}")

                shutil.rmtree(work_dir, onerror=rmtree_error_handler)
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

            dimension = self.dimension
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
                if degree_last != degree_max:
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
