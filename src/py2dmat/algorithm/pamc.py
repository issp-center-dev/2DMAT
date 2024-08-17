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

from typing import List, Dict, Union

from io import open
import copy
import time
import sys

import numpy as np

import py2dmat
import py2dmat.exception
import py2dmat.algorithm.montecarlo
import py2dmat.util.separateT
import py2dmat.util.resampling
from py2dmat.algorithm.montecarlo import read_Ts


class Algorithm(py2dmat.algorithm.montecarlo.AlgorithmBase):
    """Population annealing Monte Carlo

    Attributes
    ==========
    x: np.ndarray
        current configuration
    fx: np.ndarray
        current "Energy"
    logweights: np.ndarray
        current logarithm of weights (Neal-Jarzynski factor)
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
    nreplica: int
        The number of replicas (= the number of procs)
    rank: int
        MPI rank
    betas: list
        List of inverse temperatures
    Tindex: int
        Temperature index
    """

    x: np.ndarray
    xmin: np.ndarray
    xmax: np.ndarray
    xunit: np.ndarray

    numsteps: int
    numsteps_annealing: int

    logweights: np.ndarray
    fx: np.ndarray
    istep: int
    nreplicas: np.ndarray
    betas: np.ndarray
    Tindex: int

    fx_from_reset: np.ndarray

    # 0th column: number of accepted MC trials
    # 1st column: number of total MC trials
    naccepted_from_reset: np.ndarray
    resampling_interval: int

    nset_bootstrap: int

    walker_ancestors: np.ndarray
    populations: np.ndarray
    family_lo: int
    family_hi: int

    Fmeans: np.ndarray
    Ferrs: np.ndarray

    def __init__(self, info: py2dmat.Info, runner: py2dmat.Runner = None) -> None:
        time_sta = time.perf_counter()

        info_pamc = info.algorithm["pamc"]
        nwalkers = info_pamc.get("nreplica_per_proc", 1)

        super().__init__(info=info, runner=runner, nwalkers=nwalkers)

        self.verbose = True and self.mpirank == 0

        numT = self._find_scheduling(info_pamc)

        # super()._initialize()

        #self.betas = self.read_Ts(info_pamc, numT=numT)
        self.input_as_beta, self.betas = read_Ts(info_pamc, numT=numT)
        self.betas.sort()
        # self.Tindex = 0

        # self.logZ = 0.0
        # self.logZs = np.zeros(numT)
        # self.logweights = np.zeros(self.nwalkers)

        # self.Fmeans = np.zeros(numT)
        # self.Ferrs = np.zeros(numT)
        # nreplicas = self.mpisize * self.nwalkers
        # self.nreplicas = np.full(numT, nreplicas)

        # self.populations = np.zeros((numT, self.nwalkers), dtype=int)
        # self.family_lo = self.nwalkers * self.mpirank
        # self.family_hi = self.nwalkers * (self.mpirank + 1)
        # self.walker_ancestors = np.arange(self.family_lo, self.family_hi)
        self.fix_nwalkers = info_pamc.get("fix_num_replicas", True)
        self.resampling_interval = info_pamc.get("resampling_interval", 1)
        if self.resampling_interval < 1:
            self.resampling_interval = numT + 1
        # self.fx_from_reset = np.zeros((self.resampling_interval, self.nwalkers))
        # self.naccepted_from_reset = np.zeros((self.resampling_interval, 2), dtype=int)
        # self.acceptance_ratio = np.zeros(numT)

        #self._initialize()

        time_end = time.perf_counter()
        self.timer["init"]["total"] = time_end - time_sta

    def _initialize(self) -> None:
        super()._initialize()

        # #self.betas = self.read_Ts(info_pamc, numT=numT)
        # self.input_as_beta, self.betas = read_Ts(info_pamc, numT=numT)
        # self.betas.sort()
        # self.Tindex = 0

        numT = len(self.betas)

        self.logZ = 0.0
        self.logZs = np.zeros(numT)
        self.logweights = np.zeros(self.nwalkers)

        self.Fmeans = np.zeros(numT)
        self.Ferrs = np.zeros(numT)
        nreplicas = self.mpisize * self.nwalkers
        self.nreplicas = np.full(numT, nreplicas)

        self.populations = np.zeros((numT, self.nwalkers), dtype=int)
        self.family_lo = self.nwalkers * self.mpirank
        self.family_hi = self.nwalkers * (self.mpirank + 1)
        self.walker_ancestors = np.arange(self.family_lo, self.family_hi)
        # self.fix_nwalkers = info_pamc.get("fix_num_replicas", True)
        # self.resampling_interval = info_pamc.get("resampling_interval", 1)
        # if self.resampling_interval < 1:
        #     self.resampling_interval = numT + 1
        self.fx_from_reset = np.zeros((self.resampling_interval, self.nwalkers))
        self.naccepted_from_reset = np.zeros((self.resampling_interval, 2), dtype=int)
        self.acceptance_ratio = np.zeros(numT)


    def _find_scheduling(self, info_pamc) -> int:
        numsteps = info_pamc.get("numsteps", 0)
        numsteps_annealing = info_pamc.get("numsteps_annealing", 0)
        numT = info_pamc.get("Tnum", 0)

        oks = np.array([numsteps, numsteps_annealing, numT]) > 0
        if np.count_nonzero(oks) != 2:
            msg = "ERROR: Two of 'numsteps', 'numsteps_annealing', "
            msg += "and 'Tnum' should be positive in the input file\n"
            msg += f"  numsteps = {numsteps}\n"
            msg += f"  numsteps_annealing = {numsteps_annealing}\n"
            msg += f"  Tnum = {numT}\n"
            raise py2dmat.exception.InputError(msg)

        if numsteps <= 0:
            self.numsteps_for_T = np.full(numT, numsteps_annealing)
        elif numsteps_annealing <= 0:
            nr = numsteps // numT
            self.numsteps_for_T = np.full(numT, nr)
            rem = numsteps - nr * numT
            if rem > 0:
                self.numsteps_for_T[0 : (rem - 1)] += 1
        else:
            ss: List[int] = []
            while numsteps > 0:
                if numsteps > numsteps_annealing:
                    ss.append(numsteps_annealing)
                    numsteps -= numsteps_annealing
                else:
                    ss.append(numsteps)
                    numsteps = 0
            self.numsteps_for_T = np.array(ss)
            numT = len(ss)

        return numT

    def _run(self) -> None:

        if self.mode is None:
            raise RuntimeError("mode unset")

        restore_rng = not self.mode.endswith("-initrand")
        if self.mode.startswith("init"):
            self._initialize()

            self.Tindex = 0
            self.index_from_reset = 0
            self.istep = 0

            beta = self.betas[self.Tindex]
            self._evaluate()

            file_trial = open("trial_T0.txt", "w")
            self._write_result_header(file_trial, ["weight", "ancestor"])
            self._write_result(file_trial, [np.exp(self.logweights), self.walker_ancestors])
            file_trial.close()

            file_result = open("result_T0.txt", "w")
            self._write_result_header(file_result, ["weight", "ancestor"])
            self._write_result(file_result, [np.exp(self.logweights), self.walker_ancestors])
            file_result.close()

            self.istep += 1

            minidx = np.argmin(self.fx)
            self.best_x = copy.copy(self.x[minidx, :])
            self.best_fx = np.min(self.fx[minidx])
            self.best_istep = 0
            self.best_iwalker = 0

        elif self.mode.startswith("resume"):
            self._load_state(self.checkpoint_file, mode="resume", restore_rng=restore_rng)

        elif self.mode.startswith("continue"):
            self._load_state(self.checkpoint_file, mode="continue", restore_rng=restore_rng)

            self.Tindex = 0
            self.index_from_reset = 0
            self.istep = 0

        else:
            raise RuntimeError("unknown mode {}".format(self.mode))

        next_checkpoint_step = self.istep + self.checkpoint_steps
        next_checkpoint_time = time.time() + self.checkpoint_interval

        if self.verbose:
            print("β mean[f] Err[f] nreplica log(Z/Z0) acceptance_ratio")

        numT = len(self.betas)
        while self.Tindex < numT:
            # print(">>> Tindex = {}".format(self.Tindex))
            Tindex = self.Tindex
            beta = self.betas[self.Tindex]

            if Tindex == 0:
                file_trial = open(f"trial_T{Tindex}.txt", "a")
                file_result = open(f"result_T{Tindex}.txt", "a")
            else:  # Tindex=1,2,...
                file_trial = open(f"trial_T{Tindex}.txt", "w")
                self._write_result_header(file_trial, ["weight", "ancestor"])
                file_result = open(f"result_T{Tindex}.txt", "w")
                self._write_result_header(file_result, ["weight", "ancestor"])

            if self.nwalkers != 0:
                for _ in range(self.numsteps_for_T[Tindex]):
                    self.local_update(
                        beta,
                        file_trial,
                        file_result,
                        extra_info_to_write=[
                            np.exp(self.logweights),
                            self.walker_ancestors,
                        ],
                    )
                    self.istep += 1
            else : #self.nwalkers == 0
                pass

            file_trial.close()
            file_result.close()

            # print(">>> istep={}".format(self.istep))

            self.fx_from_reset[self.index_from_reset, :] = self.fx[:]
            self.naccepted_from_reset[self.index_from_reset, 0] = self.naccepted
            self.naccepted_from_reset[self.index_from_reset, 1] = self.ntrial
            self.naccepted = 0
            self.ntrial = 0
            self.index_from_reset += 1

            if Tindex == numT - 1:
                break

            dbeta = self.betas[Tindex + 1] - self.betas[Tindex]
            self.logweights += -dbeta * self.fx
            if self.index_from_reset == self.resampling_interval:
                time_sta = time.perf_counter()
                self._resample()
                time_end = time.perf_counter()
                self.timer["run"]["resampling"] += time_end - time_sta
                self.index_from_reset = 0

            self.Tindex += 1

            if self.checkpoint:
                time_now = time.time()
                if self.istep >= next_checkpoint_step or time_now >= next_checkpoint_time:
                    # print(">>> checkpoint")
                    self._save_state(self.checkpoint_file)
                    next_checkpoint_step = self.istep + self.checkpoint_steps
                    next_checkpoint_time = time_now + self.checkpoint_interval

        if self.index_from_reset > 0:
            res = self._gather_information(self.index_from_reset)
            self._save_stats(res)
        file_result.close()
        file_trial.close()

        # store final state for continuation
        if self.checkpoint:
            # print(">>> store final state")
            self._save_state(self.checkpoint_file)

        if self.mpisize > 1:
            self.mpicomm.barrier()
        print("complete main process : rank {:08d}/{:08d}".format(self.mpirank, self.mpisize))

    def _gather_information(self, numT: int = None) -> Dict[str, np.ndarray]:
        """
        Arguments
        ---------

        numT: int
            size of dataset

        Returns
        -------
        res: Dict[str, np.ndarray]
            key-value corresponding is the following

            - fxs
                - objective function of each walker over all processes
            - logweights
                - log of weights
            - ns
                - number of walkers in each process
            - ancestors
                - ancestor (origin) of each walker
            - acceptance ratio
                - acceptance_ratio for each temperature
        """

        if numT is None:
            numT = self.resampling_interval
        res = {}
        if self.mpisize > 1:
            fxs_list = self.mpicomm.allgather(self.fx_from_reset[0:numT, :])
            fxs = np.block(fxs_list)
            res["fxs"] = fxs
            ns = np.array([fs.shape[1] for fs in fxs_list], dtype=int)
            res["ns"] = ns
            ancestors_list = self.mpicomm.allgather(self.walker_ancestors)
            res["ancestors"] = np.block(ancestors_list)

            naccepted = self.mpicomm.allreduce(self.naccepted_from_reset[0:numT, :])
            res["acceptance ratio"] = naccepted[:, 0] / naccepted[:, 1]
        else:
            res["fxs"] = self.fx_from_reset[0:numT, :]
            res["ns"] = np.array([self.nwalkers], dtype=int)
            res["ancestors"] = self.walker_ancestors
            res["acceptance ratio"] = (
                self.naccepted_from_reset[:, 0] / self.naccepted_from_reset[:, 1]
            )
        fxs = res["fxs"]
        numT, nreplicas = fxs.shape
        endTindex = self.Tindex + 1
        startTindex = endTindex - numT
        logweights = np.zeros((numT, nreplicas))
        for iT in range(1, numT):
            dbeta = self.betas[startTindex + iT] - self.betas[startTindex + iT - 1]
            logweights[iT, :] = logweights[iT - 1, :] - dbeta * fxs[iT - 1, :]
        res["logweights"] = logweights
        return res

    def _save_stats(self, info: Dict[str, np.ndarray]) -> None:
        fxs = info["fxs"]
        numT, nreplicas = fxs.shape
        endTindex = self.Tindex + 1
        startTindex = endTindex - numT

        logweights = info["logweights"]
        weights = np.exp(
            logweights - logweights.max(axis=1).reshape(-1, 1)
        )  # to avoid overflow

        # bias-corrected jackknife resampling method
        fs = np.zeros((numT, nreplicas))
        fw_sum = (fxs * weights).sum(axis=1)
        w_sum = weights.sum(axis=1)
        for i in range(nreplicas):
            F = fw_sum - fxs[:, i] * weights[:, i]
            W = w_sum - weights[:, i]
            fs[:, i] = F / W
        N = fs.shape[1]
        fm = N * (fw_sum / w_sum) - (N - 1) * fs.mean(axis=1)
        ferr = np.sqrt((N - 1) * fs.var(axis=1))

        self.Fmeans[startTindex:endTindex] = fm
        self.Ferrs[startTindex:endTindex] = ferr
        self.nreplicas[startTindex:endTindex] = nreplicas
        self.acceptance_ratio[startTindex:endTindex] = info["acceptance ratio"][0:numT]

        weights = np.exp(logweights)
        logz = np.log(np.mean(weights, axis=1))
        self.logZs[startTindex:endTindex] = self.logZ + logz
        if endTindex < len(self.betas):
            # calculate the next weight before reset and evalute dF
            bdiff = self.betas[endTindex] - self.betas[endTindex - 1]
            w = np.exp(logweights[-1, :] - bdiff * fxs[-1, :])
            self.logZ = self.logZs[startTindex] + np.log(w.mean())

        if self.verbose:
            for iT in range(startTindex, endTindex):
                print(" ".join(map(str, [
                    self.betas[iT],
                    self.Fmeans[iT],
                    self.Ferrs[iT],
                    self.nreplicas[iT],
                    self.logZs[iT],
                    self.acceptance_ratio[iT],
                ])))

    def _resample(self) -> None:
        res = self._gather_information()
        self._save_stats(res)

        # weights for resampling
        dbeta = self.betas[self.Tindex + 1] - self.betas[self.Tindex]
        logweights = res["logweights"][-1, :] - dbeta * res["fxs"][-1, :]
        weights = np.exp(logweights - logweights.max())  # to avoid overflow
        if self.fix_nwalkers:
            self._resample_fixed(weights)
            self.logweights[:] = 0.0
        else:
            ns = res["ns"]
            offsets = ns.cumsum()
            offset = offsets[self.mpirank - 1] if self.mpirank > 0 else 0
            self._resample_varied(weights, offset)
            self.fx_from_reset = np.zeros((self.resampling_interval, self.nwalkers))
            self.logweights = np.zeros(self.nwalkers)

    def _resample_varied(self, weights: np.ndarray, offset: int) -> None:
        weights_sum = np.sum(weights)
        expected_numbers = (self.nreplicas[0] / weights_sum) * weights[
            offset : offset + self.nwalkers
        ]
        next_numbers = self.rng.poisson(expected_numbers)

        if self.iscontinuous:
            new_x = []
            new_fx = []
            new_ancestors = []
            for iwalker in range(self.nwalkers):
                for _ in range(next_numbers[iwalker]):
                    new_x.append(self.x[iwalker, :])
                    new_fx.append(self.fx[iwalker])
                    new_ancestors.append(self.walker_ancestors[iwalker])
            self.x = np.array(new_x)
            self.fx = np.array(new_fx)
            self.walker_ancestors = np.array(new_ancestors)
        else:
            new_inodes = []
            new_fx = []
            new_ancestors = []
            for iwalker in range(self.nwalkers):
                for _ in range(next_numbers[iwalker]):
                    new_inodes.append(self.inodes[iwalker])
                    new_fx.append(self.fx[iwalker])
                    new_ancestors.append(self.walker_ancestors[iwalker])
            self.inode = np.array(new_inodes)
            self.fx = np.array(new_fx)
            self.walker_ancestors = np.array(new_ancestors)
            self.x = self.node_coordinates[self.inode, :]
        self.nwalkers = np.sum(next_numbers)

    def _resample_fixed(self, weights: np.ndarray) -> None:
        resampler = py2dmat.util.resampling.WalkerTable(weights)
        new_index = resampler.sample(self.rng, self.nwalkers)

        if self.iscontinuous:
            if self.mpisize > 1:
                xs = np.zeros((self.mpisize, self.nwalkers, self.dimension))
                self.mpicomm.Allgather(self.x, xs)
                xs = xs.reshape(self.nreplicas[self.Tindex], self.dimension)
                ancestors = np.array(
                    self.mpicomm.allgather(self.walker_ancestors)
                ).flatten()
            else:
                xs = self.x
                ancestors = self.walker_ancestors
            self.x = xs[new_index, :]
            self.walker_ancestors = ancestors[new_index]
        else:
            if self.mpisize > 1:
                inodes = np.array(self.mpicomm.allgather(self.inode)).flatten()
                ancestors = np.array(
                    self.mpicomm.allgather(self.walker_ancestors)
                ).flatten()
            else:
                inodes = self.inode
                ancestors = self.walker_ancestors
            self.inode = inodes[new_index]
            self.walker_ancestors = ancestors[new_index]
            self.x = self.node_coordinates[self.inode, :]

    def _prepare(self) -> None:
        self.timer["run"]["submit"] = 0.0
        self.timer["run"]["resampling"] = 0.0

    def _post(self) -> None:
        for name in ("result", "trial"):
            with open(self.proc_dir / f"{name}.txt", "w") as fout:
                self._write_result_header(fout, ["weight", "ancestor"])
                for Tindex in range(len(self.betas)):
                    with open(self.proc_dir / f"{name}_T{Tindex}.txt") as fin:
                        for line in fin:
                            if line.startswith("#"):
                                continue
                            fout.write(line)
        if self.mpisize > 1:
            # NOTE:
            # ``gather`` seems not to work with many processes (say, 32) in some MPI implementation.
            # ``Gather`` and ``allgather`` seem to work fine.
            # Since the performance is not so important here, we use ``allgather`` for simplicity.
            best_fx = self.mpicomm.allgather(self.best_fx)
            best_x = self.mpicomm.allgather(self.best_x)
            best_istep = self.mpicomm.allgather(self.best_istep)
            best_iwalker = self.mpicomm.allgather(self.best_iwalker)
        else:
            best_fx = [self.best_fx]
            best_x = [self.best_x]
            best_istep = [self.best_istep]
            best_iwalker = [self.best_iwalker]
        best_rank = np.argmin(best_fx)
        if self.mpirank == 0:
            with open("best_result.txt", "w") as f:
                f.write(f"nprocs = {self.mpisize}\n")
                f.write(f"rank = {best_rank}\n")
                f.write(f"step = {best_istep[best_rank]}\n")
                f.write(f"walker = {best_iwalker[best_rank]}\n")
                f.write(f"fx = {best_fx[best_rank]}\n")
                for label, x in zip(self.label_list, best_x[best_rank]):
                    f.write(f"{label} = {x}\n")
            print("Best Result:")
            print(f"  rank = {best_rank}")
            print(f"  step = {best_istep[best_rank]}")
            print(f"  walker = {best_iwalker[best_rank]}")
            print(f"  fx = {best_fx[best_rank]}")
            for label, x in zip(self.label_list, best_x[best_rank]):
                print(f"  {label} = {x}")

            with open("fx.txt", "w") as f:
                f.write("# $1: 1/T\n")
                f.write("# $2: mean of f(x)\n")
                f.write("# $3: standard error of f(x)\n")
                f.write("# $4: number of replicas\n")
                f.write("# $5: log(Z/Z0)\n")
                f.write("# $6: acceptance ratio\n")
                for i in range(len(self.betas)):
                    f.write(f"{self.betas[i]}")
                    f.write(f" {self.Fmeans[i]} {self.Ferrs[i]}")
                    f.write(f" {self.nreplicas[i]}")
                    f.write(f" {self.logZs[i]}")
                    f.write(f" {self.acceptance_ratio[i]}")
                    f.write("\n")
        return {
            "x": best_x[best_rank],
            "fx": best_fx[best_rank],
            "nprocs": self.mpisize,
            "rank": best_rank,
            "step": best_istep[best_rank],
            "walker": best_iwalker[best_rank],
        }

    def _save_state(self, filename) -> None:
        data = {
            #-- _algorithm
            "mpisize": self.mpisize,
            "mpirank": self.mpirank,
            "rng": self.rng.get_state(),
            "timer": self.timer,
            #-- montecarlo
            "x": self.x,
            "fx": self.fx,
            "inode": self.inode,
            "istep": self.istep,
            "best_x": self.best_x,
            "best_fx": self.best_fx,
            "best_istep": self.best_istep,
            "best_iwalker": self.best_iwalker,
            "naccepted": self.naccepted,
            "ntrial": self.ntrial,
            #-- pamc
            "Tindex": self.Tindex,
            "index_from_reset": self.index_from_reset,
            "logZ": self.logZ,
            "logZs": self.logZs,
            "logweights": self.logweights,
            "Fmeans": self.Fmeans,
            "Ferrs": self.Ferrs,
            "nreplicas": self.nreplicas,
            "populations": self.populations,
            "family_lo": self.family_lo,
            "family_hi": self.family_hi,
            "walker_ancestors": self.walker_ancestors,
            "fx_from_reset": self.fx_from_reset,
            "naccepted_from_reset": self.naccepted_from_reset,
            "acceptance_ratio": self.acceptance_ratio,
        }
        self._save_data(data, filename)

    def _load_state(self, filename, mode="resume", restore_rng=True):
        data = self._load_data(filename)
        if not data:
            print("ERROR: Load status file failed")
            sys.exit(1)

        #-- _algorithm
        assert self.mpisize == data["mpisize"]
        assert self.mpirank == data["mpirank"]

        if restore_rng:
            self.rng = np.random.RandomState()
            self.rng.set_state(data["rng"])
        self.timer = data["timer"]

        #-- montecarlo
        self.x = data["x"]
        self.fx = data["fx"]
        self.inode = data["inode"]

        if mode == "resume":
            self.istep = data["istep"]

        self.best_x = data["best_x"]
        self.best_fx = data["best_fx"]
        self.best_istep = data["best_istep"]
        self.best_iwalker = data["best_iwalker"]

        self.naccepted = data["naccepted"]
        self.ntrial = data["ntrial"]

        #-- pamc
        self.Tindex = data["Tindex"]
        self.index_from_reset = data["index_from_reset"]
        self.logZ = data["logZ"]
        self.logZs = data["logZs"]
        self.logweights = data["logweights"]
        self.Fmeans = data["Fmeans"]
        self.Ferrs = data["Ferrs"]
        self.nreplicas = data["nreplicas"]
        self.populations = data["populations"]

        #assert self.mpirank * self.nwalkers == data["family_lo"]
        #assert (self.mpirank+1) * self.nwalkers == data["family_hi"]
        self.family_lo = data["family_lo"]
        self.family_hi = data["family_hi"]

        self.fx_from_reset = data["fx_from_reset"]
        self.walker_ancestors = data["walker_ancestors"]
        self.naccepted_from_reset = data["naccepted_from_reset"]
        self.acceptance_ratio = data["acceptance_ratio"]


