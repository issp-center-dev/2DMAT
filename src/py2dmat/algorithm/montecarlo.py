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

import typing
from typing import TextIO, Union, List, Tuple
import copy
import time
from pathlib import Path

import numpy as np

import py2dmat
from py2dmat.util.neighborlist import load_neighbor_list
import py2dmat.util.graph
import py2dmat.domain


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
    istep: int
        current step (or, the number of calculated energies)
    best_x: np.ndarray
        best configuration
    best_fx: float
        best "Energy"
    best_istep: int
        index of best configuration (step)
    best_iwalker: int
        index of best configuration (walker)
    comm: MPI.comm
        MPI communicator
    rank: int
        MPI rank
    Ts: np.ndarray
        List of temperatures
    Tindex: np.ndarray
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
    best_iwalker: int
    betas: np.ndarray
    input_as_beta: bool
    Tindex: np.ndarray

    ntrial: int
    naccepted: int

    def __init__(self, info: py2dmat.Info,
                 runner: py2dmat.Runner = None,
                 domain = None,
                 nwalkers: int = 1,
                 run_mode: str = "initial"
    ) -> None:
        time_sta = time.perf_counter()
        super().__init__(info=info, runner=runner, run_mode=run_mode)
        self.nwalkers = nwalkers

        if domain:
            if isinstance(domain, py2dmat.domain.MeshGrid):
                self.iscontinuous = False
            elif isinstance(domain, py2dmat.domain.Region):
                self.iscontinuous = True
            else:
                raise ValueError("ERROR: unsupoorted domain type {}".format(type(domain)))
            self.domain = domain
        else:
            info_param = info.algorithm["param"]
            if "mesh_path" in info_param:
                self.iscontinuous = False
                self.domain = py2dmat.domain.MeshGrid(info)

            else:
                self.iscontinuous = True
                self.domain = py2dmat.domain.Region(info)

        if self.iscontinuous:
            self.xmin = self.domain.min_list
            self.xmax = self.domain.max_list
            self.xunit = self.domain.unit_list

        else:
            self.node_coordinates = np.array(self.domain.grid)[:, 1:]
            self.nnodes = self.node_coordinates.shape[0]
            self._setup_neighbour(info_param)

        time_end = time.perf_counter()
        self.timer["init"]["total"] = time_end - time_sta
        self.Tindex = 0
        self.input_as_beta = False

    def _initialize(self):
        if self.iscontinuous:
            self.domain.initialize(rng=self.rng, limitation=self.runner.limitation, num_walkers=self.nwalkers)
            self.x = self.domain.initial_list
            self.inode = None
        else:
            self.inode = self.rng.randint(self.nnodes, size=self.nwalkers)
            self.x = self.node_coordinates[self.inode, :]

        self.fx = np.zeros(self.nwalkers)
        self.best_fx = 0.0
        self.best_istep = 0
        self.best_iwalker = 0
        self.naccepted = 0
        self.ntrial = 0

    def _setup_neighbour(self, info_param):
        if "neighborlist_path" in info_param:
            nn_path = self.root_dir / Path(info_param["neighborlist_path"]).expanduser()
            self.neighbor_list = load_neighbor_list(nn_path, nnodes=self.nnodes)

            # checks
            if not py2dmat.util.graph.is_connected(self.neighbor_list):
                raise RuntimeError(
                    "ERROR: The transition graph made from neighbor list is not connected."
                    "\nHINT: Increase neighborhood radius."
                )
            if not py2dmat.util.graph.is_bidirectional(self.neighbor_list):
                raise RuntimeError(
                    "ERROR: The transition graph made from neighbor list is not bidirectional."
                )

            self.ncandidates = np.array([len(ns) - 1 for ns in self.neighbor_list], dtype=np.int64)
        else:
            raise ValueError(
                "ERROR: Parameter algorithm.param.neighborlist_path does not exist."
            )
            # otherwise find neighbourlist

    def _evaluate(self, in_range: np.ndarray = None) -> np.ndarray:
        """evaluate current "Energy"s

        ``self.fx`` will be overwritten with the result

        Parameters
        ==========
        run_info: dict
            Parameter set.
            Some parameters will be overwritten.
        """
        # print(">>> _evaluate")
        for iwalker in range(self.nwalkers):
            x = self.x[iwalker, :]
            if in_range is None or in_range[iwalker]:
                args = (self.istep, iwalker)

                time_sta = time.perf_counter()
                self.fx[iwalker] = self.runner.submit(x, args)
                time_end = time.perf_counter()
                self.timer["run"]["submit"] += time_end - time_sta
            else:
                self.fx[iwalker] = np.inf
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
        self,
        beta: Union[float, np.ndarray],
        file_trial: TextIO,
        file_result: TextIO,
        extra_info_to_write: Union[List, Tuple] = None,
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
        extra_info_to_write: List of np.ndarray or tuple of np.ndarray
            extra information to write
        """
        # make candidate
        x_old = copy.copy(self.x)
        if self.iscontinuous:
            self.x = self.propose(x_old)
            #judgement of "in_range"
            in_range_xmin = self.xmin <= self.x
            in_range_xmax = self.x <= self.xmax
            in_range_limitation = np.full(self.nwalkers, False)
            for index_walker in range(self.nwalkers):
                in_range_limitation[index_walker] = self.runner.limitation.judge(
                                                        self.x[index_walker]
                                                            )

            in_range = (in_range_xmin & in_range_xmax).all(axis=1) \
                       &in_range_limitation 
        else:
            i_old = copy.copy(self.inode)
            self.inode = self.propose(self.inode)
            self.x = self.node_coordinates[self.inode, :]
            in_range = np.ones(self.nwalkers, dtype=bool)

        # evaluate "Energy"s
        fx_old = self.fx.copy()
        self._evaluate(in_range)
        self._write_result(file_trial, extra_info_to_write=extra_info_to_write)

        fdiff = self.fx - fx_old

        # Ignore an overflow warning in np.exp(x) for x >~ 710
        # and an invalid operation warning in exp(nan) (nan came from 0 * inf)
        # Note: fdiff (fx) becomes inf when x is out of range
        # old_setting = np.seterr(over="ignore")
        old_setting = np.seterr(all="ignore")
        probs = np.exp(-beta * fdiff)
        #probs[np.isnan(probs)] = 0.0
        np.seterr(**old_setting)

        if not self.iscontinuous:
            probs *= self.ncandidates[i_old] / self.ncandidates[self.inode]
        tocheck = in_range & (probs < 1.0)
        num_check = np.count_nonzero(tocheck)

        accepted = in_range.copy()
        accepted[tocheck] = self.rng.rand(num_check) < probs[tocheck]
        rejected = ~accepted
        self.naccepted += accepted.sum()
        self.ntrial += accepted.size

        # revert rejected steps
        self.x[rejected, :] = x_old[rejected, :]
        self.fx[rejected] = fx_old[rejected]
        if not self.iscontinuous:
            self.inode[rejected] = i_old[rejected]

        minidx = np.argmin(self.fx)
        if self.fx[minidx] < self.best_fx:
            np.copyto(self.best_x, self.x[minidx, :])
            self.best_fx = self.fx[minidx]
            self.best_istep = self.istep
            self.best_iwalker = typing.cast(int, minidx)
        self._write_result(file_result, extra_info_to_write=extra_info_to_write)

    def _write_result_header(self, fp, extra_names=None) -> None:
        if self.input_as_beta:
            fp.write("# step walker beta fx")
        else:
            fp.write("# step walker T fx")
        for label in self.label_list:
            fp.write(f" {label}")
        if extra_names is not None:
            for label in extra_names:
                fp.write(f" {label}")
        fp.write("\n")

    def _write_result(self, fp, extra_info_to_write: Union[List, Tuple] = None) -> None:
        for iwalker in range(self.nwalkers):
            if isinstance(self.Tindex, int):
                beta = self.betas[self.Tindex]
            else:
                beta = self.betas[self.Tindex[iwalker]]
            fp.write(f"{self.istep}")
            fp.write(f" {iwalker}")
            if self.input_as_beta:
                fp.write(f" {beta}")
            else:
                fp.write(f" {1.0/beta}")
            fp.write(f" {self.fx[iwalker]}")
            for x in self.x[iwalker, :]:
                fp.write(f" {x}")
            if extra_info_to_write is not None:
                for ex in extra_info_to_write:
                    fp.write(f" {ex[iwalker]}")
            fp.write("\n")
        fp.flush()

def read_Ts(info: dict, numT: int = None) -> Tuple[bool, np.ndarray]:
    """

    Returns
    -------
    as_beta: bool
        true when using inverse-temperature
    betas: np.ndarray
        sequence of inverse-temperature
    """
    if numT is None:
        raise ValueError("read_Ts: numT is not specified")

    Tmin = info.get("Tmin", None)
    Tmax = info.get("Tmax", None)
    bmin = info.get("bmin", None)
    bmax = info.get("bmax", None)
    logscale = info.get("Tlogspace", True)

    if "Tinvspace" in info:
        raise ValueError("Tinvspace is deprecated. Use bmax/bmin instead.")

    set_b = (bmin is not None or bmax is not None)
    set_T = (Tmin is not None or Tmax is not None)

    if set_b and set_T:
        raise ValueError("both Tmin/Tmax and bmin/bmax are defined")
    if (not set_b) and (not set_T):
        raise ValueError("neither Tmin/Tmax nor bmin/bmax are defined")

    if set_b:
        if bmin is None or bmax is None:
            raise ValueError("bmin and bmax must be set")

        input_as_beta = True
        if not np.isreal(bmin) or bmin < 0.0:
            raise ValueError("bmin must be zero or a positive real number")
        if not np.isreal(bmax) or bmax < 0.0:
            raise ValueError("bmin must be zero or a positive real number")
        if bmin > bmax:
            raise ValueError("bmin must be smaller than or equal to bmax")

        if logscale:
            if bmin == 0.0:
                raise ValueError("bmin must be greater than 0.0 when Tlogspace is True")
            betas = np.logspace(start=np.log10(bmin), stop=np.log10(bmax), num=numT)
        else:
            betas = np.linspace(start=bmin, stop=bmax, num=numT)

    elif set_T:
        if Tmin is None or Tmax is None:
            raise ValueError("Tmin and Tmax must be set")

        input_as_beta = False
        if not np.isreal(Tmin) or Tmin <= 0.0:
            raise ValueError("Tmin must be a positive real number")
        if not np.isreal(Tmax) or Tmax <= 0.0:
            raise ValueError("Tmax must be a positive real number")
        if Tmin > Tmax:
            raise ValueError("Tmin must be smaller than or equal to Tmax")

        if logscale:
            Ts = np.logspace(start=np.log10(Tmin), stop=np.log10(Tmax), num=numT)
        else:
            Ts = np.linspace(start=Tmin, stop=Tmax, num=numT)

        betas = 1.0 / Ts
    else:
        raise RuntimeError("read_Ts: unknown mode: not set_T nor set_b")

    return input_as_beta, betas
