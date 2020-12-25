from typing import List

from mpi4py.MPI import Intracomm

from io import open
import copy
import os
import time

import numpy as np
from numpy.random import default_rng

from . import algorithm

from ..info import Info

class Algorithm(algorithm.Algorithm):
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
    fx: float
    T: float
    istep: int
    best_x: np.ndarray
    best_fx: float
    best_istep: int
    comm: Intracomm
    nreplica: int
    rank: int
    Ts: List[float]
    Tindex: int
    T2rep: List[int]
    exchange_direction: bool
    label_list: List[str]

    def __init__(self, info, runner):
        super().__init__(info=info, runner=runner)
        self.prepare_info(info)

    def run(self, run_info: dict):
        original_dir = os.getcwd()
        rank = self.rank
        nreplica = self.nreplica
        os.chdir(str(rank))
        run_info["base"]["base_dir"] = os.getcwd()

        info_alg = run_info["algorithm"]

        dimension = self.dimension
        xmin = np.array(info_alg["param"]["min_list"])
        xmax = np.array(info_alg["param"]["max_list"])
        xunit = np.array(info_alg["param"]["unit_list"])

        self.x = np.array(info_alg["param"]["initial_list"])
        if self.x.size == 0:
            self.x = xmin + (xmax - xmin) * self.rng.random(size=dimension)
        x_old = np.zeros(dimension)

        if info_alg["exchange"]["Tlogspace"]:
            self.Ts = np.logspace(
                start=np.log10(info_alg["exchange"]["Tmin"]),
                stop=np.log10(info_alg["exchange"]["Tmax"]),
                num=nreplica,
            )
        else:
            self.Ts = np.linspace(
                start=info_alg["exchange"]["Tmin"],
                stop=info_alg["exchange"]["Tmax"],
                num=nreplica,
            )
        self.Tindex = rank
        self.T2rep = list(range(nreplica))
        self.T = self.Ts[rank]
        mbeta = -1.0 / self.T
        self.exchange_direction = True

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

        numsteps = info_alg["exchange"]["numsteps"]
        numsteps_exchange = info_alg["exchange"]["numsteps_exchange"]
        while self.istep < numsteps:
            # Exchange
            if self.istep % numsteps_exchange == 0:
                time_sta = time.perf_counter()
                self._exchange()
                time_end = time.perf_counter()
                run_info["log"]["time"]["run"]["exchange"] += time_end - time_sta
                mbeta = -1.0 / self.T

            # make candidate
            np.copyto(x_old, self.x)
            self.x += self.rng.normal(size=dimension) * xunit
            bound = (xmin <= self.x).all() and (self.x <= xmax).all()

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

    def _exchange(self):
        """try to exchange temperatures"""
        self.comm.Barrier()
        if self.exchange_direction:
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
                beta = 1.0 / self.T
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
        if self.nreplica > 2:
            self.exchange_direction = not self.exchange_direction

    def prepare(self, prepare_info):
        import shutil

        self.comm = prepare_info["mpi"]["comm"]
        self.nreplica = prepare_info["mpi"]["size"]
        self.rank = prepare_info["mpi"]["rank"]
        seed = prepare_info["algorithm"]["exchange"]["seed"]
        seed_delta = prepare_info["algorithm"]["exchange"]["seed_delta"]
        if seed is None:
            self.rng = default_rng()
        else:
            self.rng = default_rng(seed + self.rank * seed_delta)

        prepare_info["log"]["time"]["run"]["submit"] = 0.0
        prepare_info["log"]["time"]["run"]["exchange"] = 0.0

    def post(self, post_info):
        best_fx = self.comm.gather(self.best_fx, root=0)
        best_x = self.comm.gather(self.best_x, root=0)
        best_istep = self.comm.gather(self.best_istep, root=0)
        if self.rank == 0:
            best_rank = np.argmin(best_fx)
            with open("best_result.txt", "w") as f:
                f.write("nprocs = {}\n".format(self.nreplica))
                f.write("rank = {}\n".format(best_rank))
                f.write("step = {}\n".format(best_istep[best_rank]))
                f.write("fx = {}\n".format(best_fx[best_rank]))
                for i, x in enumerate(best_x[best_rank]):
                    f.write("x[{}] = {}\n".format(i, x))
            print("Result:")
            print("  rank = {}".format(best_rank))
            print("  step = {}".format(best_istep[best_rank]))
            print("  fx = {}".format(best_fx[best_rank]))
            for i, x in enumerate(best_x[best_rank]):
                print("  x[{}] = {}".format(i, x))

    def write_result_header(self, fp):
        fp.write("# step T fx")
        for label in self.label_list:
            fp.write(f" {label}")
        fp.write("\n")

    def write_result(self, fp):
        fp.write("{} ".format(self.istep))
        fp.write("{} ".format(self.T))
        fp.write("{} ".format(self.fx))
        for x in self.x:
            fp.write("{} ".format(x))
        fp.write("\n")
        fp.flush()

    def prepare_info(self, info: Info) -> None:
        dimension = self.dimension
        info_alg = info["algorithm"]
        info_param = info_alg["param"]
        info_exchange = info_alg["exchange"]

        info_param.setdefault("initial_list", [])
        info_param.setdefault("unit_list", [1.0] * dimension)
        if "label_list" in info_param:
            self.label_list = info_param["label_list"]
        else:
            self.label_list = [f"x{i+1}" for i in range(dimension)]

        # check if defined (FIXME)
        info_param["min_list"]
        info_param["max_list"]
        info_exchange["numsteps"]
        info_exchange["numsteps_exchange"]

        info_exchange.setdefault("Tmin", 0.1)
        info_exchange.setdefault("Tmax", 10.0)
        info_exchange.setdefault("Tlogspace", True)

        info_exchange.setdefault("seed", None)
        info_exchange.setdefault("seed_delta", 314159)


def MPI_Init(info):
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    # Check size ?: size * nprocs_per_solver
    size = comm.Get_size()
    info["mpi"]["comm"] = comm
    info["mpi"]["rank"] = rank
    info["mpi"]["size"] = size
    return info
