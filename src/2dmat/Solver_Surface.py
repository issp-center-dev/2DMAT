import numpy as np
import os
import shutil


class Surface(object):
    def __init__(self, info):
        self.info_file = info["file"]
        self.string_list = info["string_list"]
        self.surface_input_file = info["surface_input_file"]
        self.surface_output_file = info["surface_output_file"]
        self.dimension = info["dimension"]
        self.label_list = info["label_list"]
        self.bulk_output_file = info["bulk_output_file"]
        self.main_dir = info["main_dir"]
        self.omega = info["omega"]
        self.degree_max = info["degree_max"]
        self.degree_list = info["degree_list"]
        self.normalization = info["normalization"]
        self.Rfactor = info["Rfactor"]
        self.info_experiment = info["experiment"]
        self.Log_number = 0

    def f(self, x_list, extra=False):
        # Make fitted x_list and value
        # Move subdir
        fitted_x_list, fitted_value = self._prepare(x_list, extra)
        # Run surf.exe
        print("Perform surface-calculation")
        os.system("%s/surf.exe" % self.main_dir)
        # Calculate Rfactor and Output numerical results
        Rfactor = self._post(fitted_x_list)
        return Rfactor

    def set_log(self, log_number):
        self.Log_number = log_number

    #####[S] Prepare #####
    def _prepare(self, x_list, extra=False):
        dimension = self.dimension
        string_list = self.string_list
        label_list = self.label_list
        bulk_output_file = self.bulk_output_file
        surface_input_file = self.surface_input_file
        fitted_x_list = []
        for index in range(dimension):
            if x_list[index] < 0:
                fitted_value = "%.8f" % (x_list[index])
            else:
                fitted_value = " " + "%.8f" % (x_list[index])
            fitted_value = fitted_value[: len(string_list[index])]
            fitted_x_list.append(fitted_value)
        for index in range(dimension):
            print(label_list[index], "=", fitted_x_list[index])
        self._replace(fitted_x_list)
        self._pre_bulk(self.Log_number, bulk_output_file, surface_input_file, extra)
        return fitted_x_list, fitted_value

    def _pre_bulk(self, Log_number, bulk_output_file, surface_input_file, extra):
        if extra:
            folder_name = "Extra_Log%08d" % Log_number
        else:
            folder_name = "Log%08d" % Log_number
        os.makedirs(folder_name, exist_ok=True)
        shutil.copy("%s" % bulk_output_file, "%s/%s" % (folder_name, bulk_output_file))
        shutil.copy(
            "%s" % surface_input_file, "%s/%s" % (folder_name, surface_input_file)
        )
        os.chdir(folder_name)

    def _replace(self, fitted_x_list):
        print(os.getcwd())
        with open("template.txt", "r") as file_input, open(
            self.surface_input_file, "w"
        ) as file_output:
            for line in file_input:
                for index in range(self.dimension):
                    if line.find(self.string_list[index]) != -1:
                        line = line.replace(
                            self.string_list[index], fitted_x_list[index]
                        )
                file_output.write(line)
        print(os.getcwd())

    #####[E] Prepare #####

    #####[S] Post #####
    def _post(self, fitted_x_list):
        degree_list = self.degree_list
        normalization = self.normalization
        I_experiment_total = self.info_experiment["I_total"]
        I_experiment_list = self.info_experiment["I"]

        (
            convolution_I_calculated_list_normalized,
            I_calculated_total,
            I_calculated_list,
            convolution_I_calculated_list,
        ) = self._calc_I_from_file()
        I_calculated_max = max(convolution_I_calculated_list)

        # Calculate Rfactor
        y = self._calc_Rfactor(convolution_I_calculated_list_normalized)
        print("R-factor =", y)

        dimension = self.dimension
        label_list = self.label_list

        with open("RockingCurve.txt", "w") as file_RC:
            file_RC.write("#")
            for index in range(dimension - 1):
                file_RC.write("%s = %s" % (label_list[index], fitted_x_list[index]))
                file_RC.write(" ")
            file_RC.write(
                "%s = %s\n" % (label_list[dimension - 1], fitted_x_list[dimension - 1])
            )
            file_RC.write("#R-factor = %f\n" % y)
            if normalization == "TOTAL":
                file_RC.write("#I_calculated_total=%f\n" % I_calculated_total)
                file_RC.write("#I_experiment_total=%f\n" % I_experiment_total)
            elif normalization == "MAX":
                file_RC.write("#I_calculated_max=%f\n" % I_calculated_max)
                file_RC.write("#I_experiment_max=%f\n" % I_experiment_max)
            file_RC.write(
                "#degree convolution_I_calculated I_experiment convolution_I_calculated(normalized) I_experiment(normalized) I_calculated\n"
            )
            for index in range(len(degree_list)):
                file_RC.write(
                    "{} {} {} {} {}\n".format(
                        degree_list[index],
                        convolution_I_calculated_list[index],
                        I_experiment_list[index],
                        convolution_I_calculated_list_normalized[index],
                        I_calculated_list[index],
                    )
                )
        return y

    def _g(self, x):
        g = (0.939437 / self.omega) * np.exp(-2.77259 * (x ** 2.0 / self.omega ** 2.0))
        return g

    def _calc_I_from_file(self):
        surface_output_file = self.surface_output_file
        calculated_first_line = self.info_file["calculated_first_line"]
        calculated_last_line = self.info_file["calculated_last_line"]
        row_number = self.info_file["row_number"]
        degree_max = self.degree_max
        degree_list = self.degree_list
        normalization = self.normalization

        I_calculated_list = []
        with open(surface_output_file, "r") as file_result:
            lines = file_result.readlines()
            for line in lines[calculated_first_line - 1 : calculated_last_line]:
                line = line.replace(",", "").split()
                I_calculated_list.append(float(line[row_number - 1]))
            value = float(lines[calculated_last_line - 1].replace(",", "").split()[0])
            if round(value, 1) == degree_max:
                print("PASS : degree_max = %s" % value)
            else:
                print("WARNING : degree_max = %s" % value)

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
        if len(I_calculated_list) == len(convolution_I_calculated_list):
            print(
                "PASS : len(calculated_list)%d = len(convolution_I_calculated_list)%d"
                % (len(I_calculated_list), len(convolution_I_calculated_list))
            )
        else:
            print(
                "WARNING : len(calculated_list)%d != len(convolution_I_calculated_list)%d"
                % (len(I_calculated_list), len(convolution_I_calculated_list))
            )

        convolution_I_calculated_list_normalized = []
        if normalization == "TOTAL":
            I_calculated_total = sum(convolution_I_calculated_list)
            for i in range(len(convolution_I_calculated_list)):
                convolution_I_calculated_list_normalized.append(
                    (convolution_I_calculated_list[i]) / I_calculated_total
                )
        elif normalization == "MAX":
            I_calculated_max = max(convolution_I_calculated_list)
            for i in range(len(convolution_I_calculated_list)):
                convolution_I_calculated_list_normalized.append(
                    convolution_I_calculated_list[i] / I_calculated_max
                )
        return (
            convolution_I_calculated_list_normalized,
            I_calculated_total,
            I_calculated_list,
            convolution_I_calculated_list,
        )

    def _calc_Rfactor(self, calc_reslut):
        Rfactor = self.Rfactor
        degree_list = self.degree_list
        I_experiment_list_normalized = self.info_experiment["I_normalized"]
        if Rfactor == "A":
            y1 = 0.0
            for i in range(len(degree_list)):
                y1 += (I_experiment_list_normalized[i] - calc_reslut[i]) ** 2.0
            y = np.sqrt(y1)
        elif Rfactor == "B":
            y1 = 0.0
            y2 = 0.0
            y3 = 0.0
            for i in range(len(degree_list)):
                y1 += (I_experiment_list_normalized[i] - calc_reslut[i]) ** 2.0
                y2 += I_experiment_list_normalized[i] ** 2.0
                y3 += calc_reslut[i] ** 2.0
            y = y1 / (y2 + y3)
        return y

    #####[E] Post #####
