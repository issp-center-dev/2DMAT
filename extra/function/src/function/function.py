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
from typing import Callable, Optional, Dict


class Solver:
    root_dir: Path
    output_dir: Path
    proc_dir: Path
    work_dir: Path
    _name: str
    dimension: int
    timer: Dict[str, Dict]
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
        self.root_dir = info.base["root_dir"]
        self.output_dir = info.base["output_dir"]
        self.proc_dir = self.output_dir / str(py2dmat.mpi.rank())
        self.work_dir = self.proc_dir

        self.dimension = info.solver.get("dimension") or info.base.get("dimension")

        self._name = "function"
        self._func = fn

        self.timer = {"prepare": {}, "run": {}, "post": {}}

    @property
    def name(self) -> str:
        return self._name

    def evaluate(self, x: np.ndarray, args = (), nprocs: int = 1, nthreads: int = 1) -> float:
        if self._func is None:
            raise RuntimeError("ERROR: function is not set. Make sure that `set_function` is called.")
        return self._func(x)

    def set_function(self, f: Callable[[np.ndarray], float]) -> None:
        self._func = f
