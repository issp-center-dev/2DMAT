from typing import List
import itertools
import os
import os.path
import shutil
from pathlib import Path
import subprocess
import time
from . import lib_make_convolution

import numpy as np

import py2dmat
from py2dmat import exception, mpi

import ctypes

from typing import TYPE_CHECKING

import copy

class Solver(py2dmat.solver.SolverBase):
    path_to_solver: Path

    def __init__(self, info: py2dmat.Info):
        super().__init__(info)
        self.mpicomm = mpi.comm()
        self.mpisize = mpi.size()
        self.mpirank = mpi.rank()
        
        self._name = "sim_trhepd_rheed_mb_connect"

        self.run_scheme = info.solver.get("run_scheme",None)
        scheme_list = ["subprocess","connect_so"]
        scheme_judge = [i == self.run_scheme for i in scheme_list]

        if not any(scheme_judge):
            raise exception.InputError(
                    "ERROR : Input scheme is incorrect."
                )

        if self.run_scheme == "connect_so":
            self.load_so()
        
        elif self.run_scheme == "subprocess":
            #path to surf.exe
            p2solver = info.solver["config"].get("surface_exec_file", "surf.exe")
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
        
        self.log_mode = False
        self.set_detail_timer()

        self.input = Solver.Input(info,self.detail_timer)
        self.output = Solver.Output(info,self.detail_timer)
         
    def set_detail_timer(self):
        # TODO: Operate log_mode with toml file. Generate txt of detail_timer.
        if self.log_mode:
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
            self.detail_timer = None

    def default_run_scheme(self):
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

    def prepare(self, message: py2dmat.Message) -> None:
        fitted_x_list, subdir = self.input.prepare(message)
        self.work_dir = self.proc_dir / Path(subdir)

        self.output.prepare(fitted_x_list)

    def get_results(self) -> float:
        return self.output.get_results(self.work_dir)
    
    def load_so(self):
        self.lib = np.ctypeslib.load_library("surf.so",os.path.dirname(__file__) )
        self.lib.surf_so.argtypes = (
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_int),
                np.ctypeslib.ndpointer(),
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_int),
                np.ctypeslib.ndpointer(),
                np.ctypeslib.ndpointer()
                )
        self.lib.surf_so.restype = ctypes.c_void_p
    
    def launch_so(self):
       
        n_template_file = len(self.input.template_file)
        m_template_file = self.input.surf_tempalte_width_for_fortran
        n_bulk_file = len(self.input.bulk_file)
        m_bulk_file = self.input.bulk_out_width_for_fortran
        
        # NOTE: The "20480" is related to the following directive in surf_so.f90.
        # character(c_char), intent(inout) :: surf_out(20480)
        emp_str = ' '*20480
        self.output.surf_output = np.array([emp_str.encode()])
        self.lib.surf_so(
                ctypes.byref(ctypes.c_int(n_template_file)),
                ctypes.byref(ctypes.c_int(m_template_file)),
                self.input.template_file,
                ctypes.byref(ctypes.c_int(n_bulk_file)),
                ctypes.byref(ctypes.c_int(m_bulk_file)),
                self.input.bulk_file,
                self.output.surf_output
                )
        self.output.surf_output = self.output.surf_output[0].decode().splitlines()
    
    def run(self, nprocs: int = 1, nthreads: int = 1) -> None:
        if self.log_mode : time_sta = time.perf_counter()
        
        if self.run_scheme == "connect_so":
            self.launch_so()
        elif self.run_scheme == "subprocess":
            self._run_by_subprocess([str(self.path_to_solver)])
        
        if self.log_mode:
            time_end = time.perf_counter()
            self.detail_timer["launch_STR"] += time_end - time_sta
             
    class Input(object):
        root_dir: Path
        output_dir: Path
        dimension: int
        string_list: List[str]
        bulk_output_file: Path
        surface_input_file: Path
        surface_template_file: Path

        def __init__(self, info, d_timer):
            self.mpicomm = mpi.comm()
            self.mpisize = mpi.size()
            self.mpirank = mpi.rank()
       
            if d_timer is None:
                self.log_mode = False
            else:
                self.log_mode = True
                self.detail_timer = d_timer

            self.root_dir = info.base["root_dir"]
            self.output_dir = info.base["output_dir"]

            if "dimension" in info.solver:
                self.dimension = info.solver["dimension"]
            else:
                self.dimension = info.base["dimension"]

            info_s = info.solver
            self.run_scheme = info_s["run_scheme"]
            self.generate_rocking_curve = info_s.get("generate_rocking_curve", False)
            
            # NOTE:
            # surf_tempalte_width_for_fortran: Number of strings per line of template.txt data for surf.so.
            # bulk_out_width_for_fortran: Number of strings per line of bulkP.txt data for surf.so.
            if self.run_scheme=="connect_so":
                self.surf_tempalte_width_for_fortran = 128
                self.bulk_out_width_for_fortran = 1024
            
            info_param = info_s.get("param", {})
            v = info_param.setdefault("string_list", ["value_01", "value_02"])
            if len(v) != self.dimension:
                raise exception.InputError(
                    f"ERROR: len(string_list) != dimension ({len(v)} != {self.dimension})"
                )
            self.string_list = v

            info_config = info_s.get("config", {})
            self.surface_input_file = Path(
                info_config.get("surface_input_file", "surf.txt")
            )

            filename = info_config.get("surface_template_file", "template.txt")
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
            self.template_file_origin = self.mpicomm.bcast(temp_origin,root=0) 

            if self.run_scheme == "connect_so": 
                filename = info_config.get("bulk_output_file", "bulkP.txt")
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
                self.bulk_file = self.mpicomm.bcast(bulk_f,root=0)

            else:
                filename = info_config.get("bulk_output_file", "bulkP.b")
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

        def load_bulk_output_file(self, filename) :
            bulk_file = []
            with open(self.bulk_output_file) as f:
                for line in f:
                    line = line.replace("\t", " ").replace("\n", " ")
                    line = line.encode().ljust(self.bulk_out_width_for_fortran)
                    bulk_file.append(line)
            bulk_f = np.array(bulk_file)
            return bulk_f

        def prepare(self, message: py2dmat.Message):
            if self.log_mode : time_sta = time.perf_counter() 
            
            x_list = message.x
            step = message.step
            iset = message.set
            
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
            
            if self.log_mode :
                time_end = time.perf_counter() 
                self.detail_timer["make_surf_input"] += time_end - time_sta
            
            if self.log_mode : time_sta = time.perf_counter() 
            
            if self.generate_rocking_curve:
                folder_name = self._pre_bulk(step, bulk_output_file, iset)
            else:
                if self.run_scheme == "connect_so":
                    folder_name = "."
                        
                elif self.run_scheme == "subprocess":
                    #make workdir and copy bulk output file
                    folder_name = self._pre_bulk(step, bulk_output_file, iset)
            
            if self.log_mode :
                time_end = time.perf_counter() 
                self.detail_timer["prepare_Log-directory"] += time_end - time_sta

            if self.log_mode : time_sta = time.perf_counter() 
            
            self._replace(fitted_x_list, folder_name)
            
            if self.log_mode :
                time_end = time.perf_counter() 
                self.detail_timer["make_surf_input"] += time_end - time_sta

            return fitted_x_list, folder_name

        def _pre_bulk(self, Log_number, bulk_output_file, iset):
            folder_name = "Log{:08d}_{:08d}".format(Log_number, iset)
            os.makedirs(folder_name, exist_ok=True)
            if self.run_scheme == "connect_so":
                pass
            else: #self.run_scheme == "subprocess":
                shutil.copy(
                    bulk_output_file, os.path.join(folder_name, bulk_output_file.name)
                )
            return folder_name

        def _replace(self, fitted_x_list, folder_name):
            template_file = []
            if self.run_scheme == "subprocess":
                file_output = open(os.path.join(folder_name, self.surface_input_file), "w") 
            for line in self.template_file_origin:
                for index in range(self.dimension):
                    if line.find(self.string_list[index]) != -1:
                        line = line.replace(
                                self.string_list[index],
                                fitted_x_list[index]
                            )

                if self.run_scheme == "connect_so":
                    line = line.replace("\t", " ").replace("\n", " ")
                    line = line.encode().ljust(self.surf_tempalte_width_for_fortran)
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

    class Output(object):
        """
        Output manager.
        """

        dimension: int
        string_list: List[str]
        surface_output_file: str
        normalization: str
        Rfactor_type: str
        calculated_first_line: int
        calculated_last_line: int
        row_number: int
        degree_max: float
        degree_list: List[float]

        reference: List[float]
        reference_norm: float
        reference_normalized: List[float]
        degree_list: List[float]

        def __init__(self, info, d_timer):
            self.mpicomm = mpi.comm()
            self.mpisize = mpi.size()
            self.mpirank = mpi.rank()

            if d_timer is None:
                self.log_mode = False
            else:
                self.log_mode = True
                self.detail_timer = d_timer

            if "dimension" in info.solver:
                self.dimension = info.solver["dimension"]
            else:
                self.dimension = info.base["dimension"]

            info_s = info.solver
            self.run_scheme = info_s["run_scheme"]
            self.generate_rocking_curve = info_s.get("generate_rocking_curve", False)

            # solver.config
            info_config = info_s.get("config", {})
            self.surface_output_file = info_config.get(
                "surface_output_file", "surf-bulkP.s"
            )

            v = info_config.get("calculated_first_line", 5)
            if not (isinstance(v, int) and v >= 0):
                raise exception.InputError(
                    "ERROR: calculated_first_line should be non-negative integer"
                )
            self.calculated_first_line = v

            v = info_config.get("calculated_last_line", 60)
            if not (isinstance(v, int) and v >= 0):
                raise exception.InputError(
                    "ERROR: calculated_last_line should be non-negative integer"
                )
            self.calculated_last_line = v

            v = info_config.get("row_number", 8)
            if not (isinstance(v, int) and v >= 0):
                raise exception.InputError(
                    "ERROR: row_number should be non-negative integer"
                )
            self.row_number = v

            v = info_config.get("cal_number",None)
            
            if v == None :
                raise exception.InputError(
                        "ERROR: You have to set the 'cal_number'."
                )
            
            if not isinstance(v, list):
                raise exception.InputError(
                    "ERROR: 'cal_number' must be a list type."
                )
            
            self.cal_number = v

            # solver.post
            info_post = info_s.get("post", {})
            v = info_post.get("normalization", "TOTAL")
            if v not in ["TOTAL", "MAX", "MS_NORM", "MS_NORM_SET_WGT"]:
                raise exception.InputError("ERROR: normalization must be MS_NORM, TOTAL or MAX")
            self.normalization = v

            v = info_post.get("Rfactor_type", "A")
            if v not in ["A", "B", "A2"]:
                raise exception.InputError("ERROR: Rfactor_type must be A, A2 or B")
            if self.normalization=="MS_NORM_SET_WGT":
                if (v!="A") and (v!="A2") :
                    raise exception.InputError(
                            'ERROR: When normalization="MS_NORM_SET_WGT" is set, only Rfactor_type="A" or Rfactor_type="A2" is valid.'
                            )
            self.Rfactor_type = v

            v = info_post.get("omega", 0.5)
            if v <= 0.0:
                raise exception.InputError("ERROR: omega should be positive")
            self.omega = v
            
            self.remove_work_dir = info_post.get("remove_work_dir", False)
            
            if self.normalization=="MS_NORM_SET_WGT":
                v = info_post.get("spot_weight", None)
                if v is None:
                    raise exception.InputError('ERROR:If normalization="MS_NORM_SET_WGT", the weight must be set in solver.post.')
                if len(v) != len(self.cal_number):
                    raise exception.InputError(
                        "len('cal_number') and len('spot_weight') do not match."
                    )
                
                self.spot_weight = np.array(v)/sum(v)
            
            # solver.param
            info_param = info_s.get("param", {})
            v = info_param.setdefault("string_list", ["value_01", "value_02"])
            if len(v) != self.dimension:
                raise exception.InputError(
                    f"ERROR: len(string_list) != dimension ({len(v)} != {self.dimension})"
                )
            self.string_list = v

            v = info_param.get("degree_max", 6.0)
            self.degree_max = v
            
            # solver.reference
            info_ref = info_s.get("reference", {})
            v = info_ref.setdefault("reference_first_line", 1)
            if not (isinstance(v, int) and v >= 0):
                raise exception.InputError(
                    "ERROR: reference_first_line should be non-negative integer"
                )
            firstline = v

            # None is dummy value
            # If "reference_last_line" is not specified in the toml file, 
            # the last line of the reference file is used for the R-factor calculation.
            v = info_ref.setdefault("reference_last_line", None)
            if v is None:
                reference_are_read_to_final_line = True
            else:
                reference_are_read_to_final_line = False
                if not (isinstance(v, int) and v >= firstline):
                    raise exception.InputError(
                        "ERROR: reference_last_line < reference_first_line"
                    )
            lastline = v

            reference_path = info_ref.get("path", "experiment.txt")
            data_experiment = self.read_experiment(
                    reference_path, firstline, lastline,
                    reference_are_read_to_final_line              )
            self.angle_number_experiment = data_experiment.shape[0]
            self.beam_number_exp_raw = data_experiment.shape[1]
            
            v = info_ref.get("exp_number", None)
            
            if v == None :
                raise exception.InputError(
                    "ERROR: You have to set the 'exp_number'."
                )

            if not isinstance(v, list):
                raise exception.InputError(
                    "ERROR: 'exp_number' must be a list type."
                )

            if max(v) > self.beam_number_exp_raw :
                raise exception.InputError(
                    "ERROR: The 'exp_number' setting is wrong."
                )

            if self.normalization=="MS_NORM_SET_WGT":
                if len(v) != len(self.spot_weight):
                    raise exception.InputError(
                        "len('exp_number') and len('spot_weight') do not match."
                    )

            self.exp_number = v
            self.beam_number_experiment = len(self.exp_number)
            number_ex = self.exp_number
            
            sum_experiment = 0
            for i in number_ex:
                sum_experiment += sum(data_experiment[::,i])
            
            self.degree_list = (data_experiment[::,0])
            self.all_reference_normalized = []
            for index, j in enumerate(number_ex):
                self.reference = (data_experiment[::,j])
                
                self.reference_norm = 0.0
                if self.normalization == "TOTAL":
                    self.reference_norm = sum_experiment
                    self.reference_normalized = [
                        I_exp / self.reference_norm for I_exp in self.reference
                    ]
                    for p in self.reference_normalized:
                        self.all_reference_normalized.append(p)

                elif self.normalization == "MS_NORM":
                    if j == number_ex[0]: #first loop
                        self.reference_norm_1st = np.array([np.sum(self.reference)])
                        self.reference_1st_normed = np.array([self.reference/self.reference_norm_1st[-1]])
                    else : # N-th loop
                        self.reference_norm_1st = np.block([self.reference_norm_1st, np.sum(self.reference)])
                        self.reference_1st_normed = np.block([[self.reference_1st_normed],[self.reference/self.reference_norm_1st[-1]]])
                
                elif self.normalization == "MS_NORM_SET_WGT":
                    if index == 0: #first loop
                        self.reference_norm_l = np.array(
                            [np.sum(self.reference)]
                            )
                        self.reference_normed_not_sptwgt = np.array(
                            [self.reference/self.reference_norm_l[-1]]
                            ) 
                        self.reference_normed = self._multiply_spot_weight(
                            self.reference_normed_not_sptwgt,    
                            self.spot_weight[index])
                    else : # N-th loop
                        self.reference_norm_l = np.block(
                            [self.reference_norm_l,
                            np.sum(self.reference)]
                            )
                        self.reference_normed_not_sptwgt = np.block(
                            [[self.reference_normed_not_sptwgt],
                             [self.reference/self.reference_norm_l[-1]]]
                            )
                        self.reference_normed = np.block(
                            [[self.reference_normed],
                             [self._multiply_spot_weight(
                                self.reference_normed_not_sptwgt[-1,:],
                                self.spot_weight[index]) ] ]
                            )
                    self.all_reference_normalized.extend(
                            self.reference_normed[-1,:].tolist()
                        )

                else:  # self.normalization == "MAX":
                    self.reference_norm = max(self.reference) 
                    self.reference_normalized = [
                        I_exp / self.reference_norm for I_exp in self.reference
                    ]
                    for p in self.reference_normalized:
                        self.all_reference_normalized.append(p)

        def read_experiment(self, ref_path, first, last, read_to_final_line):
            # Read experiment data
            if self.mpirank == 0:
                file_input = open(ref_path, "r")
                Elines = file_input.readlines()

                firstline = first
                if read_to_final_line :
                    lastline = len(Elines)
                else:
                    lastline = last
                
                n_exp_row = lastline-firstline+1
                
                # get value from data
                for row_index in range(n_exp_row) :
                    line_index = firstline + row_index - 1
                    line = Elines[line_index]
                    data = line.split()
                    # first loop
                    if row_index == 0:
                        n_exp_column = len(data)
                        data_e = np.zeros((n_exp_row, n_exp_column)) #init value
                    
                    for column_index in range(n_exp_column):
                        data_e[row_index, column_index] = float(data[column_index])
            else:
                data_e = None
            data_exp = self.mpicomm.bcast(data_e,root=0)
            return data_exp

        def prepare(self, fitted_x_list):
            self.fitted_x_list = fitted_x_list

        def get_results(self, work_dir) -> float:
            """
            Get Rfactor obtained by the solver program.
            Returns
            -------
            """            
            # Calculate Rfactor and Output numerical results
            cwd = os.getcwd()
            os.chdir(work_dir)
            Rfactor = self._post(self.fitted_x_list)
            os.chdir(cwd)

            #delete Log-directory
            if self.log_mode : time_sta = time.perf_counter()
            
            if self.run_scheme == "subprocess":
                if self.remove_work_dir:
                    def rmtree_error_handler(function, path, excinfo):
                        print(f"WARNING: Failed to remove a working directory, {path}")
                    shutil.rmtree(work_dir, onerror=rmtree_error_handler)
            
            if self.log_mode :
                time_end = time.perf_counter()
                self.detail_timer["delete_Log-directory"] += time_end - time_sta
            
            return Rfactor

        def _post(self, fitted_x_list):
            degree_list = self.degree_list
            I_experiment_norm = self.reference_norm
            I_experiment_list = self.reference

            (
                all_convolution_I_calculated_list_normalized,
                I_calculated_norm,
                convolution_I_calculated_list,
            ) = self._calc_I_from_file()
            
            if self.log_mode : time_sta = time.perf_counter()
            
            Rfactor = self._calc_Rfactor(all_convolution_I_calculated_list_normalized)
            if self.log_mode :
                time_end = time.perf_counter()
                self.detail_timer["calculate_R-factor"] += time_end - time_sta

            dimension = self.dimension
            string_list = self.string_list
            
            if self.generate_rocking_curve :
                if self.normalization == "MS_NORM":
                    print('NOTICE: The output of rocking curve is not implemented when the following settings are made: self.normalization == "MS_NORM".')
                else:
                    if self.log_mode : time_sta = time.perf_counter()
                    with open("RockingCurve_calculated.txt", "w") as file_RC:
                        # Write headers
                        file_RC.write("#")
                        for index in range(dimension):
                            file_RC.write(
                                "{} = {} ".format(string_list[index], fitted_x_list[index])
                            )
                        file_RC.write("\n")
                        file_RC.write(f"#Rfactor_type = {self.Rfactor_type}")
                        file_RC.write("\n")
                        file_RC.write(f"#normalization = {self.normalization}")
                        file_RC.write("\n")
                        file_RC.write("#R-factor = {}\n".format(Rfactor))
                        file_RC.write("#cal_number = {}\n".format(self.cal_number))
                        if self.normalization == "MS_NORM_SET_WGT" :
                            file_RC.write("#spot_weight = {}\n".format(self.spot_weight))
                            file_RC.write("#NOTICE : The listed intensities are NOT multiplied by spot_weight.")
                            file_RC.write("\n")
                        file_RC.write("#The intensity I_(spot) for each spot is normalized as in the following equation.")
                        file_RC.write("\n")
                        file_RC.write("#sum( I_(spot) ) = 1")
                        file_RC.write("\n")
                        file_RC.write("#")
                        file_RC.write("\n")
                        
                        label_column = ["glancing_angle"]
                        fmt_rc = '%.5f'
                        for i in range(len(self.cal_number)):
                            label_column.append(f"cal_number={self.cal_number[i]}")
                            fmt_rc += " %.15e"

                        for i in range(len(label_column)):
                            file_RC.write(f"# #{i} {label_column[i]}")
                            file_RC.write("\n")

                        angle_for_rc = np.array([self.glancing_angle]) 
                        np.savetxt(
                                file_RC,
                                np.block(
                                    [angle_for_rc.T, 
                                     self.calc_rocking_curve.T]  
                                    ),
                                fmt=fmt_rc
                                )
                    
                if self.log_mode :
                    time_end = time.perf_counter()
                    self.detail_timer["make_RockingCurve.txt"] += time_end - time_sta
    
            return Rfactor

        def _g(self, x):
            g = (0.939437 / self.omega) * np.exp(
                -2.77259 * (x ** 2.0 / self.omega ** 2.0)
            )
            return g

        def _calc_I_from_file(self):
            if self.log_mode : time_sta = time.perf_counter()
            
            surface_output_file = self.surface_output_file
            calculated_first_line = self.calculated_first_line
            calculated_last_line = self.calculated_last_line
            row_number = self.row_number
            degree_max = self.degree_max
            degree_list = self.degree_list

            nlines = calculated_last_line - calculated_first_line + 1
            assert 0 < nlines

            if self.run_scheme == "connect_so":
                Clines = self.surf_output
            
            elif self.run_scheme == "subprocess":
                file_input = open(self.surface_output_file, "r")
                Clines = file_input.readlines()
                file_input.close()
            
            # Extract STR results (glancing angle and intensity) from Clines.
            # Read the file header
            line = Clines[0]
           
            if line ==  ' FILE OUTPUT for UNIT3\n':
                alpha_lines = 1
            else:
                alpha_lines = 0
            
            number_of_lines        = int(len(Clines))
            number_of_header_lines = 4 + alpha_lines
            
            line = Clines[1 + alpha_lines]
            line = line.replace(",", "")
            data = line.split()
            
            number_of_azimuth_angles  = int(data[0])
            number_of_glancing_angles = int(data[1])
            number_of_beams           = int(data[2])

            # Define the array for the rocking curve data.
            # Note the components with (beam-index)=0 are the degree data
            RC_data_org = np.zeros((number_of_glancing_angles, number_of_beams+1))

            for g_angle_index in range(number_of_glancing_angles):
                line_index = number_of_header_lines + g_angle_index
                line = Clines[ line_index ]
            #   print("data line: ", line_index, g_angle_index, line)
                line = line.replace(",", "")
                data = line.split()
            #   print(data)
                RC_data_org[g_angle_index,0]=float(data[0])
                for beam_index in range(number_of_beams):
                    RC_data_org[g_angle_index, beam_index+1] = data[beam_index+1]

            if self.log_mode :
                time_end = time.perf_counter()
                self.detail_timer["load_STR_result"] += time_end - time_sta
            
            if self.log_mode : time_sta = time.perf_counter() 
            verbose_mode = False
            data_convolution = lib_make_convolution.calc(
                    RC_data_org, number_of_beams, number_of_glancing_angles, self.omega, verbose_mode
                        ) 

            self.all_convolution_I_calculated_list_normalized = []
            if self.log_mode :
                time_end = time.perf_counter()
                self.detail_timer["convolution"] += time_end - time_sta

            if self.log_mode : time_sta = time.perf_counter() 
            number = self.cal_number
            angle_number_convolution = data_convolution.shape[0]
            self.glancing_angle = data_convolution[:,0]
            
            if self.angle_number_experiment !=angle_number_convolution:
                raise exception.InputError(
                    "ERROR: The number of glancing angles in the calculation data does not match the number of glancing angles in the experimental data."
                )
                
            self.beam_number_convolution = data_convolution.shape[1]
            sum_convolution = np.sum(data_convolution[:,number])

            for i in range(len(number)):
                convolution_I_calculated_list = data_convolution[:,number[i]]

                if self.normalization == "TOTAL":
                    I_calculated_norm = sum_convolution
                    convolution_I_calculated_list_normalized = [
                        c / I_calculated_norm for c in convolution_I_calculated_list
                    ]
                    self.calc_rocking_curve = np.array([copy.deepcopy(convolution_I_calculated_list_normalized)])
             
                elif self.normalization == "MS_NORM":
                    if i == 0: 
                        self.reference_2nd_normed = copy.deepcopy(self.reference_1st_normed)
                        self.all_reference_normalized = []
                    I_calculated_norm = sum_convolution
                    convolution_I_calculated_list_normalized = [
                        c / I_calculated_norm for c in convolution_I_calculated_list
                    ]
                    I_calc_norm_sum_spot = sum(convolution_I_calculated_list_normalized)
                    self.reference_2nd_normed[i,:] *= I_calc_norm_sum_spot 
                    self.all_reference_normalized.extend(self.reference_2nd_normed[i,:].tolist())

                elif self.normalization == "MS_NORM_SET_WGT":
                    if i == 0: #first loop
                        I_calculated_norm = np.array(
                            [np.sum(convolution_I_calculated_list)]
                            )
                        self.convolution_I_calculated_list_normalized_not_spotwgt_array = np.array(
                            [convolution_I_calculated_list/I_calculated_norm[-1]]
                            ) 
                        convolution_I_calculated_list_normalized_array = self._multiply_spot_weight(
                                self.convolution_I_calculated_list_normalized_not_spotwgt_array,
                                self.spot_weight[i])
                    else: # N-th loop
                        I_calculated_norm = np.block(
                            [I_calculated_norm,
                            np.sum(convolution_I_calculated_list)]
                            )
                        self.convolution_I_calculated_list_normalized_not_spotwgt_array = np.block(
                            [[self.convolution_I_calculated_list_normalized_not_spotwgt_array],
                             [convolution_I_calculated_list/I_calculated_norm[-1]]] 
                            )
                        convolution_I_calculated_list_normalized_array = np.block(
                            [[convolution_I_calculated_list_normalized_array],
                             [ self._multiply_spot_weight(
                                 self.convolution_I_calculated_list_normalized_not_spotwgt_array[-1,:],
                                 self.spot_weight[i]) ] ]
                            )
                    convolution_I_calculated_list_normalized = convolution_I_calculated_list_normalized_array[-1,:].copy()
                    self.calc_rocking_curve = np.copy(self.convolution_I_calculated_list_normalized_not_spotwgt_array) 
                
                else:  # self.normalization == "MAX"
                    print('self.normalization == "MAX" mb対応検討中')
                    I_calculated_norm = max(convolution_I_calculated_list)
                    convolution_I_calculated_list_normalized = [
                        c / I_calculated_norm for c in convolution_I_calculated_list
                    ]
                    self.calc_rocking_curve = np.array([copy.deepcopy(convolution_I_calculated_list_normalized)])
                
                for h in convolution_I_calculated_list_normalized:
                    self.all_convolution_I_calculated_list_normalized.append(h)
                
            if self.log_mode :
                time_end = time.perf_counter()
                self.detail_timer["normalize_calc_I"] += time_end - time_sta
            
            return (
                self.all_convolution_I_calculated_list_normalized,
                I_calculated_norm,
                convolution_I_calculated_list,
            )
        
        
        def _calc_Rfactor(self, calc_result):
            I_experiment_list_normalized = self.all_reference_normalized
            if self.Rfactor_type == "A":
                R = 0.0
                for I_exp, I_calc in zip(I_experiment_list_normalized, calc_result):
                    R += (I_exp - I_calc) ** 2
                R = np.sqrt(R)

            elif self.Rfactor_type == "A2":
                R = 0.0
                for I_exp, I_calc in zip(I_experiment_list_normalized, calc_result):
                    R += (I_exp - I_calc) ** 2
            
            else:  # self.Rfactor_type == "B"
                y1 = 0.0
                y2 = 0.0
                y3 = 0.0
                for I_exp, I_calc in zip(I_experiment_list_normalized, calc_result):
                    y1 += (I_exp - I_calc) ** 2
                    y2 += I_exp ** 2
                    y3 += I_calc ** 2
                R = y1 / (y2 + y3)
            return R
         
        def _multiply_spot_weight(self,I_not_multiplied_spotwgt,s_weight):
            if (self.Rfactor_type=="A") or (self.Rfactor_type=="A2") :
                I_multiplied = np.sqrt(s_weight)*I_not_multiplied_spotwgt
            
            else:
                raise exception.InputError(
                        'ERROR: When normalization="MS_NORM_SET_WGT" is set, only Rfactor_type="A" or Rfactor_type="A2" is valid.'
                        )
            return I_multiplied
