from typing import List, TextIO
from io import open
import copy
import time

import numpy as np

import py2dmat


class AlgorithmBase(py2dmat.algorithm.AlgorithmBase):
    """Base of Monte Carlo

    Attributes
    ==========
    x: np.ndarray
        current configuration
    fx: float
        current "Energy"
    T: float
        current "Temperature"
    istep: int
        current step (or, the number of calculated energies)
    best_x: np.ndarray
        best configuration
    best_fx: float
        best "Energy"
    best_istep: int
        index of best configuration
    comm: MPI.comm
        MPI communicator
    rank: int
        MPI rank
    Ts: list
        List of temperatures
    Tindex: int
        Temperature index
    """

    x: np.ndarray
    xmin: np.ndarray
    xmax: np.ndarray
    xunit: np.ndarray

    numsteps: int

    fx: float
    istep: int
    best_x: np.ndarray
    best_fx: float
    best_istep: int
    T: float
    Ts: np.ndarray
    Tindex: int

    def __init__(self, info: py2dmat.Info, runner: py2dmat.Runner = None) -> None:
        super().__init__(info=info, runner=runner)

        self.x, self.xmin, self.xmax, self.xunit = self._read_param(info)

    def read_Ts(self, info: dict) -> np.ndarray:
        bTinv = info.get("Tinvspace", False)
        bTlog = info.get("Tlogspace", True)
        bTlogdefined = "Tlogspace" in info

        if bTinv and bTlog:
            msg = "ERROR: Both Tinvspace and Tlogspace are enabled."
            if not bTlogdefined:
                msg += "\nNote: The default value of Tlogspace is true."
            raise RuntimeError(msg)

        if bTinv:
            T_inverse = np.linspace(
                start=(1.0 / info.get("Tmin", 0.1)),
                stop=(1.0 / info.get("Tmax", 10)),
                num=self.mpisize,
            )
            Ts = 1.0 / T_inverse
        elif bTlog:
            Ts = np.logspace(
                start=np.log10(info.get("Tmin", 0.1)),
                stop=np.log10(info.get("Tmax", 10.0)),
                num=self.mpisize,
            )
        else:
            Ts = np.linspace(
                start=info.get("Tmin", 0.1),
                stop=info.get("Tmax", 10.0),
                num=self.mpisize,
            )
        return Ts

    def _evaluate(self) -> float:
        """evaluate current "Energy"

        ``self.fx`` will be overwritten with the result

        Parameters
        ==========
        run_info: dict
            Parameter set.
            Some parameters will be overwritten.
        """

        message = py2dmat.Message(self.x, self.istep, 0)

        time_sta = time.perf_counter()
        self.fx = self.runner.submit(message)
        time_end = time.perf_counter()
        self.timer["run"]["submit"] += time_end - time_sta
        return self.fx

    def propose(self, current_x) -> np.ndarray:
        """propose next candidate

        Parameters
        ==========
        current_x: np.ndarray
            current position

        Returns
        =======
        next_x: np.ndarray
            proposal
        """
        dx = self.rng.normal(size=self.dimension) * self.xunit
        next_x = current_x + dx
        return next_x

    def local_update(self, beta: float, file_trial: TextIO, file_result: TextIO):
        """one step of Monte Carlo

        Parameters
        ==========
        beta: float
            inverse temperature
        file_trial: TextIO
            log file for all trial points
        file_result: TextIO
            log file for all generated samples
        """
        # make candidate
        x_old = copy.copy(self.x)
        self.x = self.propose(x_old)
        bound = (self.xmin <= self.x).all() and (self.x <= self.xmax).all()

        # evaluate "Energy"
        fx_old = self.fx
        self._evaluate()
        self._write_result(file_trial)

        if bound:
            if self.fx < self.best_fx:
                np.copyto(self.best_x, self.x)
                self.best_fx = self.fx
                self.best_istep = self.istep

            fdiff = self.fx - fx_old
            if fdiff <= 0.0 or self.rng.random() < np.exp(-beta * fdiff):
                pass
            else:
                np.copyto(self.x, x_old)
                self.fx = fx_old
        else:
            np.copyto(self.x, x_old)
            self.fx = fx_old
        self._write_result(file_result)

    def _write_result_header(self, fp) -> None:
        fp.write("# step T fx")
        for label in self.label_list:
            fp.write(f" {label}")
        fp.write("\n")

    def _write_result(self, fp) -> None:
        fp.write(f"{self.istep} ")
        fp.write(f"{self.Ts[self.Tindex]} ")
        fp.write(f"{self.fx} ")
        for x in self.x:
            fp.write(f"{x} ")
        fp.write("\n")
        fp.flush()
