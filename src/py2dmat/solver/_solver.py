# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

import py2dmat

# type hints
from pathlib import Path
from typing import Optional, Dict


class SolverBase(object, metaclass=ABCMeta):
    root_dir: Path
    output_dir: Path
    work_dir: Optional[Path]
    proc_dir: Optional[Path]
    _name: str
    timer: Dict[str, Dict]

    @abstractmethod
    def __init__(self, info: py2dmat.Info) -> None:
        info_base = info["base"]
        self.root_dir = info_base["root_dir"]
        self.output_dir = info_base["output_dir"]
        self.work_dir = None
        self.proc_dir = None
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

    def get_working_directory(self) -> Path:
        if self.work_dir is None:
            raise RuntimeError("work_dir is not set")
        return self.work_dir
