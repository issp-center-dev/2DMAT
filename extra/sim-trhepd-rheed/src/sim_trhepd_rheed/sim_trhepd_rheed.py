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

import itertools
import os
import sys
import time
import ctypes
import subprocess

import numpy as np

import py2dmat
from py2dmat import exception, mpi
from .input import Input
from .output import Output
from .parameter import SolverInfo

from pydantic import ValidationError

# for type hints
from pathlib import Path
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from mpi4py import MPI


class Solver(py2dmat.solver.SolverBase):
    mpicomm: Optional["MPI.Comm"]
    mpisize: int
    mpirank: int
    run_scheme: str
    isLogmode: bool
    detail_timer: Dict
    path_to_solver: Path

    def __init__(self, info: py2dmat.Info):
        super().__init__(info)

        self.mpicomm = mpi.comm()
        self.mpisize = mpi.size()
        self.mpirank = mpi.rank()

        self._name = "sim_trhepd_rheed_mb_connect"

        try:
            info_solver = SolverInfo(**info.solver)
        except ValidationError as e:
            print("ERROR: {}".format(e))
            sys.exit(1)

        self.run_scheme = info_solver.run_scheme

        if self.run_scheme == "connect_so":
            self.load_so()

        elif self.run_scheme == "subprocess":
            # path to surf.exe
            p2solver = info_solver.config.surface_exec_file
            if os.path.dirname(p2solver) != "":
                # ignore ENV[PATH]
                self.path_to_solver = self.root_dir / Path(p2solver).expanduser()
            else:
                for P in itertools.chain(
                    [self.root_dir], os.environ["PATH"].split(":")
                ):
                    self.path_to_solver = Path(P) / p2solver
                    if os.access(self.path_to_solver, mode=os.X_OK):
                        break
            if not os.access(self.path_to_solver, mode=os.X_OK):
                raise exception.InputError(f"ERROR: solver ({p2solver}) is not found")

        self.isLogmode = False
        self.set_detail_timer()

        self.input = Input(info.base, info_solver, self.isLogmode, self.detail_timer)
        self.output = Output(info.base, info_solver, self.isLogmode, self.detail_timer)

    def set_detail_timer(self) -> None:
        # TODO: Operate log_mode with toml file. Generate txt of detail_timer.
        if self.isLogmode:
            self.detail_timer = {}
            self.detail_timer["prepare_Log-directory"] = 0
            self.detail_timer["make_surf_input"] = 0
            self.detail_timer["launch_STR"] = 0
            self.detail_timer["load_STR_result"] = 0
            self.detail_timer["convolution"] = 0
            self.detail_timer["normalize_calc_I"] = 0
            self.detail_timer["calculate_R-factor"] = 0
            self.detail_timer["make_RockingCurve.txt"] = 0
            self.detail_timer["delete_Log-directory"] = 0
        else:
            self.detail_timer = {}

    def default_run_scheme(self) -> str:
        """
        Return
        -------
        str
            run_scheme.
        """
        return self.run_scheme

    def command(self) -> List[str]:
        """Command to invoke solver"""
        return [str(self.path_to_solver)]

    def evaluate(self, x: np.ndarray, args = (), nprocs: int = 1, nthreads: int = 1) -> float:
        self.prepare(x, args)
        cwd = os.getcwd()
        os.chdir(self.work_dir)
        self.run(nprocs, nthreads)
        os.chdir(cwd)
        result = self.get_results()
        return result

    def prepare(self, x: np.ndarray, args) -> None:
        fitted_x_list, subdir = self.input.prepare(x, args)
        self.work_dir = self.proc_dir / Path(subdir)

        self.output.prepare(fitted_x_list)

    def get_results(self) -> float:
        return self.output.get_results(self.work_dir)

    def load_so(self) -> None:
        self.lib = np.ctypeslib.load_library("surf.so", os.path.dirname(__file__))
        self.lib.surf_so.argtypes = (
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            np.ctypeslib.ndpointer(),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            np.ctypeslib.ndpointer(),
            np.ctypeslib.ndpointer(),
        )
        self.lib.surf_so.restype = ctypes.c_void_p

    def launch_so(self) -> None:

        n_template_file = len(self.input.template_file)
        m_template_file = self.input.surf_template_width_for_fortran
        n_bulk_file = len(self.input.bulk_file)
        m_bulk_file = self.input.bulk_out_width_for_fortran

        # NOTE: The "20480" is related to the following directive in surf_so.f90.
        # character(c_char), intent(inout) :: surf_out(20480)
        emp_str = " " * 20480
        self.output.surf_output = np.array([emp_str.encode()])
        self.lib.surf_so(
            ctypes.byref(ctypes.c_int(n_template_file)),
            ctypes.byref(ctypes.c_int(m_template_file)),
            self.input.template_file,
            ctypes.byref(ctypes.c_int(n_bulk_file)),
            ctypes.byref(ctypes.c_int(m_bulk_file)),
            self.input.bulk_file,
            self.output.surf_output,
        )
        self.output.surf_output = self.output.surf_output[0].decode().splitlines()

    def _run_by_subprocess(self, command: List[str]) -> None:
        with open("stdout", "w") as fi:
            subprocess.run(
                command,
                stdout=fi,
                stderr=subprocess.STDOUT,
                check=True,
            )

    def run(self, nprocs: int = 1, nthreads: int = 1) -> None:
        if self.isLogmode:
            time_sta = time.perf_counter()

        if self.run_scheme == "connect_so":
            self.launch_so()
        elif self.run_scheme == "subprocess":
            self._run_by_subprocess([str(self.path_to_solver)])

        if self.isLogmode:
            time_end = time.perf_counter()
            self.detail_timer["launch_STR"] += time_end - time_sta

