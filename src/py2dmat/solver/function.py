from typing import Callable, Optional

import numpy as np

from . import solver_base
from ..message import Message
from ..info import Info


class Solver(solver_base.SolverBase):
    x: np.ndarray
    fx: float
    _func: Optional[Callable[[np.ndarray], float]]

    def __init__(self, info: Info) -> None:
        """
        Initialize the solver.

        Parameters
        ----------
        info: Info
        """
        self._name = "function"
        self.path_to_solver = ""
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

    def prepare(self, message: Message) -> None:
        self.x = message.x

    def get_results(self) -> float:
        return self.fx

    def set_function(self, f: Callable[[np.ndarray], float]) -> None:
        self._func = f
