from typing import List

import time

import physbo
import numpy as np

from . import algorithm
from ..message import Message

# for type hints
from ..info import Info


class Algorithm(algorithm.AlgorithmBase):

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

    def __init__(self, info: Info) -> None:
        super().__init__(info=info)

        info_alg = info["algorithm"]

        # TODO: change default values
        # TODO: error check

        info_param = info_alg.get("param", {})
        # Check input files are correct or not
        self.random_max_num_probes = info_param.get("random_max_num_probes", 20)
        self.bayes_max_num_probes = info_param.get("bayes_max_num_probes", 40)
        self.score = info_param.get("score", "TS")
        self.interval = info_alg.get("interval", 5)
        self.num_rand_basis = info_alg.get("num_rand_basis", 5000)

        print("# parameter")
        print(f"random_max_num_probes = {self.random_max_num_probes}")
        print(f"bayes_max_num_probes = {self.bayes_max_num_probes}")
        print(f"score = {self.score}")
        print(f"interval = {self.interval}")
        print(f"num_rand_basis = {self.num_rand_basis}")

        mesh_path = info_param.get("mesh_path", "MeshData.txt")
        self.mesh_list = np.loadtxt(mesh_path)
        X_normalized = physbo.misc.centering(self.mesh_list[:, 1:])
        comm = self.mpicomm if self.mpisize > 1 else None
        self.policy = physbo.search.discrete.policy(test_X=X_normalized, comm=comm)
        seed = info_alg.get("seed", 1)
        self.policy.set_seed(seed)
        self.param_list = []
        self.fx_list = []

    def _run(self) -> None:
        runner = self.runner
        mesh_list = self.mesh_list
        fx_list = []
        param_list = []

        class simulator:
            def __call__(self, action: np.ndarray) -> float:
                a = int(action[0])
                message = Message(mesh_list[a, 1:], a, 0)
                fx = runner.submit(message)
                fx_list.append(fx)
                param_list.append(mesh_list[a])
                return -fx

        time_sta = time.perf_counter()
        res = self.policy.random_search(
            max_num_probes=self.random_max_num_probes, simulator=simulator()
        )
        time_end = time.perf_counter()
        self.timer["run"]["random_search"] = time_end - time_sta

        time_sta = time.perf_counter()
        res = self.policy.bayes_search(
            max_num_probes=self.bayes_max_num_probes,
            simulator=simulator(),
            score=self.score,
            interval=self.interval,
            num_rand_basis=self.num_rand_basis,
        )
        time_end = time.perf_counter()
        self.timer["run"]["bayes_search"] = time_end - time_sta
        self.best_fx, self.best_action = res.export_all_sequence_best_fx()
        self.xopt = mesh_list[int(self.best_action[-1]), 1:]
        self.fx_list = fx_list
        self.param_list = param_list

    def _prepare(self) -> None:
        self.proc_dir = self.output_dir
        self.runner.set_solver_dir(self.proc_dir)

    def _post(self) -> None:
        label_list = self.label_list
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
