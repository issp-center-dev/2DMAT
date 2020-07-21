import solver_base

class sol_surface(solver_base.Solver_Base):
    def __init__(self, path_to_solver, info):
        """
        Initialize the solver.

        Parameters
        ----------
        solver_name : str
            Solver name.
        path_to_solver : str
            Path to the solver.
        """
        info["experiment"] = {}
        degree_list, I_experiment_list, I_experiment_list_normalized = self._read_experimentself(info["main_dir"])
        info["experiment"]["degree_list"] = degree_list
        info["experiment"]["I_experiment_list"] = I_experiment_list
        info["experiment"]["I_experiment_list_normalized"] = I_experiment_list_normalized
        self.path_to_solver = path_to_solver
        self.input = sol_surface.Input(info)
        self.output = sol_surface.Output(info)
        self.base_info = info
        self.pre_procedure(info["x_list"], info["dimension"], info["bulk_output_file"], info["surface_input_file"])

    def _read_experiment(self, main_dir):
        degree_list = []
        I_experiment_list = []
        with open(os.path.join(main_dir, "experiment.txt"), "r") as fp:
            lines = fp.readlines()
            for line in lines[experiment_first_line - 1:experiment_last_line]:
                line = line.split()
                degree_list.append(float(line[0]))
                I_experiment_list.append(float(line[1]))
        I_experiment_list_normalized = []
        if normalization == "TOTAL":
            I_experiment_total = sum(I_experiment_list)
            for i in range(len(I_experiment_list)):
                I_experiment_list_normalized.append(
                    (I_experiment_list[i]) / I_experiment_total
                )
        elif normalization == "MAX":
            I_experiment_max = max(I_experiment_list)
            for i in range(len(I_experiment_list)):
                I_experiment_list_normalized.append(I_experiment_list[i] / I_experiment_max)
        return degree_list, I_experiment_list, I_experiment_list_normalized


    def get_run_scheme(self):
        """
        Return
        -------
        str
            run_scheme.
        """
        return "subprocess_from_python"

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

    def pre_procedure(self):
        x_list = self.base_info["x_list"]
        dimension = self.base_info["dimension"]
        bulk_output_file = self.base_info["bulk_output_file"]
        surface_input_file = self.base_info["surface_input_file"]

        # Perform bulk-calculation
        print("Perform bulk-calculation")
        os.system("%s/bulk.exe" % self.base_info["main_dir"])
        # Make ColorMap
        print("Read MeshData.txt")
        mesh_list = []
        with open(("MeshData.txt", "r")) as file_MD:
            for line in file_MD:
                if line[0] == "#":
                    continue
                line = line.split()
                mesh = []
                for value in line:
                    mesh.append(float(value))
                mesh_list.append(mesh)

        print("Make ColorMap")
        file_CM = open("ColorMap.txt", "w")
        file_CM.write("#")
        for label in label_list:
            file_CM.write("%s " % label)
        file_CM.write("R-factor\n")
        self.iterations = len(mesh_list)

    def run(self):
        fx_list = []
        def replace(fitted_x_list):
            with open("template.txt", "r") as file_input, open(surface_input_file, "w") as file_output:
                for line in file_input:
                    for index in range(dimension):
                        if line.find(string_list[index]) != -1:
                            line = line.replace(string_list[index], fitted_x_list[index])
                    file_output.write(line)

        Log_number = round(x_list[0])
        x_list = x_list[1:]
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
        replace(fitted_x_list)
        folder_name = "Log%08d" % Log_number
        os.makedirs(folder_name, exist_ok=True)
        shutil.copy("%s" % bulk_output_file, "%s/%s" % (folder_name, bulk_output_file))
        shutil.copy(
            "%s" % surface_input_file, "%s/%s" % (folder_name, surface_input_file)
        )
        os.chdir(folder_name)

    class Input(object):
        """
        Input manager.

        Attributes
        ----------
        base_info : Any
            Common parameter.
        """

        def __init__(self, info):
            self.base_info = info

        def update_info(self, update_info):
            """
            Update information.

            Parameters
            ----------
            update_info : dict
                Atomic structure.

            """
            raise NotImplementedError()

        def write_input(self, workdir):
            """
            Generate input files of the solver program.

            Parameters
            ----------
            workdir : str
                Path to working directory.
            """
            raise NotImplementedError()

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
            self.base_info = info

        def get_results(self):
            """
            Get energy and structure obtained by the solver program.

            Parameters
            ----------
            output_info : dict

            Returns
            -------
            """
            info = self.base_info
            y = self.post_procedure()
            #Check does it really need ?
            os.chdir(info["main_dir"])
            return y


        def check_results(self):
            """
            Check calculation status
            surface_output_file:
            workdir:

            Returns
            -------
            True: Calculation is normally finished.
            False: Calculation is not normally finished.
            """
            surface_output_file = self.base_info["surface_output_file"]
            NaN_exist = False
            with open(surface_output_file, "r") as file_check:
                lines = file_check.readlines()
                for line in lines[calculated_first_line-1:calculated_last_line]:
                        if line.find("NaN") != -1:
                            NaN_exist = True
            if not NaN_exist:
                print("RASS : %s does not have NaN." % surface_output_file)
                return True
            else:
                print(
                    "WARNING : %s has NaN. Perform surface-calculation one more time."
                    % surface_output_file
                )
                return False

        def post_procedure(self):
            surface_output_file = self.base_info["surface_output_file"]
            omega = self.base_info["omega"]
            I_experiment_list = self.base_info["experiment"]["I_experiment_list"]
            I_experiment_list_normalized = self.base_info["experiment"]["I_experiment_list_normalized"]
            degree_list = self.base_info["experiment"]["degree_list"]
            normalization = self.base_info["normalization"]
            Rfactor = self.base_info["Rfactor"]

            I_calculated_list = []
            with open(surface_output_file, "r") as file_result:
                lines = file_result.readlines()
                for line in lines[calculated_first_line - 1:calculated_last_line]:
                    line = line.replace(",", "").split()
                    I_calculated_list.append(float(line[row_number - 1]))
                value = float(lines[calculated_last_line - 1].replace(",", "").split()[0])
                if round(value, 1) == degree_max:
                    print("PASS : degree_max = %s" % value)
                else:
                    print("WARNING : degree_max = %s" % value)

            def g(x, omega):
                g = (0.939437 / omega) * np.exp(-2.77259 * (x ** 2.0 / omega ** 2.0))
                return g

            ##### convolution #####
            convolution_I_calculated_list = []
            for index in range(len(I_calculated_list)):
                integral = 0.0
                for index2 in range(len(I_calculated_list)):
                    integral += (
                            I_calculated_list[index2]
                            * g(degree_list[index] - degree_list[index2], omega)
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
            #####################

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

            if Rfactor == "A":
                y1 = 0.0
                for i in range(len(degree_list)):
                    y1 +=  (I_experiment_list_normalized[i]- convolution_I_calculated_list_normalized[i])**2.0
                y = np.sqrt(y1)
            elif Rfactor == "B":
                y1 = 0.0
                y2 = 0.0
                y3 = 0.0
                for i in range(len(degree_list)):
                    y1 +=  (I_experiment_list_normalized[i]- convolution_I_calculated_list_normalized[i])**2.0
                    y2 += I_experiment_list_normalized[i] ** 2.0
                    y3 += convolution_I_calculated_list_normalized[i] ** 2.0
                y = y1 / (y2 + y3)
            print("R-factor =", y)
            for index in range(len(degree_list)):
                file_RC.write("{} {} {} {} {}\n".format(
                    degree_list[index],
                    convolution_I_calculated_list[index],
                    I_experiment_list[index],
                    convolution_I_calculated_list_normalized[index],
                    I_calculated_list[index]
                ))
            return y


if __name__ == "__main__":


    import subprocess
    surf = sol_surface("./surf.exe")
    print(surf.get_name())
    #args = input_info.cl_args(self.nprocs, self.nthreads, output_dir)
    path_to_solver = surf.get_path_to_solver()
    command = [path_to_solver]
    #command.extend(args)
    for time in range(100):
        subprocess.run(command, check=True)

    sol_surface.Output.post_procedure()