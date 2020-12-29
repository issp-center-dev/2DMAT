from typing import List, TYPE_CHECKING, Optional

from io import open
import copy
import os
import time

import numpy as np
from numpy.random import default_rng

from . import algorithm

from ..info import Info

if TYPE_CHECKING:
    from mpi4py.MPI import Comm


class Algorithm(algorithm.AlgorithmBase):
    """Replica Exchange Monte Carlo

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
    nreplica: int
        The number of replicas (= the number of procs)
    rank: int
        MPI rank
    Ts: list
        List of temperatures
    Tindex: int
        Temperature index
    T2rep: list
        Mapping from temperature index to replica index
    exchange_direction: bool
    """

    x: np.ndarray
    xmin: np.ndarray
    xmax: np.ndarray
    xunit: np.ndarray

    numsteps: int
    numsteps_exchange: int

    fx: float
    istep: int
    best_x: np.ndarray
    best_fx: float
    best_istep: int
    nreplica: int
    T: float
    Ts: np.ndarray
    Tindex: int
    T2rep: List[int]

    rng: np.random.Generator

    def __init__(self, info):
        super().__init__(info=info)

        if self.comm is None:
            msg = f"ERROR: algorithm.exchange requires mpi4py, but mpi4py cannot be imported"
            raise ImportError(msg)

        info_alg = info["algorithm"]

        info_exchange = info_alg["exchange"]
        if info_exchange.get("Tlogspace", True):
            self.Ts = np.logspace(
                start=np.log10(info_exchange.get("Tmin", 0.1)),
                stop=np.log10(info_exchange.get("Tmax", 10.0)),
                num=self.size,
            )
        else:
            self.Ts = np.linspace(
                start=info_exchange.get("Tmin", 0.1),
                stop=info_exchange.get("Tmax", 10.0),
                num=self.size,
            )
        self.Tindex = self.rank
        self.T2rep = list(range(self.size))
        self.nreplica = self.size

        seed = info_exchange.get("seed", None)
        seed_delta = info_exchange.get("seed_delta", 314159)

        if seed is None:
            self.rng = default_rng()
        else:
            self.rng = default_rng(seed + self.rank * seed_delta)

        info_param = info_alg["param"]
        self.xmin = np.array(info_param["min_list"])
        self.xmax = np.array(info_param["max_list"])
        self.xunit = np.array(info_param.get("unit_list", [1.0] * self.dimension))

        self.x = np.array(info_alg["param"].get("initial_list", []))
        if self.x.size == 0:
            self.x = self.xmin + (self.xmax - self.xmin) * self.rng.random(
                size=self.dimension
            )

        self.numsteps = info_exchange["numsteps"]
        self.numsteps_exchange = info_exchange["numsteps_exchange"]

    def run(self, run_info: dict):
        super().run(run_info)
        original_dir = os.getcwd()
        rank = self.rank
        os.chdir(str(rank))
        run_info["base"]["base_dir"] = os.getcwd()

        x_old = np.zeros(self.dimension)
        mbeta = -1.0 / self.Ts[self.Tindex]
        exchange_direction = True

        self.istep = 0

        # first step
        self._evaluate(run_info)

        file_trial = open("trial.txt", "w")
        file_result = open("result.txt", "w")
        self.write_result_header(file_result)
        self.write_result(file_result)
        self.write_result_header(file_trial)
        self.write_result(file_trial)
        self.istep += 1

        self.best_x = copy.copy(self.x)
        self.best_fx = self.fx
        self.best_istep = 0

        while self.istep < self.numsteps:
            # Exchange
            if self.istep % self.numsteps_exchange == 0:
                time_sta = time.perf_counter()
                self._exchange(exchange_direction)
                if self.size > 1:
                    exchange_direction = not exchange_direction
                time_end = time.perf_counter()
                run_info["log"]["time"]["run"]["exchange"] += time_end - time_sta
                mbeta = -1.0 / self.Ts[self.Tindex]

            # make candidate
            np.copyto(x_old, self.x)
            self.x += self.rng.normal(size=self.dimension) * self.xunit
            bound = (self.xmin <= self.x).all() and (self.x <= self.xmax).all()

            # evaluate "Energy"
            fx_old = self.fx
            self._evaluate(run_info)
            self.write_result(file_trial)

            if bound:
                if self.fx < self.best_fx:
                    np.copyto(self.best_x, self.x)
                    self.best_fx = self.fx
                    self.best_istep = self.istep

                fdiff = self.fx - fx_old
                if fdiff <= 0.0 or self.rng.random() < np.exp(mbeta * fdiff):
                    pass
                else:
                    np.copyto(self.x, x_old)
                    self.fx = fx_old
            else:
                np.copyto(self.x, x_old)
                self.fx = fx_old

            self.write_result(file_result)
            self.istep += 1

        file_result.close()
        file_trial.close()
        os.chdir(original_dir)
        print("complete main process : rank {:08d}/{:08d}".format(rank, self.nreplica))

    def _evaluate(self, run_info: dict) -> float:
        """evaluate current "Energy"

        ``self.fx`` will be overwritten with the result

        Parameters
        ==========
        run_info: dict
            Parameter set.
            Some parameters will be overwritten.
        """

        run_info["log"]["Log_number"] = self.istep
        run_info["calc"]["x_list"] = list(self.x)

        time_sta = time.perf_counter()
        self.fx = self.runner.submit(update_info=run_info)
        time_end = time.perf_counter()
        run_info["log"]["time"]["run"]["submit"] += time_end - time_sta
        return self.fx

    def _exchange(self, direction: bool) -> None:
        """try to exchange temperatures"""
        self.comm.Barrier()
        if direction:
            if self.Tindex % 2 == 0:
                other_index = self.Tindex + 1
                is_main = True
            else:
                other_index = self.Tindex - 1
                is_main = False
        else:
            if self.Tindex % 2 == 0:
                other_index = self.Tindex - 1
                is_main = False
            else:
                other_index = self.Tindex + 1
                is_main = True

        ibuf = np.zeros(1, dtype=np.int)
        fbuf = np.zeros(1, dtype=np.float)

        if 0 <= other_index < self.nreplica:
            other_rank = self.T2rep[other_index]
            if is_main:
                self.comm.Recv(fbuf, source=other_rank, tag=1)
                other_fx = fbuf[0]
                beta = 1.0 / self.Ts[self.Tindex]
                other_beta = 1.0 / self.Ts[self.Tindex + 1]
                logp = (other_beta - beta) * (other_fx - self.fx)
                if logp >= 0.0 or self.rng.random() < np.exp(logp):
                    ibuf[0] = self.Tindex
                    self.comm.Send(ibuf, dest=other_rank, tag=2)
                    self.Tindex += 1
                else:
                    ibuf[0] = self.Tindex + 1
                    self.comm.Send(ibuf, dest=other_rank, tag=2)
            else:
                fbuf[0] = self.fx
                self.comm.Send(fbuf, dest=other_rank, tag=1)
                self.comm.Recv(ibuf, source=other_rank, tag=2)
                self.Tindex = ibuf[0]

        self.comm.Barrier()
        if self.rank == 0:
            self.T2rep[self.Tindex] = self.rank
            for other_rank in range(1, self.nreplica):
                self.comm.Recv(ibuf, source=other_rank, tag=0)
                self.T2rep[ibuf[0]] = other_rank
        else:
            ibuf[0] = self.Tindex
            self.comm.Send(ibuf, dest=0, tag=0)
        new_T2rep = np.array(self.T2rep)
        self.comm.Bcast(new_T2rep, root=0)
        self.T2rep[:] = new_T2rep[:]

        self.T = self.Ts[self.Tindex]

    def prepare(self, prepare_info) -> None:
        super().prepare(prepare_info)
        prepare_info["log"]["time"]["run"]["submit"] = 0.0
        prepare_info["log"]["time"]["run"]["exchange"] = 0.0
        os.makedirs(str(self.rank), exist_ok=True)

    def post(self, post_info) -> None:
        super().post(post_info)
        best_fx = self.comm.gather(self.best_fx, root=0)
        best_x = self.comm.gather(self.best_x, root=0)
        best_istep = self.comm.gather(self.best_istep, root=0)
        if self.rank == 0:
            best_rank = np.argmin(best_fx)
            with open("best_result.txt", "w") as f:
                f.write(f"nprocs = {self.nreplica}\n")
                f.write(f"rank = {best_rank}\n")
                f.write(f"step = {best_istep[best_rank]}\n")
                f.write(f"fx = {best_fx[best_rank]}\n")
                for label, x in zip(self.label_list, best_x[best_rank]):
                    f.write(f"{label} = {x}\n")
            print("Result:")
            print(f"  rank = {best_rank}")
            print(f"  step = {best_istep[best_rank]}")
            print(f"  fx = {best_fx[best_rank]}")
            for label, x in zip(self.label_list, best_x[best_rank]):
                print(f"  {label} = {x}")

    def write_result_header(self, fp) -> None:
        fp.write("# step T fx")
        for label in self.label_list:
            fp.write(f" {label}")
        fp.write("\n")

    def write_result(self, fp) -> None:
        fp.write(f"{self.istep} ")
        fp.write(f"{self.Ts[self.Tindex]} ")
        fp.write(f"{self.fx} ")
        for x in self.x:
            fp.write(f"{x} ")
        fp.write("\n")
        fp.flush()
