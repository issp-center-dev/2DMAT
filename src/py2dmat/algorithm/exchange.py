from typing import List
from io import open
import copy
import time

import numpy as np

import py2dmat


class Algorithm(py2dmat.algorithm.AlgorithmBase):
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

    def __init__(self, info: py2dmat.Info, runner: py2dmat.Runner = None) -> None:
        super().__init__(info=info, runner=runner)

        if self.mpicomm is None:
            msg = "ERROR: algorithm.exchange requires mpi4py, but mpi4py cannot be imported"
            raise ImportError(msg)

        info_exchange = info.algorithm["exchange"]
        if info_exchange.get("Tlogspace", True):
            self.Ts = np.logspace(
                start=np.log10(info_exchange.get("Tmin", 0.1)),
                stop=np.log10(info_exchange.get("Tmax", 10.0)),
                num=self.mpisize,
            )
        else:
            self.Ts = np.linspace(
                start=info_exchange.get("Tmin", 0.1),
                stop=info_exchange.get("Tmax", 10.0),
                num=self.mpisize,
            )
        self.Tindex = self.mpirank
        self.T2rep = list(range(self.mpisize))
        self.nreplica = self.mpisize

        self.x, self.xmin, self.xmax, self.xunit = self._read_param(info)

        self.numsteps = info_exchange["numsteps"]
        self.numsteps_exchange = info_exchange["numsteps_exchange"]

    def _run(self) -> None:
        rank = self.mpirank

        x_old = np.zeros(self.dimension)
        mbeta = -1.0 / self.Ts[self.Tindex]
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

        self.best_x = copy.copy(self.x)
        self.best_fx = self.fx
        self.best_istep = 0

        while self.istep < self.numsteps:
            # Exchange
            if self.istep % self.numsteps_exchange == 0:
                time_sta = time.perf_counter()
                self._exchange(exchange_direction)
                if self.mpisize > 1:
                    exchange_direction = not exchange_direction
                time_end = time.perf_counter()
                self.timer["run"]["exchange"] += time_end - time_sta
                mbeta = -1.0 / self.Ts[self.Tindex]

            # make candidate
            np.copyto(x_old, self.x)
            self.x += self.rng.normal(size=self.dimension) * self.xunit
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
                if fdiff <= 0.0 or self.rng.random() < np.exp(mbeta * fdiff):
                    pass
                else:
                    np.copyto(self.x, x_old)
                    self.fx = fx_old
            else:
                np.copyto(self.x, x_old)
                self.fx = fx_old

            self._write_result(file_result)
            self.istep += 1

        file_result.close()
        file_trial.close()
        print("complete main process : rank {:08d}/{:08d}".format(rank, self.nreplica))

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

    def _exchange(self, direction: bool) -> None:
        """try to exchange temperatures"""
        self.mpicomm.Barrier()
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
                self.mpicomm.Recv(fbuf, source=other_rank, tag=1)
                other_fx = fbuf[0]
                beta = 1.0 / self.Ts[self.Tindex]
                other_beta = 1.0 / self.Ts[self.Tindex + 1]
                logp = (other_beta - beta) * (other_fx - self.fx)
                if logp >= 0.0 or self.rng.random() < np.exp(logp):
                    ibuf[0] = self.Tindex
                    self.mpicomm.Send(ibuf, dest=other_rank, tag=2)
                    self.Tindex += 1
                else:
                    ibuf[0] = self.Tindex + 1
                    self.mpicomm.Send(ibuf, dest=other_rank, tag=2)
            else:
                fbuf[0] = self.fx
                self.mpicomm.Send(fbuf, dest=other_rank, tag=1)
                self.mpicomm.Recv(ibuf, source=other_rank, tag=2)
                self.Tindex = ibuf[0]

        self.mpicomm.Barrier()
        if self.mpirank == 0:
            self.T2rep[self.Tindex] = self.mpirank
            for other_rank in range(1, self.nreplica):
                self.mpicomm.Recv(ibuf, source=other_rank, tag=0)
                self.T2rep[ibuf[0]] = other_rank
        else:
            ibuf[0] = self.Tindex
            self.mpicomm.Send(ibuf, dest=0, tag=0)
        new_T2rep = np.array(self.T2rep)
        self.mpicomm.Bcast(new_T2rep, root=0)
        self.T2rep[:] = new_T2rep[:]

        self.T = self.Ts[self.Tindex]

    def _prepare(self) -> None:
        self.timer["run"]["submit"] = 0.0
        self.timer["run"]["exchange"] = 0.0

    def _post(self) -> None:
        best_fx = self.mpicomm.gather(self.best_fx, root=0)
        best_x = self.mpicomm.gather(self.best_x, root=0)
        best_istep = self.mpicomm.gather(self.best_istep, root=0)
        if self.mpirank == 0:
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
