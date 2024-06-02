# -*- coding: utf-8 -*-

# 2DMAT -- Data-analysis software of quantum beam diffraction experiments for 2D material structure
# Copyright (C) 2020- The University of Tokyo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

from abc import ABCMeta, abstractmethod

import numpy as np

import py2dmat
import py2dmat.util.read_matrix
import py2dmat.util.mapping
import py2dmat.util.limitation
from py2dmat.util.logger import Logger
from py2dmat.exception import InputError

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
    def submit(self, solver):
        pass


class Runner(object):
    #solver: "py2dmat.solver.SolverBase"
    logger: Logger

    def __init__(self,
                 solver,
                 info: Optional[py2dmat.Info] = None,
                 mapping = None,
                 limitation = None) -> None:
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
            b: Optional[np.ndarray] = py2dmat.util.read_matrix.read_matrix(
                info_mapping.get("b", [])
            )
            if A is not None:
                if A.size == 0:
                    A = None
                elif A.ndim != 2:
                    raise InputError("A should be a matrix")
            if b is not None:
                if b.size == 0:
                    b = None
                elif b.ndim == 2:
                    if b.shape[1] == 1:
                        b = b.reshape(-1)
                    else:
                        raise InputError("b should be a vector")
                elif b.ndim > 2:
                    raise InputError("b should be a vector")
            self.mapping = py2dmat.util.mapping.Affine(A=A, b=b)
        else:
            self.mapping = mapping
        
        self.ndim = info.base["dimension"]
        if limitation is None:
            info_limitation = info.runner.get("limitation",{})
            co_a: np.ndarray = py2dmat.util.read_matrix.read_matrix(
                info_limitation.get("co_a", [])
            )
            co_b: np.ndarray = py2dmat.util.read_matrix.read_matrix(
                info_limitation.get("co_b", [])
            )
            if co_a.size == 0:
                is_set_co_a = False
            else:
                is_set_co_a = True
                if co_a.ndim != 2:
                    raise InputError("co_a should be a matrix")
                if co_a.shape[1] != self.ndim:
                    msg ='The number of columns in co_a should be equal to'
                    msg+='the value of "dimension" in the [base] section'
                    raise InputError(msg)
                n_row_co_a = co_a.shape[0]
            if co_b.size == 0:
                if not is_set_co_a :
                    is_set_co_b = False
                else: # is_set_co_a is True
                    msg = "ERROR: co_a is defined but co_b is not."
                    raise InputError(msg)
            elif co_b.ndim == 2:
                if is_set_co_a:
                    if co_b.shape[0] == 1 or co_b.shape[1] == 1:
                        is_set_co_b = True
                        co_b = co_b.reshape(-1)
                    else:
                        raise InputError("co_b should be a vector")
                    if co_b.size != n_row_co_a:
                        msg ='The number of row in co_a should be equal to'
                        msg+='the number of size in co_b'
                        raise InputError(msg)
                else: # not is_set_co_a:
                    msg = "ERROR: co_b is defined but co_a is not."
                    raise InputError(msg)
            elif co_b.ndim > 2:
                raise InputError("co_b should be a vector")
            
            if is_set_co_a and is_set_co_b:
                is_limitation = True
            elif (not is_set_co_a) and (not is_set_co_b):
                is_limitation = False
            else:
                msg = "ERROR: Both co_a and co_b must be defined."
                raise InputError(msg)

            self.limitation = py2dmat.util.limitation.Inequality(co_a, co_b, is_limitation)

    def prepare(self, proc_dir: Path):
        self.logger.prepare(proc_dir)

    def submit(
        self, message: py2dmat.Message, nprocs: int = 1, nthreads: int = 1
    ) -> float:
        if self.limitation.judge(message.x):
            x = self.mapping(message.x)
            message_indeed = py2dmat.Message(x, message.step, message.set)
            # self.solver.prepare(message_indeed)
            # cwd = os.getcwd()
            # os.chdir(self.solver.work_dir)
            # self.solver.run(nprocs, nthreads)
            # os.chdir(cwd)
            # result = self.solver.get_results()
            result = self.solver.evaluate(message_indeed)
        else:
            result = np.inf
        self.logger.count(message, result)
        return result

    def post(self) -> None:
        self.logger.write()
