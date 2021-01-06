from typing import Callable

import numpy as np

from . import solver_base
from ..message import Message
from ..info import Info


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


class Solver(solver_base.SolverBase):
    x: np.ndarray
    fx: float

    def __init__(self, info: Info) -> None:
        """
        Initialize the solver.

        Parameters
        ----------
        info: Info
        """
        self._name = "analytical"
        self.path_to_solver = ""
        if "solver" in info:
            function_name = info["solver"].get("function_name", "quadratics")
        else:
            function_name = "quadratics"

        try:
            self._func = eval(function_name)
        except NameError:
            raise RuntimeError(f"ERROR: Unknown function, {function_name}")

    def default_run_scheme(self) -> str:
        """
        Return
        -------
        str
            run_scheme.
        """
        return "function"

    def function(self) -> Callable[[], None]:
        """ return function to invoke the solver
        """
        return self._run

    def _run(self) -> None:
        self.fx = self._func(self.x)

    def prepare(self, message: Message) -> None:
        self.x = message.x

    def get_results(self) -> float:
        return self.fx
