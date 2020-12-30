#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from enum import IntEnum
import time

from .. import exception, mpi

# for type hints
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING, Dict
from ..runner.runner import Runner
from ..info import Info


if TYPE_CHECKING:
    from mpi4py import MPI


class AlgorithmStatus(IntEnum):
    INIT = 1
    PREPARE = 2
    RUN = 3


class AlgorithmBase(metaclass=ABCMeta):
    comm: Optional["MPI.Comm"] = mpi.comm()
    size: int = mpi.size()
    rank: int = mpi.rank()
    dimension: int
    label_list: List[str]
    runner: Optional[Runner] = None

    root_dir: Path
    output_dir: Path
    proc_dir: Optional[Path] = None

    timer: Dict[str, Dict] = {"prepare": {}, "run": {}, "post": {}}

    status: AlgorithmStatus = AlgorithmStatus.INIT

    def __init__(self, info: Info) -> None:
        info_base = info["base"]
        self.root_dir = info_base["root_dir"]
        self.output_dir = info_base["output_dir"]
        self.dimension = info_base["dimension"]

        info_alg = info["algorithm"]
        if "label_list" in info_alg:
            label = info_alg["label_list"]
            if len(label) != self.dimension:
                raise exception.InputError(
                    f"ERROR: len(label_list) != dimension ({len(label)} != {self.dimension})"
                )
            self.label_list = label
        else:
            self.label_list = [f"x{d+1}" for d in range(self.dimension)]

    def set_runner(self, runner: Runner) -> None:
        self.runner = runner

    @abstractmethod
    def prepare(self) -> None:
        if self.runner is None:
            msg = "Runner is not assigned"
            raise RuntimeError(msg)
        self.status = AlgorithmStatus.PREPARE

    @abstractmethod
    def run(self) -> None:
        if self.status < AlgorithmStatus.PREPARE:
            msg = "algorithm has not prepared yet"
            raise RuntimeError(msg)
        self.status = AlgorithmStatus.RUN

    @abstractmethod
    def post(self) -> None:
        if self.status < AlgorithmStatus.RUN:
            msg = "algorithm has not run yet"
            raise RuntimeError(msg)

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

        with open(self.output_dir / f"time_rank{mpi.rank()}.log", "w") as fw:

            def output_file(type):
                tmp_dict = self.timer[type]
                fw.write("#{}\n total = {} [s]\n".format(type, tmp_dict["total"]))
                for key, t in tmp_dict.items():
                    if key == "total":
                        continue
                    fw.write(" - {} = {}\n".format(key, t))

            output_file("prepare")
            output_file("run")
            output_file("post")
