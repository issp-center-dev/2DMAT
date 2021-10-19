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
        info_s = info.solver

        # Check keywords
        def check_keywords(key, segment, registered_list):
            if (key in registered_list) is False:
                msg = "Error: {} in {} is not correct keyword.".format(key, segment)
                raise RuntimeError(msg)

        keywords_solver = ["name", "config", "reference", "param"]
        keywords = {}
        keywords["config"] = ["sxrd_exec_file", "bulk_struc_in_file"]
        keywords["reference"] = ["f_in_file"]
        keywords["param"] = [
            "scale_factor",
            "type_vector",
            "opt_scale_factor",
            "domain",
        ]

        for key in info_s.keys():
            check_keywords(key, "solver", keywords_solver)
            if key == "name":
                continue
            for key_child in info_s[key].keys():
                check_keywords(key_child, key, keywords[key])

        # Check keywords of param.domain list
        keywords_domain = ["domain_occupancy", "atom"]
        keywords_atom = [
            "name",
            "pos_center",
            "DWfactor",
            "occupancy",
            "displace_vector",
            "opt_DW",
            "opt_occupancy",
        ]
        for domain in info_s["param"]["domain"]:
            for key_domain in domain.keys():
                check_keywords(key_domain, "domain", keywords_domain)
            for atom in domain["atom"]:
                for key_atom in atom.keys():
                    check_keywords(key_atom, "atom", keywords_atom)

        # Set environment
        p2solver = info_s["config"].get("sxrd_exec_file", "sxrdcalc")
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
        self.path_to_f_in = info_s["reference"]["f_in_file"]
        self.path_to_bulk = info_s["config"]["bulk_struc_in_file"]
        self.input = Solver.Input(info)

    def prepare(self, message: py2dmat.Message) -> None:
        self.work_dir = self.proc_dir
        self.input.prepare(message)
        import shutil

        for file in ["lsfit.in", self.path_to_f_in, self.path_to_bulk]:
            shutil.copyfile(
                os.path.join(self.root_dir, file), os.path.join(self.work_dir, file)
            )

    def run(self, nprocs: int = 1, nthreads: int = 1) -> None:
        self._run_by_subprocess([str(self.path_to_solver), "lsfit.in"])

    def get_results(self) -> float:
        # Get R-factor
        with open(os.path.join(self.work_dir, "stdout"), "r") as fr:
            lines = fr.readlines()
            l_rfactor = [line for line in lines if "R =" in line][0]
            rfactor = float(l_rfactor.strip().split("=")[1])
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
            # Set default values
            # Initial values
            self.info_param["opt_scale_factor"] = self.info_param.get(
                "opt_scale_factor", False
            )
            self.info_param["scale_factor"] = self.info_param.get("scale_factor", 1.0)

            # Read info (a, b, c, alpha, beta, gamma ) from blk or surf files.
            self.lattice_info = self._read_lattice_info(
                info_s["config"]["bulk_struc_in_file"]
            )
            # Generate input file
            self._write_input_file(
                info_s["config"], info_s["reference"], info_s["param"]["domain"]
            )

        def prepare(self, message: py2dmat.Message):
            x_list = message.x
            step = message.step
            extra = message.set > 0

            # Generate fit file
            # Add variables by numpy array.(Variables are updated in optimization process).
            self._write_fit_file(self.lattice_info, self.info_param, x_list)

        def _read_lattice_info(self, file_name: str):
            with open(file_name, "r") as fr:
                lines = fr.readlines()
            # (a, b, c, alpha, beta, gamma)
            lattice_info = lines[1]
            return lattice_info

        def _write_input_file(self, info_config, info_reference, info_domain):
            with open("lsfit.in", "w") as fw:
                fw.write("do = ls_fit\n")
                fw.write(
                    "bulk_struc_in_file = {}\n".format(
                        info_config["bulk_struc_in_file"]
                    )
                )
                for idx, domain in enumerate(info_domain):
                    fw.write(
                        "fit_struc_in_file{} = {}\n".format(
                            idx + 1, "ls_{}.fit".format(idx + 1)
                        )
                    )
                    fw.write(
                        "fit_coord_out_file{} = {}\n".format(
                            idx + 1, "ls_{}.sur".format(idx + 1)
                        )
                    )
                fw.write("nr_domains = {}\n".format(len(info_domain)))
                for idx, domain in enumerate(info_domain):
                    fw.write(
                        "domain_occ{} = {}\n".format(
                            idx + 1, domain["domain_occupancy"]
                        )
                    )
                for key, value in info_reference.items():
                    fw.write("{} = {}\n".format(key, value))
                fw.write("max_iteration = 0\n")

        def _write_fit_file(self, lattice_info: str, info_param, variables):
            type_vector = [type_idx for type_idx in info_param["type_vector"]]
            for idx, domain in enumerate(info_param["domain"]):
                with open("ls_{}.fit".format(idx + 1), "w") as fw:
                    fw.write("# Temporary file\n")
                    fw.write("{}".format(lattice_info))
                    type_atom = []
                    for atom_info in domain["atom"]:
                        position = atom_info["pos_center"]
                        fw.write(
                            "pos {} {} {} {} {} {}\n".format(
                                atom_info["name"],
                                position[0],
                                position[1],
                                position[2],
                                atom_info["DWfactor"],
                                atom_info.get("occupancy", 1.0),
                            )
                        )
                        for idx_atom, displ in enumerate(atom_info["displace_vector"]):
                            fw.write(
                                "displ{} {} {} {} {}\n".format(
                                    idx_atom + 1,
                                    int(displ[0]),
                                    displ[1],
                                    displ[2],
                                    displ[3],
                                )
                            )
                            type_atom.append(int(displ[0]))
                            if "opt_DW" in atom_info.keys():
                                DW_info = atom_info["opt_DW"]
                                fw.write(
                                    "dw_par {} {}\n".format(DW_info[0], DW_info[1])
                                )
                                type_atom.append(DW_info[0])
                            if "opt_occupancy" in atom_info.keys():
                                fw.write("occ {} \n".format(atom_info["opt_occupancy"]))
                                type_atom.append(atom_info["opt_occupancy"])
                    if info_param["opt_scale_factor"] is True and idx == 0:
                        type_vector.insert(0, 0)
                        type_atom.append(0)
                    else:
                        fw.write("start_par 0 {}\n".format(info_param["scale_factor"]))
                    for type_idx, variable in zip(type_vector, variables):
                        if type_idx in type_atom:
                            fw.write(
                                "start_par {} {}\n".format(int(type_idx), variable)
                            )
