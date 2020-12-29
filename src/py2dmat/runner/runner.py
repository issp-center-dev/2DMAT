#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import subprocess
from abc import ABCMeta, abstractmethod

import numpy as np

from .. import mpi
from ..solver.solver_base import SolverBase


class Runner(object):
    solver: SolverBase

    def __init__(self, solver: SolverBase, nprocs: int = 1, nthreads: int = 1):
        """

        Parameters
        ----------
        Solver: py2dmat.solver.solver_base object
        mpi_info:
        """
        self.solver_name = solver.get_name()
        self.base_solver_input = solver.get_input()
        self.output = solver.get_output()
        path_to_solver = solver.get_path_to_solver()
        run_scheme = solver.get_run_scheme()
        if run_scheme == "mpi_spawn_ready":
            self.run = run_mpispawn_ready(
                path_to_solver,
                nprocs=nprocs,
                nthreads=nthreads,
                comm=mpi.comm(),
            )
        elif run_scheme == "mpi_spawn":
            self.run = run_mpispawn(
                path_to_solver,
                nprocs=nprocs,
                nthreads=nthreads,
                comm=mpi.comm(),
            )
        elif run_scheme == "mpi_spawn_wrapper":
            self.run = run_mpispawn_wrapper(
                path_to_solver,
                nprocs=nprocs,
                nthreads=nthreads,
                comm=mpi.comm(),
            )
        elif run_scheme == "subprocess":
            self.run = run_subprocess(
                path_to_solver,
                nprocs=nprocs,
                nthreads=nthreads,
                comm=mpi.comm(),
            )
        elif run_scheme == "function":
            self.run = run_function(path_to_solver, comm=mpi.comm())
        else:
            msg = f"Unknown scheme: {run_scheme}"
            raise ValueError(msg)

    def submit(self, update_info):
        solverinput = self.base_solver_input
        update_info = solverinput.update_info(update_info)
        self.output.update_info(update_info)
        self.run.submit(self.solver_name, solverinput, self.output)
        results = self.output.get_results()
        return results


class Run(metaclass=ABCMeta):
    def __init__(self, path_to_solver, nprocs=None, nthreads=None, comm=None):
        """
        Parameters
        ----------
        path_to_solver : str
            Path to solver program
        nprocs : int
            Number of process which one solver uses
        nthreads : int
            Number of threads which one solver process uses
        comm : MPI.Comm
            MPI Communicator
        """
        self.path_to_solver = path_to_solver
        self.nprocs = nprocs
        self.nthreads = nthreads
        self.comm = comm

    @abstractmethod
    def submit(self, solver_name, input_info, output_info):
        pass


class run_mpispawn_wrapper(Run):
    def submit(self, solver_name, input_info, output_info):
        raise NotImplementedError()


class run_mpispawn(Run):
    def submit(self, solver_name, input_info, output_info):
        raise NotImplementedError()


class run_mpispawn_ready(Run):
    def submit(self, solver_name, input_info, output_info):
        raise NotImplementedError()


class run_subprocess(Run):
    """
    Invoker via subprocess

    """

    def submit(self, solver_name, solverinput, solveroutput):
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
        base_dir = solveroutput.base_info["output_dir"]
        solverinput.write_input(workdir=base_dir)
        cwd = os.getcwd()
        os.chdir(base_dir)
        command = [self.path_to_solver]
        with open(os.path.join(base_dir, "stdout"), "w") as fi:
            subprocess.run(
                command, stdout=fi, stderr=subprocess.STDOUT, check=True, shell=True
            )
        os.chdir(cwd)
        return 0


class run_function(Run):
    def submit(self, solver_name, input_info, output_info):
        self.path_to_solver()
