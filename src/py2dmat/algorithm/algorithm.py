#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from enum import IntEnum

from .. import exception, mpi

# for type hints
from typing import List, Optional, TYPE_CHECKING
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

    status: AlgorithmStatus = AlgorithmStatus.INIT

    def __init__(self, info: Info) -> None:
        self.dimension = info["base"]["dimension"]
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
    def prepare(self, prepare_info) -> None:
        if self.runner is None:
            msg = "Runner is not assigned"
            raise RuntimeError(msg)
        self.status = AlgorithmStatus.PREPARE

    @abstractmethod
    def run(self, run_info) -> None:
        if self.status < AlgorithmStatus.PREPARE:
            msg = "algorithm has not prepared yet"
            raise RuntimeError(msg)
        self.status = AlgorithmStatus.RUN

    @abstractmethod
    def post(self, post_info) -> None:
        if self.status < AlgorithmStatus.RUN:
            msg = "algorithm has not run yet"
            raise RuntimeError(msg)
