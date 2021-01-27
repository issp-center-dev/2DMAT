#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from enum import IntEnum
import time
import os

import numpy as np
from numpy.random import default_rng

import py2dmat
from py2dmat import exception, mpi

# for type hints
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING, Dict, Tuple


if TYPE_CHECKING:
    from mpi4py import MPI


class AlgorithmStatus(IntEnum):
    INIT = 1
    PREPARE = 2
    RUN = 3


class AlgorithmBase(metaclass=ABCMeta):
    mpicomm: Optional["MPI.Comm"]
    mpisize: int
    mpirank: int
    rng: np.random.Generator
    dimension: int
    label_list: List[str]
    runner: Optional[py2dmat.Runner]

    root_dir: Path
    output_dir: Path
    proc_dir: Path

    timer: Dict[str, Dict] = {"prepare": {}, "run": {}, "post": {}}

    status: AlgorithmStatus = AlgorithmStatus.INIT

    @abstractmethod
    def __init__(self, info: py2dmat.Info) -> None:
        self.mpicomm = mpi.comm()
        self.mpisize = mpi.size()
        self.mpirank = mpi.rank()
        self.runner = None
        self.timer = {"prepare": {}, "run": {}, "post": {}}
        self.status = AlgorithmStatus.INIT

        if "dimension" not in info.base:
            raise exception.InputError(
                "ERROR: base.dimension is not defined in the input"
            )
        try:
            self.dimension = int(str(info.base["dimension"]))
        except ValueError:
            raise exception.InputError(
                "ERROR: base.dimension should be positive integer"
            )
        if self.dimension < 1:
            raise exception.InputError(
                "ERROR: base.dimension should be positive integer"
            )

        if "label_list" in info.algorithm:
            label = info.algorithm["label_list"]
            if len(label) != self.dimension:
                raise exception.InputError(
                    f"ERROR: len(label_list) != dimension ({len(label)} != {self.dimension})"
                )
            self.label_list = label
        else:
            self.label_list = [f"x{d+1}" for d in range(self.dimension)]

        self.__init_rng(info)

        self.root_dir = info.base["root_dir"]
        self.output_dir = info.base["output_dir"]
        self.proc_dir = self.output_dir / str(self.mpirank)
        self.proc_dir.mkdir(parents=True, exist_ok=True)
        # Some cache of the filesystem may delay making a dictionary
        # especially when mkdir just after removing the old one
        while not self.proc_dir.is_dir():
            time.sleep(0.1)
        self.mpicomm.Barrier()

    def __init_rng(self, info: py2dmat.Info) -> None:
        seed = info.algorithm.get("seed", None)
        seed_delta = info.algorithm.get("seed_delta", 314159)

        if seed is None:
            self.rng = default_rng()
        else:
            self.rng = default_rng(seed + self.mpirank * seed_delta)

    def _read_param(self, info: py2dmat.Info) -> Tuple[np.array, np.array, np.array, np.array]:
        """

        Returns
        =======
        initial_list
        min_list
        max_list
        unit_list
        """
        if "param" not in info.algorithm:
            raise exception.InputError(
                "ERROR: [algorithm.param] is not defined in the input"
            )
        info_param = info.algorithm["param"]

        if "min_list" not in info_param:
            raise exception.InputError(
                "ERROR: algorithm.param.min_list is not defined in the input"
            )
        min_list = np.array(info_param["min_list"])
        if len(min_list) != self.dimension:
            raise exception.InputError(
                f"ERROR: len(min_list) != dimension ({len(min_list)} != {self.dimension})"
            )

        if "max_list" not in info_param:
            raise exception.InputError(
                "ERROR: algorithm.param.max_list is not defined in the input"
            )
        max_list = np.array(info_param["max_list"])
        if len(max_list) != self.dimension:
            raise exception.InputError(
                f"ERROR: len(max_list) != dimension ({len(max_list)} != {self.dimension})"
            )

        unit_list = np.array(info_param.get("unit_list", [1.0] * self.dimension))
        if len(unit_list) != self.dimension:
            raise exception.InputError(
                f"ERROR: len(unit_list) != dimension ({len(unit_list)} != {self.dimension})"
            )

        initial_list = np.array(info_param.get("initial_list", []))
        if initial_list.size == 0:
            initial_list = min_list + (max_list - min_list) * self.rng.random(
                size=self.dimension
            )
        if initial_list.size != self.dimension:
            raise exception.InputError(
                f"ERROR: len(initial_list) != dimension ({initial_list.size} != {self.dimension})"
            )
        return initial_list, min_list, max_list, unit_list

    def set_runner(self, runner: py2dmat.Runner) -> None:
        self.runner = runner

    def prepare(self) -> None:
        if self.runner is None:
            msg = "Runner is not assigned"
            raise RuntimeError(msg)
        self.runner.set_solver_dir(self.proc_dir)
        self._prepare()
        self.status = AlgorithmStatus.PREPARE

    @abstractmethod
    def _prepare(self) -> None:
        pass

    def run(self) -> None:
        if self.status < AlgorithmStatus.PREPARE:
            msg = "algorithm has not prepared yet"
            raise RuntimeError(msg)
        original_dir = os.getcwd()
        os.chdir(self.proc_dir)
        self._run()
        os.chdir(original_dir)
        self.status = AlgorithmStatus.RUN

    @abstractmethod
    def _run(self) -> None:
        pass

    def post(self) -> None:
        if self.status < AlgorithmStatus.RUN:
            msg = "algorithm has not run yet"
            raise RuntimeError(msg)
        original_dir = os.getcwd()
        os.chdir(self.output_dir)
        self._post()
        os.chdir(original_dir)

    @abstractmethod
    def _post(self) -> None:
        pass

    def main(self):
        time_sta = time.perf_counter()
        self.prepare()
        time_end = time.perf_counter()
        self.timer["prepare"]["total"] = time_end - time_sta
        if mpi.size() > 1:
            mpi.comm().Barrier()

        time_sta = time.perf_counter()
        self.run()
        time_end = time.perf_counter()
        self.timer["run"]["total"] = time_end - time_sta
        print("end of run")
        if mpi.size() > 1:
            mpi.comm().Barrier()

        time_sta = time.perf_counter()
        self.post()
        time_end = time.perf_counter()
        self.timer["post"]["total"] = time_end - time_sta

        with open(self.proc_dir / "time.log", "w") as fw:
            fw.write("#in units of seconds")
            def output_file(type):
                tmp_dict = self.timer[type]
                fw.write("#{}\n total = {}\n".format(type, tmp_dict["total"]))
                for key, t in tmp_dict.items():
                    if key == "total":
                        continue
                    fw.write(" - {} = {}\n".format(key, t))

            output_file("prepare")
            output_file("run")
            output_file("post")
