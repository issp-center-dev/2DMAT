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

import os
import shutil
import numpy as np

# for type hints
from pathlib import Path
from typing import List, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from mpi4py import MPI

from py2dmat import exception, mpi


class Input(object):
    mpicomm: Optional["MPI.Comm"]
    mpisize: int
    mpirank: int

    root_dir: Path
    output_dir: Path
    dimension: int
    run_scheme: str
    generate_rocking_curve: bool
    string_list: List[str]
    bulk_output_file: Path
    surface_input_file: Path
    surface_template_file: Path
    template_file_origin: List[str]

    def __init__(self, info_base, info_solver, isLogmode, detail_timer):
        self.mpicomm = mpi.comm()
        self.mpisize = mpi.size()
        self.mpirank = mpi.rank()

        self.isLogmode = isLogmode
        self.detail_timer = detail_timer

        self.root_dir = info_base["root_dir"]
        self.output_dir = info_base["output_dir"]

        if info_solver.dimension:
            self.dimension = info_solver.dimension
        else:
            self.dimension = info_base["dimension"]

        # read info
        self.run_scheme = info_solver.run_scheme
        self.generate_rocking_curve = info_solver.generate_rocking_curve

        # NOTE:
        # surf_template_width_for_fortran: Number of strings per line of template.txt data for surf.so.
        # bulk_out_width_for_fortran: Number of strings per line of bulkP.txt data for surf.so.
        if self.run_scheme == "connect_so":
            self.surf_template_width_for_fortran = 128
            self.bulk_out_width_for_fortran = 1024

        self.string_list = info_solver.param.string_list
        if len(self.string_list) != self.dimension:
            raise ValueError("length of string_list does not match dimension")

        self.surface_input_file = Path(info_solver.config.surface_input_file)

        filename = info_solver.config.surface_template_file
        filename = Path(filename).expanduser().resolve()
        self.surface_template_file = self.root_dir / filename
        if not self.surface_template_file.exists():
            raise exception.InputError(
                f"ERROR: surface_template_file ({self.surface_template_file}) does not exist"
            )

        if self.mpirank == 0:
            self._check_template()
            temp_origin = self.load_surface_template_file(filename)
        else:
            temp_origin = None
        if self.mpisize > 1:
            self.template_file_origin = self.mpicomm.bcast(temp_origin, root=0)
        else:
            self.template_file_origin = temp_origin

        if self.run_scheme == "connect_so":
            filename = info_solver.config.bulk_output_file
            filename = Path(filename).expanduser().resolve()
            self.bulk_output_file = self.root_dir / filename
            if not self.bulk_output_file.exists():
                raise exception.InputError(
                    f"ERROR: bulk_output_file ({self.bulk_output_file}) does not exist"
                )

            if self.mpirank == 0:
                bulk_f = self.load_bulk_output_file(filename)
            else:
                bulk_f = None
            if self.mpisize > 1:
                self.bulk_file = self.mpicomm.bcast(bulk_f, root=0)
            else:
                self.bulk_file = bulk_f
        else:
            filename = info_solver.config.bulk_output_file
            filename = Path(filename).expanduser().resolve()
            self.bulk_output_file = self.root_dir / filename
            if not self.bulk_output_file.exists():
                raise exception.InputError(
                    f"ERROR: bulk_output_file ({self.bulk_output_file}) does not exist"
                )

    def load_surface_template_file(self, filename):
        template_file = []
        with open(self.surface_template_file) as f:
            for line in f:
                template_file.append(line)
        return template_file

    def load_bulk_output_file(self, filename):
        bulk_file = []
        with open(self.bulk_output_file) as f:
            for line in f:
                line = line.replace("\t", " ").replace("\n", " ")
                line = line.encode().ljust(self.bulk_out_width_for_fortran)
                bulk_file.append(line)
        bulk_f = np.array(bulk_file)
        return bulk_f

    def prepare(self, x: np.ndarray, args):
        if self.isLogmode:
            time_sta = time.perf_counter()

        x_list = x
        step, iset = args

        dimension = self.dimension
        string_list = self.string_list
        bulk_output_file = self.bulk_output_file
        solver_input_file = self.surface_input_file
        fitted_x_list = []
        for index in range(dimension):
            fitted_value = " " if x_list[index] >= 0 else ""
            fitted_value += format(x_list[index], ".8f")
            fitted_value = fitted_value[: len(string_list[index])]
            fitted_x_list.append(fitted_value)

        if self.isLogmode:
            time_end = time.perf_counter()
            self.detail_timer["make_surf_input"] += time_end - time_sta

        if self.isLogmode:
            time_sta = time.perf_counter()

        folder_name = "."
        if self.generate_rocking_curve:
            folder_name = self._pre_bulk(step, bulk_output_file, iset)
        else:
            if self.run_scheme == "connect_so":
                folder_name = "."

            elif self.run_scheme == "subprocess":
                # make workdir and copy bulk output file
                folder_name = self._pre_bulk(step, bulk_output_file, iset)

        if self.isLogmode:
            time_end = time.perf_counter()
            self.detail_timer["prepare_Log-directory"] += time_end - time_sta

        if self.isLogmode:
            time_sta = time.perf_counter()

        self._replace(fitted_x_list, folder_name)

        if self.isLogmode:
            time_end = time.perf_counter()
            self.detail_timer["make_surf_input"] += time_end - time_sta

        return fitted_x_list, folder_name

    def _pre_bulk(self, Log_number, bulk_output_file, iset):
        folder_name = "Log{:08d}_{:08d}".format(Log_number, iset)
        os.makedirs(folder_name, exist_ok=True)
        if self.run_scheme == "connect_so":
            pass
        else:  # self.run_scheme == "subprocess":
            shutil.copy(
                bulk_output_file, os.path.join(folder_name, bulk_output_file.name)
            )
        return folder_name

    def _replace(self, fitted_x_list, folder_name):
        template_file = []
        if self.run_scheme == "subprocess":
            file_output = open(
                os.path.join(folder_name, self.surface_input_file), "w"
            )
        for line in self.template_file_origin:
            for index in range(self.dimension):
                if line.find(self.string_list[index]) != -1:
                    line = line.replace(
                        self.string_list[index], fitted_x_list[index]
                    )

            if self.run_scheme == "connect_so":
                line = line.replace("\t", " ").replace("\n", " ")
                line = line.encode().ljust(self.surf_template_width_for_fortran)
                template_file.append(line)

            elif self.run_scheme == "subprocess":
                file_output.write(line)

        if self.run_scheme == "connect_so":
            self.template_file = np.array(template_file)
        elif self.run_scheme == "subprocess":
            file_output.close()

    def _check_template(self) -> None:
        found = [False] * self.dimension
        with open(self.surface_template_file, "r") as file_input:
            for line in file_input:
                for index, placeholder in enumerate(self.string_list):
                    if line.find(placeholder) != -1:
                        found[index] = True
        if not np.all(found):
            msg = "ERROR: the following labels do not appear in the template file:"
            for label, f in zip(self.string_list, found):
                if not f:
                    msg += "\n"
                    msg += label
            raise exception.InputError(msg)

