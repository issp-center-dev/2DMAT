from . import solver_base
import os
import sys
import shutil
import numpy as np


class surface(solver_base.Solver_Base):
    def __init__(self, info, path_to_solver=None):
        """
        Initialize the solver.

        Parameters
        ----------
        solver_name : str
            Solver name.
        path_to_solver : str
            Path to the solver.
        """
        info["calc"] = {}
        self.path_to_solver = os.path.join(info["base"]["main_dir"], self.get_name())
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
        return self.path_to_solver

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

        def __init__(self, info):
            # Set default value
            self.base_info = info["base"]
            self.base_info["extra"] = info["base"].get("extra", False)
            # TODO main_dir is suitable?
            self.base_info["output_dir"] = self.base_info["main_dir"]
            self.log_info = info["log"]
            self.calc_info = info["calc"]

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
                self.calc_info["x_list"] = update_info["calc"]["x_list"]
                self.base_info["base_dir"] = update_info["base"]["base_dir"]
            # Make fitted x_list and value
            # Move subdir
            fitted_x_list, fitted_value, folder_name = self._prepare(
                self.calc_info["x_list"], self.base_info["extra"]
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

            #####[S] Prepare #####

        def _prepare(self, x_list, extra=False):
            dimension = self.base_info["dimension"]
            string_list = self.base_info["string_list"]
            label_list = self.base_info["label_list"]
            bulk_output_file = self.base_info["bulk_output_file"]
            surface_input_file = self.base_info["surface_input_file"]
            fitted_x_list = []
            for index in range(dimension):
                fitted_value = " " if x_list[index] >= 0 else ""
                fitted_value += format(x_list[index], ".8f")
                fitted_value = fitted_value[: len(string_list[index])]
                fitted_x_list.append(fitted_value)
            for index in range(dimension):
                print(label_list[index], "=", fitted_x_list[index])
            self._replace(fitted_x_list)
            folder_name = self._pre_bulk(
                self.log_info["Log_number"], bulk_output_file, surface_input_file, extra
            )
            return fitted_x_list, fitted_value, folder_name

        def _replace(self, fitted_x_list):
            with open("template.txt", "r") as file_input, open(
                self.base_info["surface_input_file"], "w"
            ) as file_output:
                for line in file_input:
                    for index in range(self.base_info["dimension"]):
                        if line.find(self.base_info["string_list"][index]) != -1:
                            line = line.replace(
                                self.base_info["string_list"][index],
                                fitted_x_list[index],
                            )
                    file_output.write(line)

        def _pre_bulk(self, Log_number, bulk_output_file, surface_input_file, extra):
            if extra:
                folder_name = "Extra_Log{:08d}".format(Log_number)
            else:
                folder_name = "Log{:08d}".format(Log_number)
            os.makedirs(folder_name, exist_ok=True)
            shutil.copy(bulk_output_file, os.path.join(folder_name, bulk_output_file))
            shutil.copy(
                surface_input_file, os.path.join(folder_name, surface_input_file)
            )
            return folder_name

        #####[E] Prepare #####

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

        def __init__(self, info):
            self.base_info = info["base"]
            self.experiment_info = info["experiment"]
            self.file_info = info["file"]
            self.calc_info = info["calc"]

        def update_info(self, updated_info):
            self.calc_info = updated_info["calc"]
            self.base_info = updated_info["base"]

        def get_results(self):
            """
            Get energy and structure obtained by the solver program.

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

        #####[S] Post #####
        def _post(self, fitted_x_list):
            degree_list = self.base_info["degree_list"]
            normalization = self.base_info["normalization"]
            I_experiment_norm = self.experiment_info["I_norm"]
            I_experiment_list = self.experiment_info["I"]

            (
                convolution_I_calculated_list_normalized,
                I_calculated_norm,
                I_calculated_list,
                convolution_I_calculated_list,
            ) = self._calc_I_from_file()

            Rfactor = self._calc_Rfactor(convolution_I_calculated_list_normalized)

            print("R-factor =", Rfactor)

            dimension = self.base_info["dimension"]
            label_list = self.base_info["label_list"]

            with open("RockingCurve.txt", "w") as file_RC:
                I_experiment_list_normalized = self.experiment_info["I_normalized"]
                # Write headers
                file_RC.write("#")
                for index in range(dimension):
                    file_RC.write(
                        "{} = {} ".format(label_list[index], fitted_x_list[index])
                    )
                file_RC.write("\n")
                file_RC.write("#R-factor = {}\n".format(Rfactor))
                if normalization == "TOTAL":
                    file_RC.write("#I_calculated_total={}\n".format(I_calculated_norm))
                    file_RC.write("#I_experiment_total={}\n".format(I_experiment_norm))
                elif normalization == "MAX":
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
            g = (0.939437 / self.base_info["omega"]) * np.exp(
                -2.77259 * (x ** 2.0 / self.base_info["omega"] ** 2.0)
            )
            return g

        def _calc_I_from_file(self):
            surface_output_file = self.base_info["surface_output_file"]
            calculated_first_line = self.file_info["calculated_first_line"]
            calculated_last_line = self.file_info["calculated_last_line"]
            row_number = self.file_info["row_number"]
            degree_max = self.base_info["degree_max"]
            degree_list = self.base_info["degree_list"]

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

            if self.base_info["normalization"] == "TOTAL":
                I_calculated_norm = sum(convolution_I_calculated_list)
            elif self.base_info["normalization"] == "MAX":
                I_calculated_norm = max(convolution_I_calculated_list)
            else:
                # TODO: redundant?
                # TODO: error handling
                print("ERROR: unknown normalization", self.normalization)
                sys.exit(1)
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
            I_experiment_list_normalized = self.experiment_info["I_normalized"]
            if self.base_info["Rfactor_type"] == "A":
                R = 0.0
                for I_exp, I_calc in zip(I_experiment_list_normalized, calc_result):
                    R += (I_exp - I_calc) ** 2
                R = np.sqrt(R)
            elif self.base_info["Rfactor_type"] == "B":
                y1 = 0.0
                y2 = 0.0
                y3 = 0.0
                for I_exp, I_calc in zip(I_experiment_list_normalized, calc_result):
                    y1 += (I_exp - I_calc) ** 2
                    y2 += I_exp ** 2
                    y3 += I_calc ** 2
                R = y1 / (y2 + y3)
            else:
                # TODO: redundant?
                # TODO: error handling
                print("ERROR: unknown Rfactor type", self.base_info["Rfactor_type"])
                sys.exit(1)
            return R

        #####[E] Post #####
