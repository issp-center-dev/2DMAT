#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import time
from abc import ABCMeta, abstractmethod

import py2dmat

# type hints
from pathlib import Path
from typing import List, Union, Optional
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
        fields = [self.num_calls, t-self.time_previous, t-self.time_start]
        if self.to_write_result:
            fields.append(result)
        if self.to_write_x:
            for x in message.x:
                fields.append(x)
        fields.append("\n")
        self.buffer[
            self.buffer_index
        ] = " ".join(map(str, fields))
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
    run: Run
    logger: Logger

    def __init__(
        self,
        solver: py2dmat.solver.SolverBase,
        info: Optional[py2dmat.Info] = None,
        nprocs: int = 1,
        nthreads: int = 1,
    ):
        """

        Parameters
        ----------
        Solver: py2dmat.solver.SolverBase object
        """
        self.solver = solver
        self.solver_name = solver.name
        self.logger = Logger(info)
        run_scheme = solver.default_run_scheme()
        if run_scheme == "mpi_spawn_ready":
            self.run = run_mpispawn_ready(
                nprocs=nprocs,
                nthreads=nthreads,
                comm=mpi.comm(),
            )
        elif run_scheme == "mpi_spawn":
            self.run = run_mpispawn(
                nprocs=nprocs,
                nthreads=nthreads,
                comm=mpi.comm(),
            )
        elif run_scheme == "subprocess":
            self.run = run_subprocess(
                nprocs=nprocs,
                nthreads=nthreads,
                comm=mpi.comm(),
            )
        elif run_scheme == "function":
            self.run = run_function(comm=mpi.comm())
        else:
            msg = f"Unknown scheme: {run_scheme}"
            raise ValueError(msg)

    def prepare(self, proc_dir: Path):
        self.logger.prepare(proc_dir)

    def submit(self, message: py2dmat.Message) -> float:
        self.solver.prepare(message)
        cwd = os.getcwd()
        os.chdir(self.solver.work_dir)
        self.run.submit(self.solver)
        os.chdir(cwd)
        result = self.solver.get_results()
        self.logger.count(message, result)
        return result

    def post(self) -> None:
        self.logger.write()


class run_mpispawn(Run):
    def submit(self, solver: py2dmat.solver.SolverBase):
        raise NotImplementedError()


class run_mpispawn_ready(Run):
    def submit(self, solver: py2dmat.solver.SolverBase):
        raise NotImplementedError()


class run_subprocess(Run):
    """
    Invoker via subprocess

    """

    def submit(self, solver: py2dmat.solver.SolverBase):
        """
        Run solver

        Parameters
        ----------
        solver : py2dmat.solver.SolverBase
            solver

        Returns
        -------
        status : int
            Always returns 0

        Raises
        ------
        subprocess.CalledProcessError
            Raises when solver failed.
        """
        command: List[str] = solver.command()
        with open("stdout", "w") as fi:
            subprocess.run(
                command, stdout=fi, stderr=subprocess.STDOUT, check=True, shell=True
            )
        return 0


class run_function(Run):
    def submit(self, solver):
        solver.function()()
        return 0
