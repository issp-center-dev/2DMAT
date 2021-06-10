from typing import TextIO, Union, List
import copy
import time
import pathlib

import numpy as np

import py2dmat
from py2dmat.util.neighborlist import make_neighbor_list, load_neighbor_list
import py2dmat.util.graph


class AlgorithmBase(py2dmat.algorithm.AlgorithmBase):
    """Base of Monte Carlo

    Attributes
    ==========
    nwalkers: int
        the number of walkers (per one process)
    x: np.ndarray
        current configurations
        (NxD array, N is the number of walkers and D is the dimension)
    fx: np.ndarray
        current "Energy"s
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

    nwalkers: int

    iscontinuous: bool

    # continuous problem
    x: np.ndarray
    xmin: np.ndarray
    xmax: np.ndarray
    xunit: np.ndarray

    # discrete problem
    inode: np.ndarray
    nnodes: int
    node_coordinates: np.ndarray
    neighbor_list: List[List[int]]
    ncandidates: np.ndarray  # len(neighbor_list[i])-1

    numsteps: int

    fx: np.ndarray
    istep: int
    best_x: np.ndarray
    best_fx: float
    best_istep: int
    T: float
    Ts: np.ndarray
    Tindex: int

    def __init__(
        self, info: py2dmat.Info, runner: py2dmat.Runner = None, nwalkers: int = 1
    ) -> None:
        time_sta = time.perf_counter()
        super().__init__(info=info, runner=runner)
        self.nwalkers = nwalkers
        info_param = info.algorithm["param"]
        if "mesh_path" in info_param:
            self.iscontinuous = False
            self.node_coordinates = self._meshgrid(info)[0][:, 1:]
            self.nnodes = self.node_coordinates.shape[0]
            self.inode = self.rng.randint(self.nnodes, size=self.nwalkers)
            self.x = self.node_coordinates[self.inode, :]

            if "neighborlist_path" not in info_param:
                msg = "ERROR: Parameter algorithm.param.neighborlist_path does not exist."
                raise RuntimeError(msg)
            nn_path = (
                self.root_dir
                / pathlib.Path(info_param["neighborlist_path"]).expanduser()
            )
            self.neighbor_list = load_neighbor_list(
                nn_path, nnodes=self.nnodes
            )
            if not py2dmat.util.graph.is_connected(self.neighbor_list):
                msg = "ERROR: The transition graph made from neighbor list is not connected."
                msg += "\nHINT: Increase neighborhood radius."
                raise RuntimeError(msg)
            if not py2dmat.util.graph.is_bidirectional(self.neighbor_list):
                msg = "ERROR: The transition graph made from neighbor list is not bidirectional."
                raise RuntimeError(msg)
            self.ncandidates = np.array([ len(ns)-1 for ns in self.neighbor_list ], dtype=np.int64)

        else:
            self.iscontinuous = True
            self.x, self.xmin, self.xmax, self.xunit = self._read_param(
                info, num_walkers=nwalkers
            )
        self.fx = np.zeros(self.nwalkers)
        time_end = time.perf_counter()
        self.timer["init"]["total"] = time_end - time_sta

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

    def _evaluate(self) -> np.ndarray:
        """evaluate current "Energy"s

        ``self.fx`` will be overwritten with the result

        Parameters
        ==========
        run_info: dict
            Parameter set.
            Some parameters will be overwritten.
        """

        for iwalker in range(self.nwalkers):
            message = py2dmat.Message(self.x[iwalker, :], self.istep, iwalker)

            time_sta = time.perf_counter()
            self.fx[iwalker] = self.runner.submit(message)
            time_end = time.perf_counter()
            self.timer["run"]["submit"] += time_end - time_sta
        return self.fx

    def propose(self, current: np.ndarray) -> np.ndarray:
        """propose next candidate

        Parameters
        ==========
        current: np.ndarray
            current position

        Returns
        =======
        proposed: np.ndarray
            proposal
        """
        if self.iscontinuous:
            dx = self.rng.normal(size=(self.nwalkers, self.dimension)) * self.xunit
            proposed = current + dx
        else:
            proposed_list = [self.rng.choice(self.neighbor_list[i]) for i in current]
            proposed = np.array(proposed_list, dtype=np.int64)
        return proposed

    def local_update(
        self, beta: Union[float, np.ndarray], file_trial: TextIO, file_result: TextIO
    ):
        """one step of Monte Carlo

        Parameters
        ==========
        beta: np.ndarray
            inverse temperature for each walker
        file_trial: TextIO
            log file for all trial points
        file_result: TextIO
            log file for all generated samples
        """
        # make candidate
        x_old = copy.copy(self.x)
        if self.iscontinuous:
            self.x = self.propose(x_old)
        else:
            i_old = copy.copy(self.inode)
            self.inode = self.propose(self.inode)
            self.x = self.node_coordinates[self.inode, :]

        # evaluate "Energy"s
        fx_old = copy.copy(self.fx)
        self._evaluate()
        self._write_result(file_trial)

        fdiff = self.fx - fx_old

        # Ignore an overflow warning when evaluating np.exp(x) for x >~ 710.
        old_setting = np.seterr(over="ignore")
        probs = np.exp(-beta * fdiff)
        np.seterr(**old_setting)

        if self.iscontinuous:
            in_range = ((self.xmin <= self.x) & (self.x <= self.xmax)).all(axis=1)
            tocheck = in_range & (probs < 1.0)
        else:
            probs *= self.ncandidates[i_old] / self.ncandidates[self.inode]
            tocheck = probs < 1.0

        num_check = np.count_nonzero(tocheck)

        accepted = np.ones(self.nwalkers, dtype=bool)
        if self.iscontinuous:
            accepted[~in_range] = False
        accepted[tocheck] = self.rng.rand(num_check) < probs[tocheck]

        # revert rejected steps
        rejected = ~accepted
        self.x[rejected, :] = x_old[rejected, :]
        self.fx[rejected] = fx_old[rejected]
        if not self.iscontinuous:
            self.inode[rejected] = i_old[rejected]

        minidx = np.argmin(self.fx)
        if self.fx[minidx] < self.best_fx:
            np.copyto(self.best_x, self.x[minidx, :])
            self.best_fx = self.fx[minidx]
            self.best_istep = self.istep
            self.best_iwalker = minidx
        self._write_result(file_result)

    def _write_result_header(self, fp) -> None:
        fp.write("# step walker T fx")
        for label in self.label_list:
            fp.write(f" {label}")
        fp.write("\n")

    def _write_result(self, fp) -> None:
        for iwalker in range(self.nwalkers):
            fp.write(f"{self.istep} ")
            fp.write(f"{iwalker} ")
            fp.write(f"{self.Ts[self.Tindex]} ")
            fp.write(f"{self.fx[iwalker]} ")
            for x in self.x[iwalker, :]:
                fp.write(f"{x} ")
            fp.write("\n")
        fp.flush()
