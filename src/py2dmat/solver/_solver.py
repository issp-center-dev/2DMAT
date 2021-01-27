# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

import py2dmat
import py2dmat.mpi

# type hints
from pathlib import Path
from typing import Dict


class SolverBase(object, metaclass=ABCMeta):
    root_dir: Path
    output_dir: Path
    proc_dir: Path
    work_dir: Path
    _name: str
    timer: Dict[str, Dict]

    @abstractmethod
    def __init__(self, info: py2dmat.Info) -> None:
        self.root_dir = info.base["root_dir"]
        self.output_dir = info.base["output_dir"]
        self.proc_dir = self.output_dir / str(py2dmat.mpi.rank())
        self.work_dir = self.proc_dir
        self._name = ""
        self.timer = {"prepare": {}, "run": {}, "post": {}}

    @abstractmethod
    def default_run_scheme(self) -> str:
        """
        Return
        -------
        str
            run_scheme.
        """
        pass

    @property
    def name(self) -> str:
        return self._name

    def command(self):
        raise NotImplementedError()

    def function(self):
        raise NotImplementedError()

    @abstractmethod
    def prepare(self, message: py2dmat.Message) -> None:
        pass

    @abstractmethod
    def get_results(self) -> float:
        pass
