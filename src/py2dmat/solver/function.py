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

import numpy as np

import py2dmat

# type hints
from pathlib import Path
from typing import Callable, Optional, Dict


class Solver(py2dmat.solver.SolverBase):
    #-----
    root_dir: Path
    output_dir: Path
    proc_dir: Path
    work_dir: Path
    _name: str
    dimension: int
    timer: Dict[str, Dict]
    #-----
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
        #-----
        #super().__init__(info)
        self.root_dir = info.base["root_dir"]
        self.output_dir = info.base["output_dir"]
        self.proc_dir = self.output_dir / str(py2dmat.mpi.rank())
        self.work_dir = self.proc_dir
        self._name = ""
        self.timer = {"prepare": {}, "run": {}, "post": {}}
        if "dimension" in info.solver:
            self.dimension = info.solver["dimension"]
        else:
            self.dimension = info.base["dimension"]
        #-----
        self._name = "function"
        self._func = None

    @property
    def name(self) -> str:
        return self._name

    def prepare(self, message: py2dmat.Message) -> None:
        self.x = message.x

    def run(self, nprocs: int = 1, nthreads: int = 1) -> None:
        if self._func is None:
            raise RuntimeError(
                "ERROR: function is not set. Make sure that `set_function` is called."
            )
        self.fx = self._func(self.x)

    def get_results(self) -> float:
        return self.fx

    def set_function(self, f: Callable[[np.ndarray], float]) -> None:
        self._func = f
