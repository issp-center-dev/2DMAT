#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import time
from abc import ABCMeta, abstractmethod

import py2dmat

# type hints
from pathlib import Path
from typing import List
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


class Runner(object):
    solver: "py2dmat.solver.SolverBase"
    run: Run
    num_calls: int
    time_previous: float
    log_buffer: List[str]
    proc_dir: Path

    def __init__(self, solver: py2dmat.solver.SolverBase, nprocs: int = 1, nthreads: int = 1):
        """

        Parameters
        ----------
        Solver: py2dmat.solver.SolverBase object
        """
        self.solver = solver
        self.solver_name = solver.name
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
        self.num_calls = 0
        self.time_previous = time.perf_counter()

    def prepare(self, proc_dir: Path):
        self.proc_dir = proc_dir
        self.time_start = time.perf_counter()
        self.time_previous = self.time_start
        self.num_calls = 0
        self.log_buffer = []
        elfile = self.proc_dir / "elapsed_time.dat"
        if elfile.exists():
            elfile.unlink()

    def submit(self, message: py2dmat.Message) -> float:
        t = time.perf_counter()
        self.solver.prepare(message)
        cwd = os.getcwd()
        os.chdir(self.solver.work_dir)
        self.run.submit(self.solver)
        os.chdir(cwd)
        results = self.solver.get_results()

        self.log_buffer.append(f"{self.num_calls} {t - self.time_previous} {t - self.time_start}\n")
        self.time_previous = t

        self.num_calls += 1
        if self.num_calls % 20 == 0:
            with open(self.proc_dir / "elapsed_time.dat", "a") as f:
                for line in self.log_buffer:
                    f.write(line)
            self.log_buffer = []
        return results


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
