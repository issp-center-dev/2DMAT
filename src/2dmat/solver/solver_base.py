#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class Solver(object, metaclass =ABCMeta):
    @abstractmethod
    def get_run_scheme(self):
        """
        Return
        -------
        str
            run_scheme.
        """
        pass

    @abstractmethod
    def get_path_to_solver(self):
        """
        Return
        -------
        str
            Path to solver.
        """
        pass

    @abstractmethod
    def get_name(self):
        """
        Return
        -------
        str
            Name of solver.
        """
        pass

    @abstractmethod
    def get_input(self):
        """
        Return
        -------
        Input object
        """
        pass

    @abstractmethod
    def get_output(self):
        """
        Return
        -------
        Output object
        """
        pass

    class Input(object):
        """
        Input manager.

        Attributes
        ----------
        base_info : Any
            Common parameter.
        """

        def __init__(self):
            self.base_info = None

        def update_info(self, update_info):
            """
            Update information.

            Parameters
            ----------
            update_info : dict
                Atomic structure.

            """
            raise NotImplementedError()

        def write_input(self, workdir):
            """
            Generate input files of the solver program.

            Parameters
            ----------
            workdir : str
                Path to working directory.
            """
            raise NotImplementedError()

        def from_directory(self, base_input_dir):
            """
            Set information from files in the base_input_dir

            Parameters
            ----------
            base_input_dir : str
                Path to the directory including base input files.
            """
            # set information of base_input and pos_info from files in base_input_dir
            raise NotImplementedError()

        def cl_args(self, nprocs, nthreads, workdir):
            """
            Generate command line arguments of the solver program.

            Parameters
            ----------
            nprocs : int
                The number of processes.
            nthreads : int
                The number of threads.
            workdir : str
                Path to the working directory.

            Returns
            -------
            args : list[str]
                Arguments of command
            """
            return []

    class Output(object):
        """
        Output manager.
        """
        def get_results(self, output_info):
            """
            Get energy and structure obtained by the solver program.

            Parameters
            ----------
            output_info : dict

            Returns
            -------
            """
            raise NotImplementedError()


