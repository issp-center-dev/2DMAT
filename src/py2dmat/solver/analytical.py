from typing import Callable

import numpy as np

from . import solver_base


def quadratics(xs: np.ndarray) -> float:
    return np.sum(xs * xs)


def ackley(xs: np.ndarray) -> float:
    a = np.mean(xs ** 2)
    a = 20 * np.exp(-0.2 * np.sqrt(a))
    b = np.cos(2.0 * np.pi * xs)
    b = np.exp(0.5 * np.sum(b))
    return 20.0 + np.exp(1.0) - a - b


def rosenbrock(xs: np.ndarray) -> float:
    return np.sum(100.0 * (xs[1:] - xs[:-1] ** 2) ** 2 + (1.0 - xs[:-1]) ** 2)


class analytical(solver_base.Solver_Base):
    def __init__(self, info) -> None:
        """
        Initialize the solver.

        Parameters
        ----------
        solver_name : str
            Solver name.
        """
        info["calc"] = {}
        self.path_to_solver = ""
        self.input = analytical.Input(info)
        self.output = analytical.Output(info)
        self.base_info = info["base"]
        if "solver" in info:
            function_type = info["solver"].get("function_type", "quadratics")
        else:
            function_type = "quadratics"

        try:
            self.func = eval(function_type)
        except NameError:
            raise RuntimeError(f"ERROR: Unknown function, {function_type}")

    def get_run_scheme(self) -> str:
        """
        Return
        -------
        str
            run_scheme.
        """
        return "function"

    def get_path_to_solver(self) -> Callable[[], None]:
        """
        Return
        -------
        """
        return self._run

    def get_name(self) -> str:
        """
        Return
        -------
        """
        return "analytical"

    def _run(self) -> None:
        xs = np.array(self.input.calc_info["x_list"])
        v = self.func(xs)
        self.output.v = v

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
            update_info["calc"] = self.calc_info
            update_info["base"] = self.base_info
            update_info["log"] = self.log_info
            return update_info

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

        v: float = 0.0

        def __init__(self, info):
            pass

        def update_info(self, updated_info):
            pass

        def get_results(self):
            """
            Get energy obtained by the solver program.

            Returns
            -------
            """

            return self.v
