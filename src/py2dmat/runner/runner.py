#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import subprocess
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import List

import numpy as np

from .. import mpi
from ..message import Message
from ..solver.solver_base import SolverBase


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
    def submit(self, solver: SolverBase):
        pass


class Runner(object):
    solver: SolverBase
    run: Run

    def __init__(self, solver: SolverBase, nprocs: int = 1, nthreads: int = 1):
        """

        Parameters
        ----------
        Solver: py2dmat.solver.solver_base object
        mpi_info:
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

    def submit(self, message: Message) -> float:
        self.solver.prepare(message)
        cwd = os.getcwd()
        os.chdir(self.solver.get_working_directory())
        self.run.submit(self.solver)
        os.chdir(cwd)
        results = self.solver.get_results()
        return results

    def set_solver_dir(self, proc_dir: Path) -> None:
        self.solver.proc_dir = proc_dir
        self.solver.work_dir = proc_dir


class run_mpispawn(Run):
    def submit(self, solver: SolverBase):
        raise NotImplementedError()


class run_mpispawn_ready(Run):
    def submit(self, solver: SolverBase):
        raise NotImplementedError()


class run_subprocess(Run):
    """
    Invoker via subprocess

    """

    def submit(self, solver: SolverBase):
        """
        Run solver

        Parameters
        ----------
        solver_name : str
            Name of solver
        solverinput : Solver.Input
            Input manager
        solveroutput : Solver.Output
            Output manager

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
