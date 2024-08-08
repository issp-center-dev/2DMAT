# 2DMAT -- Data-analysis software of quantum beam diffraction experiments for 2D material structure
# Copyright (C) 2020- The University of Tokyo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

import os
import numpy as np
import py2dmat

# type hints
from pathlib import Path
from typing import Callable, Optional, Dict, Tuple


class Solver(py2dmat.solver.SolverBase):
    _func: Optional[Callable[[np.ndarray], float]]

    def __init__(self,
                 info: Optional[py2dmat.Info] = None,
                 fn: Optional[Callable[[np.ndarray], float]] = None) -> None:
        """
        Initialize the solver.

        Parameters
        ----------
        info: Info
        fn: callable object
        """
        self._name = "function"
        self._func = fn

    def evaluate(self, x: np.ndarray, args = (), nprocs: int = 1, nthreads: int = 1) -> float:
        if self._func is None:
            raise RuntimeError("ERROR: function is not set. Make sure that `set_function` is called.")
        return self._func(x)

    def set_function(self, f: Callable[[np.ndarray], float]) -> None:
        self._func = f
