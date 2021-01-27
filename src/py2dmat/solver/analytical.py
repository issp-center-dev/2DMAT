import numpy as np

import py2dmat
import py2dmat.solver.function

# type hints


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


class Solver(py2dmat.solver.function.Solver):
    x: np.ndarray
    fx: float

    def __init__(self, info: py2dmat.Info) -> None:
        """
        Initialize the solver.

        Parameters
        ----------
        info: Info
        """
        super().__init__(info)
        self._name = "analytical"
        function_name = info.solver.get("function_name", "quadratics")

        try:
            f = eval(function_name)
            self.set_function(f)
        except NameError:
            raise RuntimeError(f"ERROR: Unknown function, {function_name}")
