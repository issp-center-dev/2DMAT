import numpy as np

import py2dmat

# type hints
import typing
from typing import List, Dict


class Solver(py2dmat.solver.SolverBase):
    x: np.ndarray
    fx: float
    nsites: int
    Q: int
    Js: List[Dict[int, float]]
    hs: List[float]

    def __init__(self, info: py2dmat.Info) -> None:
        """
        Initialize the solver.

        Parameters
        ----------
        info: Info
        """
        super().__init__(info)
        self._name = "potts"
        self.nsites = self.dimension
        info_solver = info.solver

        self.Js = [{} for _ in range(self.nsites)]
        Js: List[Dict[int, List[float]]] = [{} for _ in range(self.nsites)]
        if "twobody" in info_solver:
            with open(self.root_dir / info_solver["twobody"]) as f:
                for line in f:
                    line = line.split("#")[0].strip()
                    if line == "":
                        continue
                    words = line.split()
                    i = int(words[0])
                    j = int(words[1])
                    J = float(words[2])
                    if j not in Js[i]:
                        Js[i][j] = [J]
                        Js[j][i] = [J]
                    else:
                        Js[i][j].append(J)
                        Js[j][i].append(J)
            for i in range(self.nsites):
                for j in Js[i].keys():
                    self.Js[i][j] = typing.cast(float, np.mean(Js[i][j])) 

        self.hs = [0.0] * self.nsites
        if "onebody" in info_solver:
            with open(self.root_dir / info_solver["onebody"]) as f:
                for line in f:
                    line = line.split("#")[0].strip()
                    if line == "":
                        continue
                    words = line.split()
                    self.hs[int(words[0])] = float(words[1])

    def run(self, nproc: int=1, nthreads: int=1) -> None:
        ene = 0.0
        for isite in range(self.nsites):
            ispin = self.x[isite]
            ene -= ispin * self.hs[isite]
            for jsite, J in self.Js[isite].items():
                jspin = self.x[jsite]
                ene -= 0.5 * J * ispin * jspin
        self.fx = ene

    def prepare(self, message: py2dmat.Message) -> None:
        self.x = message.x

    def run_delta(self) -> None:
        x = self.x
        ene = 0.0
        for isite, newspin in self.delta.items():
            oldspin = x[isite]
            ene += (oldspin - newspin) * self.hs[isite]
            for jsite, J in self.Js[isite].items():
                jspin = x[jsite]
                ene += J * (oldspin - newspin) * jspin
        self.fx = ene

    def get_results(self) -> float:
        return self.fx
