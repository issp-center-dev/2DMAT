from typing import List
import time

import physbo
import numpy as np

import py2dmat


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

    def __init__(self, info: py2dmat.Info, runner: py2dmat.Runner = None) -> None:
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

        self.mesh_list, actions = self._meshgrid(info, split=False)
        X_normalized = physbo.misc.centering(self.mesh_list[:, 1:])
        comm = self.mpicomm if self.mpisize > 1 else None
        self.policy = physbo.search.discrete.policy(test_X=X_normalized, comm=comm)
        if "seed" in info.algorithm:
            seed = info.algorithm["seed"]
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
                message = py2dmat.Message(mesh_list[a, 1:], a, 0)
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
