# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

import subprocess

import py2dmat
import py2dmat.mpi

# type hints
from pathlib import Path
from typing import Dict, List


class SolverBase(object, metaclass=ABCMeta):
    root_dir: Path
    output_dir: Path
    proc_dir: Path
    work_dir: Path
    _name: str
    dimension: int
    timer: Dict[str, Dict]

    @abstractmethod
    def __init__(self, info: py2dmat.Info) -> None:
        self.root_dir = info.base["root_dir"]
        self.output_dir = info.base["output_dir"]
        self.proc_dir = self.output_dir / str(py2dmat.mpi.rank())
        self.work_dir = self.proc_dir
        self._name = ""
        self.timer = {"prepare": {}, "run": {}, "post": {}}
        if "dimension" in info.solver:
            self.dimension = info.solver["dimension"]
        else:
            self.dimension = info.base["dimension"]

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def prepare(self, message: py2dmat.Message) -> None:
        raise NotImplementedError()

    @abstractmethod
    def run(self, nprocs: int = 1, nthreads: int = 1) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_results(self) -> float:
        raise NotImplementedError()

    def _run_by_subprocess(self, command: List[str]) -> None:
        with open("stdout", "w") as fi:
            subprocess.run(
                command,
                stdout=fi,
                stderr=subprocess.STDOUT,
                check=True,
            )
