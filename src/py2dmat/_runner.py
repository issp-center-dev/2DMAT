# -*- coding: utf-8 -*-
import os
import subprocess
import time
from abc import ABCMeta, abstractmethod

import numpy as np

import py2dmat
import py2dmat.util.read_matrix
import py2dmat.util.mapping

# type hints
from pathlib import Path
from typing import List, Optional
from . import mpi


class Run(metaclass=ABCMeta):
    def __init__(self, nprocs=None, nthreads=None, comm=None):
        """
        Parameters
        ----------
        nprocs : int
            Number of process which one solver uses
        nthreads : int
            Number of threads which one solver process uses
        comm : MPI.Comm
            MPI Communicator
        """
        self.nprocs = nprocs
        self.nthreads = nthreads
        self.comm = comm

    @abstractmethod
    def submit(self, solver: py2dmat.solver.SolverBase):
        pass


class Logger:
    logfile: Path
    buffer_index: int
    buffer_size: int
    buffer: List[str]
    num_calls: int
    time_start: float
    time_previous: float
    to_write_result: bool
    to_write_x: bool

    def __init__(self, info: Optional[py2dmat.Info] = None) -> None:
        if info is None:
            self.buffer_size = 0
            return
        info_log = info.runner.get("log", {})
        self.buffer_size = info_log.get("interval", 0)
        if self.buffer_size <= 0:
            return
        self.filename = info_log.get("filename", "runner.log")
        self.time_start = time.perf_counter()
        self.time_previous = self.time_start
        self.num_calls = 0
        self.buffer_index = 0
        self.buffer = [""] * self.buffer_size
        self.to_write_result = info_log.get("write_result", False)
        self.to_write_x = info_log.get("write_input", False)

    def disabled(self) -> bool:
        return self.buffer_size <= 0

    def prepare(self, proc_dir: Path) -> None:
        if self.disabled():
            return
        self.logfile = proc_dir / self.filename
        if self.logfile.exists():
            self.logfile.unlink()
        with open(self.logfile, "w") as f:
            f.write("# $1: num_calls\n")
            f.write("# $2: elapsed_time_from_last_call\n")
            f.write("# $3: elapsed_time_from_start\n")
            if self.to_write_result:
                f.write("# $4: result\n")
                i = 4
            else:
                i = 5
            if self.to_write_x:
                f.write(f"# ${i}-: input\n")
            f.write("\n")

    def count(self, message: py2dmat.Message, result: float) -> None:
        if self.disabled():
            return
        self.num_calls += 1
        t = time.perf_counter()
        fields = [self.num_calls, t - self.time_previous, t - self.time_start]
        if self.to_write_result:
            fields.append(result)
        if self.to_write_x:
            for x in message.x:
                fields.append(x)
        fields.append("\n")
        self.buffer[self.buffer_index] = " ".join(map(str, fields))
        self.time_previous = t
        self.buffer_index += 1
        if self.buffer_index == self.buffer_size:
            self.write()

    def write(self) -> None:
        if self.disabled():
            return
        with open(self.logfile, "a") as f:
            for i in range(self.buffer_index):
                f.write(self.buffer[i])
        self.buffer_index = 0


class Runner(object):
    solver: "py2dmat.solver.SolverBase"
    logger: Logger

    def __init__(
        self,
        solver: py2dmat.solver.SolverBase,
        info: Optional[py2dmat.Info] = None,
        mapping=None,
    ):
        """

        Parameters
        ----------
        Solver: py2dmat.solver.SolverBase object
        """
        self.solver = solver
        self.solver_name = solver.name
        self.logger = Logger(info)

        if mapping is None:
            info_mapping = info.runner.get("mapping", {})
            A: Optional[np.ndarray] = py2dmat.util.read_matrix.read_matrix(
                info_mapping.get("A", [])
            )
            b: Optional[np.ndarray] = py2dmat.util.read_matrix.read_vector(
                info_mapping.get("b", [])
            )
            if A.size == 0:
                A = None
            if b.size == 0:
                b = None
            self.mapping = py2dmat.util.mapping.Affine(A=A, b=b)
        else:
            self.mapping = mapping

    def prepare(self, proc_dir: Path):
        self.logger.prepare(proc_dir)

    def submit(
        self, message: py2dmat.Message, nprocs: int = 1, nthreads: int = 1
    ) -> float:
        x = self.mapping(message.x)
        message_indeed = py2dmat.Message(x, message.step, message.set)
        self.solver.prepare(message_indeed)
        cwd = os.getcwd()
        os.chdir(self.solver.work_dir)
        self.solver.run(nprocs, nthreads)
        os.chdir(cwd)
        result = self.solver.get_results()
        self.logger.count(message, result)
        return result

    def post(self) -> None:
        self.logger.write()
