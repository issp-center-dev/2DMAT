import numpy as np

import py2dmat

# type hints
from typing import List, Dict


class Solver(py2dmat.solver.SolverBase):
    x: np.ndarray
    fx: float
    nsites: int
    type: str
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

        self.type = info_solver.get("type", "")
        available_type = ("ising", "potts")
        if self.type not in available_type:
            msg = f'ERROR: Unknown spin type: "{self.type}"\n'
            msg += f"INFO: available types: {available_type}"
            raise py2dmat.exception.InputError(msg)

        self.Js = [{} for _ in range(self.nsites)]
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
                    self.Js[i][j] = J
                    self.Js[j][i] = J

        self.hs = [0.0] * self.nsites
        if "onebody" in info_solver:
            with open(self.root_dir / info_solver["onebody"]) as f:
                for line in f:
                    line = line.split("#")[0].strip()
                    if line == "":
                        continue
                    words = line.split()
                    self.hs[int(words[0])] = float(words[1])

    def run(self, nproc: int = 1, nthreads: int = 1) -> None:
        if self.type == "ising":
            self._run_ising(nproc, nthreads)
        elif self.type == "potts":
            self._run_potts(nproc, nthreads)

    def _run_ising(self, nproc: int = 1, nthreads: int = 1) -> None:
        ene = 0.0
        for isite in range(self.nsites):
            ispin = self.x[isite]
            ene -= ispin * self.hs[isite]
            for jsite, J in self.Js[isite].items():
                jspin = self.x[jsite]
                ene -= 0.5 * J * ispin * jspin
        self.fx = ene

    def _run_potts(self, nproc: int = 1, nthreads: int = 1) -> None:
        ene = 0.0
        for isite in range(self.nsites):
            ispin = self.x[isite]
            if ispin == 0:
                ene -= self.hs[isite]
            for jsite, J in self.Js[isite].items():
                jspin = self.x[jsite]
                if ispin == jspin:
                    ene -= 0.5 * J  # avoid double-counting
        self.fx = ene

    def prepare(self, message: py2dmat.Message) -> None:
        self.x = message.x

    def run_delta(self) -> None:
        if self.type == "ising":
            self._run_ising_delta()
        elif self.type == "potts":
            self._run_potts_delta()

    def _run_ising_delta(self) -> None:
        x = self.x
        ene = 0.0
        for isite, newspin in self.delta.items():
            oldspin = x[isite]
            ene += (oldspin - newspin) * self.hs[isite]
            for jsite, J in self.Js[isite].items():
                jspin = x[jsite]
                ene += J * (oldspin - newspin) * jspin
        self.fx = ene

    def _run_potts_delta(self) -> None:
        ene = 0.0
        for isite, newspin in self.delta.items():
            oldspin = self.x[isite]
            if oldspin == 0:
                ene += self.hs[isite]
            if newspin == 0:
                ene -= self.hs[isite]
            for jsite, J in self.Js[isite].items():
                jspin = self.x[jsite]
                if oldspin == jspin:
                    ene += J
                if newspin == jspin:
                    ene -= J
        self.fx = ene

    def get_results(self) -> float:
        return self.fx
