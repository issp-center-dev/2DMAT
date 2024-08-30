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

from typing import Dict, List, Tuple
import itertools
import os
import sys
import shutil
from pathlib import Path
import subprocess

import numpy as np

import py2dmat
from py2dmat import exception
from .input import Input
from .parameter import SolverInfo

from pydantic import ValidationError


class Solver(py2dmat.solver.SolverBase):
    path_to_solver: Path
    dimension: int

    def __init__(self, info: py2dmat.Info):
        super().__init__(info)

        self._name = "sxrd"
        # info_s = info.solver

        try:
            info_s = SolverInfo(**info.solver)
        except ValidationError as e:
            print("ERROR: {}".format(e))
            sys.exit(1)

        # # Check keywords
        # def check_keywords(key, segment, registered_list):
        #     if (key in registered_list) is False:
        #         msg = "Error: {} in {} is not correct keyword.".format(key, segment)
        #         raise RuntimeError(msg)

        # keywords_solver = ["name", "config", "reference", "param"]
        # keywords = {}
        # keywords["config"] = ["sxrd_exec_file", "bulk_struc_in_file"]
        # keywords["reference"] = ["f_in_file"]
        # keywords["param"] = [
        #     "scale_factor",
        #     "type_vector",
        #     "opt_scale_factor",
        #     "domain",
        # ]

        # for key in info_s.keys():
        #     check_keywords(key, "solver", keywords_solver)
        #     if key == "name":
        #         continue
        #     for key_child in info_s[key].keys():
        #         check_keywords(key_child, key, keywords[key])

        # # Check keywords of param.domain list
        # keywords_domain = ["domain_occupancy", "atom"]
        # keywords_atom = [
        #     "name",
        #     "pos_center",
        #     "DWfactor",
        #     "occupancy",
        #     "displace_vector",
        #     "opt_DW",
        #     "opt_occupancy",
        # ]
        # for domain in info_s["param"]["domain"]:
        #     for key_domain in domain.keys():
        #         check_keywords(key_domain, "domain", keywords_domain)
        #     for atom in domain["atom"]:
        #         for key_atom in atom.keys():
        #             check_keywords(key_atom, "atom", keywords_atom)

        # Set environment
        #p2solver = info_s["config"].get("sxrd_exec_file", "sxrdcalc")
        p2solver = info_s.config.sxrd_exec_file
        if os.path.dirname(p2solver) != "":
            # ignore ENV[PATH]
            self.path_to_solver = self.root_dir / Path(p2solver).expanduser()
        else:
            for P in itertools.chain([self.root_dir], os.environ["PATH"].split(":")):
                self.path_to_solver = Path(P) / p2solver
                if os.access(self.path_to_solver, mode=os.X_OK):
                    break
        if not os.access(self.path_to_solver, mode=os.X_OK):
            raise exception.InputError(f"ERROR: solver ({p2solver}) is not found")
        #self.path_to_f_in = info_s["reference"]["f_in_file"]
        #self.path_to_bulk = info_s["config"]["bulk_struc_in_file"]
        self.path_to_f_in = info_s.reference.f_in_file
        self.path_to_bulk = info_s.config.bulk_struc_in_file
        self.input = Input(info.base, info_s)

    def evaluate(self, x: np.ndarray, args = (), nprocs: int = 1, nthreads: int = 1) -> float:
        self.prepare(x, args)
        cwd = os.getcwd()
        os.chdir(self.work_dir)
        self.run(nprocs, nthreads)
        os.chdir(cwd)
        result = self.get_results()
        return result

    def prepare(self, x: np.ndarray, args) -> None:
        self.work_dir = self.proc_dir
        self.input.prepare(x, args)
        import shutil

        for file in ["lsfit.in", self.path_to_f_in, self.path_to_bulk]:
            shutil.copyfile(
                os.path.join(self.root_dir, file), os.path.join(self.work_dir, file)
            )

    def run(self, nprocs: int = 1, nthreads: int = 1) -> None:
        self._run_by_subprocess([str(self.path_to_solver), "lsfit.in"])

    def _run_by_subprocess(self, command: List[str]) -> None:
        with open("stdout", "w") as fi:
            subprocess.run(
                command,
                stdout=fi,
                stderr=subprocess.STDOUT,
                check=True,
            )

    def get_results(self) -> float:
        # Get R-factor
        with open(os.path.join(self.work_dir, "stdout"), "r") as fr:
            lines = fr.readlines()
            l_rfactor = [line for line in lines if "R =" in line][0]
            rfactor = float(l_rfactor.strip().split("=")[1])
        return rfactor

