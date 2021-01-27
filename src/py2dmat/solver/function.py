import numpy as np

import py2dmat

# type hints
from typing import Callable, Optional


class Solver(py2dmat.solver.SolverBase):
    x: np.ndarray
    fx: float
    _func: Optional[Callable[[np.ndarray], float]]

    def __init__(self, info: py2dmat.Info) -> None:
        """
        Initialize the solver.

        Parameters
        ----------
        info: Info
        """
        super().__init__(info)
        self._name = "function"
        self._func = None

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
        if self._func is None:
            raise RuntimeError("ERROR: function is not set. Make sure that `set_function` is called.")
        self.fx = self._func(self.x)

    def prepare(self, message: py2dmat.Message) -> None:
        self.x = message.x

    def get_results(self) -> float:
        return self.fx

    def set_function(self, f: Callable[[np.ndarray], float]) -> None:
        self._func = f
