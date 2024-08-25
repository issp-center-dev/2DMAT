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

from typing import List
import time
import shutil
import copy

import physbo
import numpy as np

import py2dmat
import py2dmat.domain


class Algorithm(py2dmat.algorithm.AlgorithmBase):

    # inputs
    mesh_list: np.ndarray
    label_list: List[str]

    # hyperparameters of Bayesian optimization
    random_max_num_probes: int
    bayes_max_num_probes: int
    score: str
    interval: int
    num_rand_basis: int

    # results
    xopt: np.ndarray
    best_fx: List[float]
    best_action: List[int]
    fx_list: List[float]
    param_list: List[np.ndarray]

    def __init__(self, info: py2dmat.Info,
                 runner: py2dmat.Runner = None,
                 domain = None) -> None:
        super().__init__(info=info, runner=runner)

        info_param = info.algorithm.get("param", {})
        info_bayes = info.algorithm.get("bayes", {})

        for key in ("random_max_num_probes", "bayes_max_num_probes", "score", "interval", "num_rand_basis"):
            if key in info_param and key not in info_bayes:
                print(f"WARNING: algorithm.param.{key} is deprecated. Use algorithm.bayes.{key} .")
                info_bayes[key] = info_param[key]

        self.random_max_num_probes = info_bayes.get("random_max_num_probes", 20)
        self.bayes_max_num_probes = info_bayes.get("bayes_max_num_probes", 40)
        self.score = info_bayes.get("score", "TS")
        self.interval = info_bayes.get("interval", 5)
        self.num_rand_basis = info_bayes.get("num_rand_basis", 5000)

        print("# parameter")
        print(f"random_max_num_probes = {self.random_max_num_probes}")
        print(f"bayes_max_num_probes = {self.bayes_max_num_probes}")
        print(f"score = {self.score}")
        print(f"interval = {self.interval}")
        print(f"num_rand_basis = {self.num_rand_basis}")

        #self.mesh_list, actions = self._meshgrid(info, split=False)
        if domain and isinstance(domain, py2dmat.domain.MeshGrid):
            self.domain = domain
        else:
            self.domain = py2dmat.domain.MeshGrid(info)
        self.mesh_list = np.array(self.domain.grid)

        X_normalized = physbo.misc.centering(self.mesh_list[:, 1:])
        comm = self.mpicomm if self.mpisize > 1 else None
        self.policy = physbo.search.discrete.policy(test_X=X_normalized, comm=comm)
        if "seed" in info.algorithm:
            seed = info.algorithm["seed"]
            self.policy.set_seed(seed)

        # store state
        self.file_history = "history.npz"
        self.file_training = "training.npz"
        self.file_predictor = "predictor.dump"
        
    def _initialize(self):
        self.istep = 0
        self.param_list = []
        self.fx_list = []
        self.timer["run"]["random_search"] = 0.0
        self.timer["run"]["bayes_search"] = 0.0

    def _run(self) -> None:
        runner = self.runner
        mesh_list = self.mesh_list
        # fx_list = []
        # param_list = []

        class simulator:
            def __call__(self, action: np.ndarray) -> float:
                a = int(action[0])
                args = (a, 0)
                x = mesh_list[a, 1:]
                fx = runner.submit(x, args)
                fx_list.append(fx)
                param_list.append(mesh_list[a])
                return -fx

        if self.mode is None:
            raise RuntimeError("mode unset")

        restore_rng = not self.mode.endswith("-resetrand")

        if self.mode.startswith("init"):
            self._initialize()
        elif self.mode.startswith("resume"):
            self._load_state(self.checkpoint_file, mode="resume", restore_rng=restore_rng)
        elif self.mode.startswith("continue"):
            self._load_state(self.checkpoint_file, mode="continue", restore_rng=restore_rng)
        else:
            raise RuntimeError("unknown mode {}".format(self.mode))

        fx_list = self.fx_list
        param_list = self.param_list
        
        if self.mode.startswith("init"):
            time_sta = time.perf_counter()
            res = self.policy.random_search(
                max_num_probes=self.random_max_num_probes, simulator=simulator()
            )
            time_end = time.perf_counter()
            self.timer["run"]["random_search"] = time_end - time_sta
        else:
            if self.istep >= self.bayes_max_num_probes:
                res = copy.deepcopy(self.policy.history)

        next_checkpoint_step = self.istep + self.checkpoint_steps
        next_checkpoint_time = time.time() + self.checkpoint_interval

        while self.istep < self.bayes_max_num_probes:
            intv = 0 if self.istep % self.interval == 0 else -1
            
            time_sta = time.perf_counter()
            res = self.policy.bayes_search(
                max_num_probes=1,
                simulator=simulator(),
                score=self.score,
                interval=intv,
                num_rand_basis=self.num_rand_basis,
            )
            time_end = time.perf_counter()
            self.timer["run"]["bayes_search"] += time_end - time_sta

            self.istep += 1

            if self.checkpoint:
                time_now = time.time()
                if self.istep >= next_checkpoint_step or time_now >= next_checkpoint_time:
                    print(">>> checkpointing")

                    self.fx_list = fx_list
                    self.param_list = param_list
                    
                    self._save_state(self.checkpoint_file)
                    next_checkpoint_step = self.istep + self.checkpoint_steps
                    next_checkpoint_time = time_now + self.checkpoint_interval

        self.best_fx, self.best_action = res.export_all_sequence_best_fx()
        self.xopt = mesh_list[int(self.best_action[-1]), 1:]
        self.fx_list = fx_list
        self.param_list = param_list

        # store final state for continuation
        if self.checkpoint:
            print(">>> store final state")
            self._save_state(self.checkpoint_file)

    def _prepare(self) -> None:
        # do nothing
        pass

    def _post(self) -> None:
        label_list = self.label_list
        if self.mpirank == 0:
            with open("BayesData.txt", "w") as file_BD:
                file_BD.write("#step")
                for label in label_list:
                    file_BD.write(f" {label}")
                file_BD.write(" fx")
                for label in label_list:
                    file_BD.write(f" {label}_action")
                file_BD.write(" fx_action\n")

                for step, fx in enumerate(self.fx_list):
                    file_BD.write(str(step))
                    best_idx = int(self.best_action[step])
                    for v in self.mesh_list[best_idx][1:]:
                        file_BD.write(f" {v}")
                    file_BD.write(f" {-self.best_fx[step]}")

                    for v in self.param_list[step][1:]:
                        file_BD.write(f" {v}")
                    file_BD.write(f" {fx}\n")
            print("Best Solution:")
            for x, y in zip(label_list, self.xopt):
                print(x, "=", y)
        return {"x": self.xopt, "fx": self.best_fx}

    def _save_state(self, filename):
        data = {
            #-- _algorithm
            "mpisize": self.mpisize,
            "mpirank": self.mpirank,
            "rng": self.rng.get_state(),
            "timer": self.timer,
            #-- bayes
            "istep": self.istep,
            "param_list": self.param_list,
            "fx_list": self.fx_list,
            "file_history": self.file_history,
            "file_training": self.file_training,
            "file_predictor": self.file_predictor,
            "random_number": np.random.get_state(),
        }
        self._save_data(data, filename)

        #-- bayes
        tmp_hist = "tmp_" + self.file_history
        tmp_tran = "tmp_" + self.file_training
        tmp_pred = "tmp_" + self.file_predictor
        
        self.policy.save(file_history=tmp_hist,
                         file_training=tmp_tran,
                         file_predictor=tmp_pred)

        shutil.move(tmp_hist, self.file_history)
        shutil.move(tmp_tran, self.file_training)
        shutil.move(tmp_pred, self.file_predictor)

    def _load_state(self, filename, mode="resume", restore_rng=True):
        data = self._load_data(filename)
        if not data:
            print("ERROR: Load status file failed")
            sys.exit(1)

        #-- _algorithm
        assert self.mpisize == data["mpisize"]
        assert self.mpirank == data["mpirank"]

        if restore_rng:
            self.rng = np.random.RandomState()
            self.rng.set_state(data["rng"])
            np.random.set_state(data["random_number"])
        self.timer = data["timer"]

        #-- bayes
        self.istep = data["istep"]
        self.param_list = data["param_list"]
        self.fx_list = data["fx_list"]
        
        self.policy.load(file_history=data["file_history"],
                         file_training=data["file_training"],
                         file_predictor=data["file_predictor"])
