from typing import List, MutableMapping

import os
import time

import physbo
import numpy as np

from . import algorithm

# for type hints
from ..info import Info


class Algorithm(algorithm.Algorithm):

    # inputs
    mesh_list: List[float]
    label_list: List[str]

    # hyperparameters of Bayesian optimization
    random_max_num_probes: int
    bayes_max_num_probes: int
    score: str
    interval: int
    num_rand_basis: int

    # results
    xopt: List[float]
    best_fx: float
    best_action: int
    fx_list: List[float]
    param_list: List[List[float]]

    def __init__(self, info: Info, runner) -> None:
        super().__init__(info=info, runner=runner)

        info_alg = info["algorithm"]

        # TODO: change default values
        # TODO: error check
        
        info_param = info_alg.get("param", {})
        #Check input files are correct or not
        self.random_max_num_probes = info_param.get("random_max_num_probes", 20)
        self.bayes_max_num_probes = info_param.get("bayes_max_num_probes", 40)
        self.score = info_param.get("score", "TS")
        self.interval = info_alg.get("interval", 5)
        self.num_rand_basis = info_alg.get("num_rand_basis", 5000)

        print("#parameter")
        print("random_max_num_probes = {}".format(self.random_max_num_probes))
        print("bayes_max_num_probes = {}".format(self.bayes_max_num_probes))
        print("score = {}" + self.score)
        print("interval = {}".format(self.interval))
        print("num_rand_basis = {}".format(self.num_rand_basis))

        mesh_path = info_param.get("mesh_path", "MeshData.txt")
        self.mesh_list = np.array(self._get_mesh_list_from_file(mesh_path))  
        X_normalized = physbo.misc.centering(self.mesh_list[:, 1:])
        self.policy = physbo.search.discrete.policy(test_X = X_normalized)
        seed = info_alg.get("seed", 1)
        self.policy.set_seed(seed)
        self.param_list = []
        self.fx_list = []

    def _get_mesh_list_from_file(self, filename="MeshData.txt"):
        print("Read", filename)
        mesh_list = []
        with open(filename, "r") as file_MD:
            for line in file_MD:
                line = line.lstrip()
                if line.startswith("#"):
                    continue
                mesh = []
                for value in line.split():
                    mesh.append(float(value))
                mesh_list.append(mesh)
        return mesh_list


    def run(self, run_info: Info) -> None:
        run = self.runner
        run_info["base"]["base_dir"] = os.getcwd()
        label_list = self.label_list
        mesh_list = self.mesh_list
        dimension = self.dimension
        fx_list = []
        param_list = []

        class simulator:
            def __init__(self):
                pass

            def __call__(self, action):
                run_info["log"]["Log_number"] = int(action[0])
                run_info["calc"]["x_list"] = mesh_list[action][0][1:]
                run_info["base"]["base_dir"] = os.getcwd()
                fx = run.submit(update_info=run_info)
                fx_list.append(fx)
                param_list.append(mesh_list[action])
                return -fx

        time_sta = time.perf_counter()
        res = self.policy.random_search(max_num_probes=self.random_max_num_probes, simulator=simulator())
        time_end = time.perf_counter()
        run_info["log"]["time"]["run"]["random_search"] = time_end - time_sta

        time_sta = time.perf_counter()
        res = self.policy.bayes_search(max_num_probes=self.bayes_max_num_probes, simulator=simulator(), score=self.score,
                                  interval=self.interval, num_rand_basis=self.num_rand_basis)
        time_end = time.perf_counter()
        run_info["log"]["time"]["run"]["bayes_search"] = time_end - time_sta
        self.best_fx, self.best_action = res.export_all_sequence_best_fx()
        self.xopt = mesh_list[int(self.best_action[-1])][1:]
        self.fx_list = fx_list
        self.param_list = param_list

    def prepare(self, prepare_info):
        pass

    def post(self, post_info):
        label_list = self.label_list
        with open("BayesData.txt", "w") as file_BD:
            file_BD.write("#step")
            for label in label_list:
                file_BD.write(" ")
                file_BD.write(label)
            file_BD.write(" R-factor")
            for label in label_list:
                file_BD.write(" {}_action".format(label))
            file_BD.write(" R-factor_action\n")

            for step, fx in enumerate(self.fx_list):
                file_BD.write(str(step))
                best_idx = int(self.best_action[step])
                for v in self.mesh_list[best_idx][1:]:
                    file_BD.write(" {}".format(v))
                file_BD.write(" {}".format(-self.best_fx[step]))

                for v in self.param_list[step][0][1:]:
                    file_BD.write(" {}".format(v))
                file_BD.write(" {}\n".format(fx))



        print("Best Solution:")
        for x, y in zip(label_list, self.xopt):
            print(x, "=", y)
