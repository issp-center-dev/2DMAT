#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import subprocess
from abc import ABCMeta, abstractmethod

class Runner(object):
    def __init__(self, Solver, mpi_info):
        """

        :param solver: 2dmat.solver.solver_base object
        :param mpi_info:
        """
        self.solver_name = Solver.get_name()
        self.base_solver_input = Solver.get_input()
        self.output = Solver.get_output()
        path_to_solver = Solver.get_path_to_solver()
        run_scheme = Solver.get_run_schemes()
        try:
            #Is it better to define mpi_info class ?
            comm = mpi_info["comm"]
            nprocs_per_solver = mpi_info["nprocs_per_solver"]
            nthreads_per_proc = mpi_info["nthreads_per_proc"]
        except KeyError:
            print("Error: key for mpi_info.")
            sys.exit(1)
        if run_scheme == "mpi_spawn_ready":
            self.run = run_mpispawn_ready(path_to_solver, nprocs_per_solver, nthreads_per_proc, comm)
        elif run_scheme == "mpi_spawn":
            self.run = run_mpispawn(path_to_solver, nprocs_per_solver, nthreads_per_proc, comm)
        elif run_scheme == "mpi_spawn_wrapper":
            self.run = run_mpispawn_wrapper(path_to_solver, nprocs_per_solver, nthreads_per_proc, comm)
        elif run_scheme == "subprocess":
            self.run = run_subprocess(path_to_solver, nprocs_per_solver, nthreads_per_proc, comm)
        else:
            msg = "Unknown scheme: {}".format(run_scheme)
            raise ValueError(msg)

    def submit(self, update_info = None):
        solverinput = self.base_solver_input
        if update_info is not None:
            solverinput.update_info(update_info)
        self.run.submit(self.solver_name, solverinput, self.output)
        results = self.output.get_results(self.output)
        return results

class Run(metaclass = ABCMeta):
    def __init__(self, path_to_solver, nprocs, nthreads, comm):
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
    def submit(self, solver_name, input_info, output_info):
        """
            Run solver

            Parameters
            ----------
            solver_name : str
                Name of solver
            solverinput : Solver.Input
                Input manager
            output_dir : str
                Path to directory where a solver saves output

            Returns
            -------
            status : int
                Always returns 0

            Raises
            ------
            RuntimeError
                Raises RuntimeError when solver failed.
            """
        try:
            output_dir = output_info["output_dir"]
        except KeyError:
            print("Error: output_info does not have the key output_dir.")
            sys.exit(1)

        input_info.write_input(output_dir=output_dir)
        cwd = os.getcwd()
        os.chdir(output_dir)
        args = input_info.cl_args(self.nprocs, self.nthreads, output_dir)
        command = [self.path_to_solver]
        command.extend(args)
        with open(os.path.join(output_dir, "stdout"), "w") as fi:
            try:
                subprocess.run(command, stdout=fi, stderr=subprocess.STDOUT, check=True)
            except subprocess.CalledProcessError as e:
                raise
        os.chdir(cwd)
        return 0
