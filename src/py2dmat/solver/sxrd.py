from typing import List
import itertools
import os
import os.path
import shutil
from pathlib import Path

import numpy as np

import py2dmat
from py2dmat import exception


class Solver(py2dmat.solver.SolverBase):
    path_to_solver: Path

    dimension: int

    def __init__(self, info: py2dmat.Info):
        super().__init__(info)

        self._name = "sxrd"
        p2solver = info.solver["config"].get("sxrd_exec_file", "surf.exe")
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

        self.input = Solver.Input(info)

    def default_run_scheme(self):
        """
        Return
        -------
        str
            run_scheme.
        """
        return "subprocess"

    def command(self) -> List[str]:
        """Command to invoke solver"""
        return [str(self.path_to_solver + " lsfit.in")]

    def prepare(self, message: py2dmat.Message) -> None:
        fitted_x_list, subdir = self.input.prepare(message)
        self.work_dir = self.proc_dir / Path(subdir)

    def get_results(self) -> float:
        # Get R-factor
        with open("stdout", "r") as fr:
            lines = fr.readlines()
            l_rfactor = [line for line in lines if 'R =' in line][0]
            rfactor = float(l_Rfactor.strip().split("=")[1])
        return rfactor

    class Input(object):
        root_dir: Path
        output_dir: Path
        dimension: int

        def __init__(self, info):
            self.dimension = info.base["dimension"]
            self.root_dir = info.base["root_dir"]
            self.output_dir = info.base["output_dir"]

            info_s = info.solver
            self.info_param = info_s["param"]
            # Read info (a, b, c, alpha, beta, gamma ) from blk or surf files.
            self.lattice_info = self._read_lattice_info(info_s["config"]["bulk_struc_in_file"])
            # Generate input file
            self._write_input_file(info_s["config"], info_s["reference"], info_s["param"]["domain"])


        def prepare(self, message: py2dmat.Message):
            x_list = message.x
            step = message.step
            extra = message.set > 0

            # Generate fit file
            # Add variables by numpy array.(Variables are updated in optimization process).
            initial_params = self.info_param["initial_params"]
            self.info_param["opt_scale_factor"] = True
            if self.info_param["opt_scale_factor"] is True:
                initial_params.insert(0, self.info_param["scale_factor"])
            variables = np.array(initial_params)
            self._write_fit_file(self.lattice_info, self.info_param, x_list)

        def _read_lattice_info(self, file_name: str):
            with open(file_name, "r") as fr:
                lines = fr.readlines()
            # (a, b, c, alpha, beta, gamma)
            lattice_info = lines[1]
            return (lattice_info)

        def _write_input_file(self, info_config, info_reference, info_domain):
            with open("lsfit.in", "w") as fw:
                fw.write("do = ls_fit\n")
                fw.write("bulk_struc_in_file = {}\n".format(info_config["bulk_struc_in_file"]))
                for idx, domain in enumerate(info_domain):
                    fw.write("fit_struc_in_file{} = {}\n".format(idx + 1, "ls_{}.fit".format(idx + 1)))
                    fw.write("fit_coord_out_file{} = {}\n".format(idx + 1, "ls_{}.sur".format(idx + 1)))
                fw.write("nr_domains = {}\n".format(len(info_domain)))
                for idx, domain in enumerate(info_domain):
                    fw.write("domain_occ{} = {}\n".format(idx + 1, domain["domain_occupancy"]))
                for key, value in info_reference.items():
                    fw.write("{} = {}\n".format(key, value))
                fw.write("max_iteration = 0\n")

        def _write_fit_file(self, lattice_info: str, info_param, variables: py2dmat.Message.x):
            type_vector = [type_idx for type_idx in info_param["type_vector"]]

            for idx, domain in enumerate(info_param["domain"]):
                with open("ls_{}.fit".format(idx + 1), "w") as fw:
                    fw.write("# Temporary file\n")
                    fw.write("{}".format(lattice_info))
                    for atom_info in domain["atom"]:
                        position = atom_info["pos_center"]
                        fw.write(
                            "pos {} {} {} {} {} {}\n".format(atom_info["name"], position[0], position[1], position[2],
                                                             atom_info["DWfactor"], atom_info["occupancy"]))
                        for idx_atom, displ in enumerate(atom_info["displace_vector"]):
                            fw.write(
                                "displ{} {} {} {} {}\n".format(idx_atom + 1, int(displ[0]), displ[1], displ[2], displ[3]))
                            if "opt_DW" in atom_info.keys():
                                DW_info = atom_info["opt_DW"]
                                fw.write("dw_par {} {}\n".format(DW_info[0], DW_info[1]))
                            if "opt_occupancy" in atom_info.keys():
                                fw.write("occ {} \n".format(atom_info["opt_occupancy"]))
                    if info_param["opt_scale_factor"] is True and idx==0:
                        type_vector.insert(0, 0)
                    else:
                        fw.write("start_par 0 {}\n".format(info_param["scale_factor"]))
                    for type_idx, variable in zip(type_vector, variables):
                        fw.write("start_par {} {}\n".format(int(type_idx), variable))

