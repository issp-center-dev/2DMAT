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

from io import open
import copy
import time
import itertools

import numpy as np

import py2dmat
import py2dmat.algorithm.montecarlo
import py2dmat.util.separateT


class Algorithm(py2dmat.algorithm.montecarlo.AlgorithmBase):
    """Replica Exchange Monte Carlo

    Attributes
    ==========
    x: np.ndarray
        current configuration
    fx: np.ndarray
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
    nreplica: int
        The number of replicas (= the number of procs)
    rank: int
        MPI rank
    T2rep: np.ndarray
        Mapping from temperature index to replica index
    exchange_direction: bool
    """

    x: np.ndarray
    xmin: np.ndarray
    xmax: np.ndarray
    xunit: np.ndarray

    numsteps: int
    numsteps_exchange: int

    fx: np.ndarray
    istep: int
    nreplica: int
    Tindex: np.ndarray
    rep2T: np.ndarray
    T2rep: np.ndarray

    def __init__(self, info: py2dmat.Info, runner: py2dmat.Runner = None) -> None:
        time_sta = time.perf_counter()

        info_exchange = info.algorithm["exchange"]
        nwalkers = info_exchange.get("nreplica_per_proc", 1)

        super().__init__(info=info, runner=runner, nwalkers=nwalkers)

        if self.mpicomm is None:
            msg = "ERROR: algorithm.exchange requires mpi4py, but mpi4py cannot be imported"
            raise ImportError(msg)

        self.nreplica = self.mpisize * self.nwalkers
        self.betas = self.read_Ts(info_exchange, numT=self.nreplica)
        self.Tindex = np.arange(
            self.mpirank * self.nwalkers, (self.mpirank + 1) * self.nwalkers
        )
        self.rep2T = np.arange(self.nreplica)
        self.T2rep = np.arange(self.nreplica)

        self.numsteps = info_exchange["numsteps"]
        self.numsteps_exchange = info_exchange["numsteps_exchange"]
        time_end = time.perf_counter()
        self.timer["init"]["total"] = time_end - time_sta

    def _run(self) -> None:
        rank = self.mpirank

        beta = self.betas[self.Tindex]
        exchange_direction = True

        self.istep = 0

        # first step
        self._evaluate()

        file_trial = open("trial.txt", "w")
        file_result = open("result.txt", "w")
        self._write_result_header(file_result)
        self._write_result(file_result)
        self._write_result_header(file_trial)
        self._write_result(file_trial)
        self.istep += 1

        minidx = np.argmin(self.fx)
        self.best_x = copy.copy(self.x[minidx, :])
        self.best_fx = np.min(self.fx[minidx])
        self.best_istep = 0
        self.best_iwalker = 0

        while self.istep < self.numsteps:
            # Exchange
            if self.istep % self.numsteps_exchange == 0:
                time_sta = time.perf_counter()
                self._exchange(exchange_direction)
                if self.nreplica > 2:
                    exchange_direction = not exchange_direction
                time_end = time.perf_counter()
                self.timer["run"]["exchange"] += time_end - time_sta
                beta = self.betas[self.Tindex]

            self.local_update(beta, file_trial, file_result)
            self.istep += 1

        file_result.close()
        file_trial.close()
        print("complete main process : rank {:08d}/{:08d}".format(rank, self.mpisize))

    def _exchange(self, direction: bool) -> None:
        """try to exchange temperatures"""
        if self.nwalkers == 1:
            self.__exchange_single_walker(direction)
        else:
            self.__exchange_multi_walker(direction)

    def __exchange_single_walker(self, direction: bool) -> None:
        self.mpicomm.Barrier()
        if direction:
            if self.Tindex[0] % 2 == 0:
                other_index = self.Tindex[0] + 1
                is_main = True
            else:
                other_index = self.Tindex[0] - 1
                is_main = False
        else:
            if self.Tindex[0] % 2 == 0:
                other_index = self.Tindex[0] - 1
                is_main = False
            else:
                other_index = self.Tindex[0] + 1
                is_main = True

        ibuf = np.zeros(1, dtype=np.int64)
        fbuf = np.zeros(1, dtype=np.float64)

        if 0 <= other_index < self.nreplica:
            other_rank = self.T2rep[other_index]
            if is_main:
                self.mpicomm.Recv(fbuf, source=other_rank, tag=1)
                other_fx = fbuf[0]
                beta = self.betas[self.Tindex[0]]
                other_beta = self.betas[self.Tindex[0] + 1]
                logp = (other_beta - beta) * (other_fx - self.fx[0])
                if logp >= 0.0 or self.rng.rand() < np.exp(logp):
                    ibuf[0] = self.Tindex
                    self.mpicomm.Send(ibuf, dest=other_rank, tag=2)
                    self.Tindex[0] += 1
                else:
                    ibuf[0] = self.Tindex + 1
                    self.mpicomm.Send(ibuf, dest=other_rank, tag=2)
            else:
                fbuf[0] = self.fx[0]
                self.mpicomm.Send(fbuf, dest=other_rank, tag=1)
                self.mpicomm.Recv(ibuf, source=other_rank, tag=2)
                self.Tindex[0] = ibuf[0]

        self.mpicomm.Barrier()
        if self.mpirank == 0:
            self.T2rep[self.Tindex[0]] = self.mpirank
            for other_rank in range(1, self.nreplica):
                self.mpicomm.Recv(ibuf, source=other_rank, tag=0)
                self.T2rep[ibuf[0]] = other_rank
        else:
            ibuf[0] = self.Tindex
            self.mpicomm.Send(ibuf, dest=0, tag=0)
        self.mpicomm.Bcast(self.T2rep, root=0)

    def __exchange_multi_walker(self, direction: bool) -> None:
        comm = self.mpicomm
        if self.mpisize > 1:
            fx_all = comm.allgather(self.fx)
            fx_all = np.array(fx_all).flatten()
        else:
            fx_all = self.fx

        rep2T_diff = []
        T2rep_diff = []

        for irep in range(
            self.mpirank * self.nwalkers, (self.mpirank + 1) * self.nwalkers
        ):
            iT = self.rep2T[irep]
            if iT % 2 != 0:
                continue
            jT = iT + 1 if direction else iT - 1
            if jT < 0 or jT == self.nreplica:
                continue
            jrep = self.T2rep[jT]
            fdiff = fx_all[jrep] - fx_all[irep]
            bdiff = self.betas[jT] - self.betas[iT]
            logp = fdiff * bdiff
            if logp >= 0.0 or self.rng.rand() < np.exp(logp):
                rep2T_diff.append((irep, jT))  # this means self.rep2T[irep] = jT
                rep2T_diff.append((jrep, iT))
                T2rep_diff.append((iT, jrep))
                T2rep_diff.append((jT, irep))

        if self.mpisize > 1:
            rep2T_diff = comm.allgather(rep2T_diff)
            rep2T_diff = list(itertools.chain.from_iterable(rep2T_diff))  # flatten
            T2rep_diff = comm.allgather(T2rep_diff)
            T2rep_diff = list(itertools.chain.from_iterable(T2rep_diff))  # flatten

        for diff in rep2T_diff:
            self.rep2T[diff[0]] = diff[1]
        for diff in T2rep_diff:
            self.T2rep[diff[0]] = diff[1]
        self.Tindex = self.rep2T[
            self.mpirank * self.nwalkers : (self.mpirank + 1) * self.nwalkers
        ]

    def _prepare(self) -> None:
        self.timer["run"]["submit"] = 0.0
        self.timer["run"]["exchange"] = 0.0

    def _post(self) -> None:
        Ts = self.betas if self.input_as_beta else 1.0/self.betas
        py2dmat.util.separateT.separateT(
            Ts=Ts,
            nwalkers=self.nwalkers,
            output_dir=self.output_dir,
            comm=self.mpicomm,
            use_beta=self.input_as_beta,
            buffer_size=10000,
        )
        if self.mpisize > 1:
            best_fx = self.mpicomm.gather(self.best_fx, root=0)
            best_x = self.mpicomm.gather(self.best_x, root=0)
            best_istep = self.mpicomm.gather(self.best_istep, root=0)
            best_iwalker = self.mpicomm.gather(self.best_iwalker, root=0)
        else:
            best_fx = [self.best_fx]
            best_x = [self.best_x]
            best_istep = [self.best_istep]
            best_iwalker = [self.best_iwalker]
        if self.mpirank == 0:
            best_rank = np.argmin(best_fx)
            with open("best_result.txt", "w") as f:
                f.write(f"nprocs = {self.nreplica}\n")
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
