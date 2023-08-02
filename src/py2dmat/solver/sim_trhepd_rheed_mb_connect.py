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

import sys
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
        self.input = Solver.Input(info)
        self.output = Solver.Output(info)
        
        self.input.run_scheme = self.run_scheme
        self.output.run_scheme = self.run_scheme

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

        self.generate_rocking_curve = info.solver.get("generate_rocking_curve", False)
        #print(f" info.solver = {info.solver}")
        self.input.generate_rocking_curve = self.generate_rocking_curve
        self.output.generate_rocking_curve = self.generate_rocking_curve

        #add
        if True:
            self.detail_timer = {}
            self.detail_timer["prepare_Log-directory"] = 0
            self.detail_timer["make_surf_input"] = 0
            self.detail_timer["launch_STR"] = 0
            self.detail_timer["load_STR_result"] = 0
            self.detail_timer["convolution"] = 0
            self.detail_timer["calculate_R-factor"] = 0
            self.detail_timer["make_RockingCurve.txt"] = 0
            self.detail_timer["delete_Log-directory"] = 0
            self.input.detail_timer = self.detail_timer
            self.output.detail_timer = self.detail_timer

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
       
        #debug
        #print(os.getcwd())
        ###### debug ############
        '''
        #make surf.txt
        for line in self.input.template_file:
            #f = open('surf.txt','w')
            l = line.decode().rstrip()
            print(l)
            #f.write(l)
            #f.write('\n')
        
        #f.close()
        #sys.exit()
        '''
        #########################

        #fn = ctypes.byref(ctypes.c_int(n))
        #fm = ctypes.byref(ctypes.c_int(m))
        #print(self.input.template_file)
        #sys.exit()
        n_template_file = len(self.input.template_file)
        m_template_file = self.input.surf_tempalte_width_for_fortran
        n_bulk_file = len(self.input.bulk_file)
        m_bulk_file = self.input.bulk_out_width_for_fortran
        
        emp_str = ' '*20480
        self.output.surf_output = np.array([emp_str.encode()])
        #for i in range(n_bulk_file):
        #    print(len(self.input.bulk_file[i]))
       
        #import sys
        #sys.exit()
        #print(self.input.template_file)
        #print(self.input.bulk_file)
        #print('launch so')
        self.lib.surf_so(
                ctypes.byref(ctypes.c_int(n_template_file)),
                ctypes.byref(ctypes.c_int(m_template_file)),
                self.input.template_file,
                ctypes.byref(ctypes.c_int(n_bulk_file)),
                ctypes.byref(ctypes.c_int(m_bulk_file)),
                self.input.bulk_file,
                self.output.surf_output
                )
        #print('finish so')
        self.output.surf_output = self.output.surf_output[0].decode().splitlines()
        '''
        print('----------in python----------')
        f = open('surf-bulkP.s','w')
        for i in range(len(self.output.surf_output)):
            f.write(self.output.surf_output[i]i.rstrip())
            f.write('\n')
        
        f.close()
        import sys
        sys.exit()
        '''
    def run(self, nprocs: int = 1, nthreads: int = 1) -> None:
        if self.run_scheme == "connect_so":
            self.launch_so()
        elif self.run_scheme == "subprocess":
            self._run_by_subprocess([str(self.path_to_solver)])
             

    class Input(object):
        root_dir: Path
        output_dir: Path
        dimension: int
        string_list: List[str]
        bulk_output_file: Path
        surface_input_file: Path
        surface_template_file: Path

        def __init__(self, info):
            self.mpicomm = mpi.comm()
            self.mpisize = mpi.size()
            self.mpirank = mpi.rank()
            
            self.root_dir = info.base["root_dir"]
            self.output_dir = info.base["output_dir"]

            if "dimension" in info.solver:
                self.dimension = info.solver["dimension"]
            else:
                self.dimension = info.base["dimension"]

            info_s = info.solver
            self.run_scheme = info_s["run_scheme"]
            #
            self.surf_tempalte_width_for_fortran = 128
            self.bulk_out_width_for_fortran = 1024
            #

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

            self._check_template()
            
            #if False:
            if True:
                if self.mpirank == 0:
                    temp_origin = self.load_surface_template_file(filename)   
                else:
                    temp_origin = None
                self.template_file_origin = self.mpicomm.bcast(temp_origin,root=0) 
                #if self.mpirank == 0:
                #    print(temp_origin,"\n")
                #    print(self.template_file_origin)
                #    print(len(temp_origin)==len(self.template_file_origin))
                #    print("for i in range(len(temp_origin))")
                #    for i in range(len(temp_origin)):
                #        print(temp_origin[i]==self.template_file_origin[i])
                #    print("end")
                #    print(temp_origin==self.template_file_origin)        
            else :
                self.template_file_origin = self.load_surface_template_file(filename)

            if self.run_scheme == "connect_so": 
                filename = info_config.get("bulk_output_file", "bulkP.txt")
                filename = Path(filename).expanduser().resolve()
                self.bulk_output_file = self.root_dir / filename
                if not self.bulk_output_file.exists():
                    raise exception.InputError(
                        f"ERROR: bulk_output_file ({self.bulk_output_file}) does not exist"
                    )
                
                #if False:
                if True:
                    if self.mpirank == 0:
                        bulk_f = self.load_bulk_output_file(filename)
                        #print(bulk_f)
                        #print(bulk_f.dtype)
                        #print(bulk_f.shape)
                    else:
                        bulk_f = None
                    self.bulk_file = self.mpicomm.bcast(bulk_f,root=0)
                    #print(self.bulk_file)
                    #print(self.bulk_file.dtype)
                    #print(self.bulk_file.shape)
                    #if self.mpirank == 0:
                    #    print(len(bulk_f)==len(self.bulk_file))
                    #    print("for i in range(len(bulk_f))")
                    #    for i in range(len(bulk_f)):
                    #        print(bulk_f[i]==self.bulk_file[i])
                    #    print("end")
                    #    print(bulk_f==self.bulk_file)        
                else:
                    self.bulk_file = self.load_bulk_output_file(filename)

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
            #print(f'load {filename}')
            return template_file

        def load_bulk_output_file(self, filename) :
            bulk_file = []
            #a = []
            with open(self.bulk_output_file) as f:
                for line in f:
                    line = line.replace("\t", " ").replace("\n", " ")
                    line = line.encode().ljust(self.bulk_out_width_for_fortran)
                    #a.append(len(line))
                    bulk_file.append(line)
            bulk_f = np.array(bulk_file)
            #self.bulk_file = np.array(bulk_file)
            #print(f'load {filename}')
            return bulk_f

        def prepare(self, message: py2dmat.Message):
            if self.detail_timer is not None : time_sta = time.perf_counter() 
            #
            x_list = message.x
            step = message.step
            #extra = False
            extra = message.set > 0
            
            #### ADHOC_MPPING! ###"
            adhoc_mapping = False
            if adhoc_mapping:
                if self.mpirank==0 and step==1:
                    print(f"NOTICE: adhoc_mapping is {adhoc_mapping}")
                A_array = np.array(
                        [[1,2],
                         [3,4]]
                        )
                B_array = np.array([10,11])
                x_list = np.dot(A_array,x_list) + B_array

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
            #for index in range(dimension):
            #    print(string_list[index], "=", fitted_x_list[index])
            #
            if self.detail_timer is not None :
                time_end = time.perf_counter() 
                self.detail_timer["make_surf_input"] += time_end - time_sta
            
            
            if self.detail_timer is not None : time_sta = time.perf_counter() 
            #
            if self.generate_rocking_curve:
                folder_name = self._pre_bulk(step, bulk_output_file, extra)
            else:
                if self.run_scheme == "connect_so":
                    folder_name = "."
                        
                elif self.run_scheme == "subprocess":
                    #make workdir and copy bulk output file
                    folder_name = self._pre_bulk(step, bulk_output_file, extra)
            #
            if self.detail_timer is not None :
                time_end = time.perf_counter() 
                self.detail_timer["prepare_Log-directory"] += time_end - time_sta

            if self.detail_timer is not None : time_sta = time.perf_counter() 
            #
            self._replace(fitted_x_list, folder_name)
            #
            if self.detail_timer is not None :
                time_end = time.perf_counter() 
                self.detail_timer["make_surf_input"] += time_end - time_sta

            return fitted_x_list, folder_name

        def _pre_bulk(self, Log_number, bulk_output_file, extra):
            if extra:
                folder_name = "Extra_Log{:08d}".format(Log_number)
            else:
                folder_name = "Log{:08d}".format(Log_number)
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
                    #print(line)
                
                elif self.run_scheme == "subprocess":
                    file_output.write(line)

            
            if self.run_scheme == "connect_so":
                self.template_file = np.array(template_file)
            elif self.run_scheme == "subprocess":
                file_output.close()
            
            '''
            with open(self.surface_template_file, "r") as file_input, open(
                os.path.join(folder_name, self.surface_input_file), "w"
            ) as file_output:
                for line in file_input:
                    for index in range(self.dimension):
                        if line.find(self.string_list[index]) != -1:
                            line = line.replace(
                                self.string_list[index],
                                fitted_x_list[index],
                            )
                    file_output.write(line)
            '''

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

        def __init__(self, info):
            self.mpicomm = mpi.comm()
            self.mpisize = mpi.size()
            self.mpirank = mpi.rank()

            if "dimension" in info.solver:
                self.dimension = info.solver["dimension"]
            else:
                self.dimension = info.base["dimension"]

            info_s = info.solver
            self.run_scheme = info_s["run_scheme"]

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
            #print(v,type(v))
            #sys.exit()
            
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
                #debug
                #print(f"spot_weight(non_norm) = {v}")
                #print(f"self.spot_weight = {self.spot_weight}")
            

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
            reference_path = info_ref.get("path", "experiment.txt")

            v = info_ref.setdefault("first", 1)
            if not (isinstance(v, int) and v >= 0):
                raise exception.InputError(
                    "ERROR: reference_first_line should be non-negative integer"
                )
            firstline = v

            v = info_ref.setdefault("last", 56)
            if not (isinstance(v, int) and v >= firstline):
                raise exception.InputError(
                    "ERROR: reference_last_line < reference_first_line"
                )
            lastline = v


            # Read experiment-data
            
            #debug
            #print(os.getcwd())
            #if False:
            if True:
                if self.mpirank == 0:
                    data_e = np.loadtxt(reference_path)
                else:
                    data_e = None
                data_experiment = self.mpicomm.bcast(data_e,root=0)
               #print(data_experiment)
               #print(data_experiment.dtype)
               #print(data_experiment.shape)
               #if self.mpirank == 0:
               #    print(len(data_e)==len(data_experiment))
               #    print("for i in range(len(data_e))")
               #    for i in range(len(data_e)):
               #        print(data_e[i]==data_experiment[i])
               #    print("end")
               #    print(data_e==data_experiment)        
            else:
                data_experiment = np.loadtxt(reference_path)
            
            self.beam_number_experiment = data_experiment.shape[1]
            self.angle_number_experiment = data_experiment.shape[0]

            v = info_ref.get("exp_number", None)
            #print(v,type(v))
            #sys.exit()
            if v == None :
                raise exception.InputError(
                    "ERROR: You have to set the 'exp_number'."
                )

            if not isinstance(v, list):
                raise exception.InputError(
                    "ERROR: 'exp_number' must be a list type."
                )

            if max(v) > self.beam_number_experiment:
                raise exception.InputError(
                    "ERROR: The 'exp_number' setting is wrong."
                )

            if self.normalization=="MS_NORM_SET_WGT":
                if len(v) != len(self.spot_weight):
                    raise exception.InputError(
                        "len('exp_number') and len('spot_weight') do not match."
                    )

            self.exp_number = v
            number_ex = self.exp_number
            sum_experiment = 0
            #for i in range(1,self.beam_number_experiment):
            for i in number_ex:
                sum_experiment += sum(data_experiment[::,i])
            
            #debug
            #print(f'number_ex = {number_ex}')

            self.degree_list = (data_experiment[::,0])
            #debug
            #print("data_experiment=\n",data_experiment) 
            self.all_reference_normalized = []
            for index, j in enumerate(number_ex):
                self.reference = (data_experiment[::,j])
                #debug
                #print(f'index,j={index},{j}\nself.reference=\n{self.reference}')
                
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
                    #debug
                    #print(f"j={j}")
                    #print(f"self.reference_1st_normed=\n{self.reference_1st_normed}")
                    #print(f"self.reference_norm_1st={self.reference_norm_1st}")
                
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
                    #debug
                    #print(f"j={j},index={index}")
                    #print(f"self.reference_norm_l={self.reference_norm_l}")
                    #print(f"self.reference_normed_not_sptwgt=\n{self.reference_normed_not_sptwgt}")
                    #print(f"self.reference_normed=\n{self.reference_normed}")
                    #print(f"self.all_reference_normalized=\n{self.all_reference_normalized}")

                else:  # self.normalization == "MAX":
                    self.reference_norm = max(self.reference) 
                    self.reference_normalized = [
                        I_exp / self.reference_norm for I_exp in self.reference
                    ]
                    for p in self.reference_normalized:
                        self.all_reference_normalized.append(p)
            
            #debug
            #print('self.all_reference_normalized=')
            #print(self.all_reference_normalized)
            #print(f"self.reference_norm_1st=\n{self.reference_norm_1st}") 
            #print(f"self.reference_1st_normed=\n{self.reference_1st_normed}") 
           
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
            if self.detail_timer is not None : time_sta = time.perf_counter()
            #
            if self.run_scheme == "subprocess":
                if self.remove_work_dir:
                    def rmtree_error_handler(function, path, excinfo):
                        print(f"WARNING: Failed to remove a working directory, {path}")
                    shutil.rmtree(work_dir, onerror=rmtree_error_handler)
        
            elif self.run_scheme == "connect_so":
                pass
            #
            if self.detail_timer is not None :
                time_end = time.perf_counter()
                self.detail_timer["delete_Log-directory"] += time_end - time_sta
            ##
            
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
            
            ###
            if self.detail_timer is not None : time_sta = time.perf_counter()
            Rfactor = self._calc_Rfactor(all_convolution_I_calculated_list_normalized)
            #print("R-factor =", Rfactor)
            if self.detail_timer is not None :
                time_end = time.perf_counter()
                self.detail_timer["calculate_R-factor"] += time_end - time_sta
            ###

            dimension = self.dimension
            string_list = self.string_list
            
            if self.generate_rocking_curve :
                if self.detail_timer is not None : time_sta = time.perf_counter()
                with open("RockingCurve.txt", "w") as file_RC:
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
                    file_RC.write("#spot_weight = {}\n".format(self.spot_weight))
                    
                    file_RC.write("#")
                    file_RC.write("\n")
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
                                 self.convolution_I_calculated_list_normalized_not_spotwgt_array.T] 
                                ),
                            fmt=fmt_rc
                            )
                    

                
                if self.detail_timer is not None :
                    time_end = time.perf_counter()
                    self.detail_timer["make_RockingCurve.txt"] += time_end - time_sta
    
            """
            with open("RockingCurve.txt", "w") as file_RC:
                I_experiment_list_normalized = self.reference_normalized
                # Write headers
                file_RC.write("#")
                for index in range(dimension):
                    file_RC.write(
                        "{} = {} ".format(string_list[index], fitted_x_list[index])
                    )
                file_RC.write("\n")
                file_RC.write("#R-factor = {}\n".format(Rfactor))
                if self.normalization == "TOTAL":
                    file_RC.write("#I_calculated_total={}\n".format(I_calculated_norm))
                    file_RC.write("#I_experiment_total={}\n".format(I_experiment_norm))
                else:  # self.normalization == "MAX"
                    file_RC.write("#I_calculated_max={}\n".format(I_calculated_norm))
                    file_RC.write("#I_experiment_max={}\n".format(I_experiment_norm))
                file_RC.write("#")
                for xname in (
                    "degree",
                    "convolution_I_calculated",
                    "I_experiment",
                    "convolution_I_calculated(normalized)",
                    "I_experiment(normalized)",
                    "I_calculated",
                ):
                    file_RC.write(xname)
                    file_RC.write(" ")
                file_RC.write("\n")

                # Write rocking curve
                for index in range(len(degree_list)):
                    file_RC.write(
                        "{} {} {} {} {}\n".format(
                            degree_list[index],
                            convolution_I_calculated_list[index],
                            I_experiment_list[index],
                            all_convolution_I_calculated_list_normalized[index],
                            I_experiment_list_normalized[index],
                        )
                    )
            """
            return Rfactor

        def _g(self, x):
            g = (0.939437 / self.omega) * np.exp(
                -2.77259 * (x ** 2.0 / self.omega ** 2.0)
            )
            return g

        def _calc_I_from_file(self):
            if self.detail_timer is not None : time_sta = time.perf_counter()
            #
            surface_output_file = self.surface_output_file
            calculated_first_line = self.calculated_first_line
            calculated_last_line = self.calculated_last_line
            row_number = self.row_number
            degree_max = self.degree_max
            degree_list = self.degree_list

            nlines = calculated_last_line - calculated_first_line + 1
            # TODO: handling error
            assert 0 < nlines

            # TODO: nlines == len(degree_list) ?
            # assert nlines == len(degree_list)
            if self.run_scheme == "connect_so":
                Clines = self.surf_output
            
            elif self.run_scheme == "subprocess":
                file_input = open(self.surface_output_file, "r")
                Clines = file_input.readlines()
                file_input.close()
            #
            if self.detail_timer is not None :
                time_end = time.perf_counter()
                self.detail_timer["load_STR_result"] += time_end - time_sta
            

            ##### convolution #####
            
            """
            beam = [0,0,0.5,0,1.0,0,1.5,0,2.0,0]
            bulk_data = np.loadtxt("/Users/ichinosehayato/mv_2DMAT/2DMAT_MB_ICHINOSE/sample/py2dmat/minsearch/bulk.txt")
            denominator_H = float(bulk_data[0,0])
            denominator_K = float(bulk_data[0,1])
            for H in beam[0::2]:
                beamnum_H = H*denominator_H
                beamnum.append(beamnum_H)
                for K in beam[1::2]:
                    beamnum_K = K*denominator_K
                    beamnum.append(beamnum_K)
                    break
            print(beamnum)
            
            for n in beamnum[0::2]:
                number.append(n*2)
            print(number)
            """
            
            #print(os.getcwd())
            #############
            if self.detail_timer is not None : time_sta = time.perf_counter() 
            verbose_mode = False
            #print("debug: Clines:",Clines)
            data_convolution = lib_make_convolution.calc(
                    Clines, self.omega, verbose_mode
                        ) 
            #print("data_convolution=") 
            #print(data_convolution)

            self.all_convolution_I_calculated_list_normalized = []
            #print(f"data_convolution=\n{data_convolution}")
            
            #number = [7,8,9,10,11]
            number = self.cal_number
            angle_number_convolution = data_convolution.shape[0]
            self.glancing_angle = data_convolution[:,0]
            
            if self.angle_number_experiment !=angle_number_convolution:
                raise exception.InputError(
                    "ERROR: The number of glancing angles in the calculation data does not match the number of glancing angles in the experimental data."
                )
                
            self.beam_number_convolution = data_convolution.shape[1]
            #for s in range(1,self.beam_number_convolution):
            sum_convolution = np.sum(data_convolution[:,number])
            #debug
            #print(f'sum_convolution = {sum_convolution}')

            for i in range(len(number)):
                convolution_I_calculated_list = data_convolution[:,number[i]]
                #debug
                #print(f'convolution_I_calculated_list=\n{convolution_I_calculated_list}')

                if self.normalization == "TOTAL":
                    I_calculated_norm = sum_convolution
                    convolution_I_calculated_list_normalized = [
                        c / I_calculated_norm for c in convolution_I_calculated_list
                    ]
             
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
                    #debug
                    #print(f"i={i}, number[i]={number[i]}")
                    #print(f"convolution_I_calculated_list_normalized={convolution_I_calculated_list_normalized}")
                    #print(f"I_calc_norm_sum_spot={I_calc_norm_sum_spot}")
                    #print(f"self.reference_2nd_normed=\n{self.reference_2nd_normed}")
                    #print(f"self.all_reference_normalized={self.all_reference_normalized}")

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
                        #convolution_I_calculated_list_normalized = convolution_I_calculated_list_normalized_array[:].copy()
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
                    #debug
                    #print(f"i={i}, number[i]={number[i]}")
                    #print(f"I_calculated_norm={I_calculated_norm}")
                    #print(f"self.convolution_I_calculated_list_normalized_not_spotwgt_array=\n{self.convolution_I_calculated_list_normalized_not_spotwgt_array}")
                    #print(f"convolution_I_calculated_list_normalized_array=\n{convolution_I_calculated_list_normalized_array}")
                    #print(f"convolution_I_calculated_list_normalized=\n{convolution_I_calculated_list_normalized}")
                
                else:  # self.normalization == "MAX"
                    print('self.normalization == "MAX" mb対応検討中')
                    I_calculated_norm = max(convolution_I_calculated_list)
                    convolution_I_calculated_list_normalized = [
                        c / I_calculated_norm for c in convolution_I_calculated_list
                    ]
                for h in convolution_I_calculated_list_normalized:
                    self.all_convolution_I_calculated_list_normalized.append(h)
                
            if self.detail_timer is not None :
                time_end = time.perf_counter()
                self.detail_timer["convolution"] += time_end - time_sta
            
            #debug
            #print('self.all_convolution_I_calculated_list_normalized=')
            #print(self.all_convolution_I_calculated_list_normalized)
            
            #print("self.all_convolution_I_calculated_list_normalized=")
            #print(self.all_convolution_I_calculated_list_normalized)
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
                    #debug
                    #print(f"I_exp, I_calc, I_exp-I_calc = {I_exp}, {I_calc}, {I_exp-I_calc}")
                #print(f"R-factor = {R}")
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
