#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from pathlib import Path
from typing import List, Optional, Dict

from ..info import Info
from ..message import Message


class SolverBase(object, metaclass=ABCMeta):
    root_dir: Path
    output_dir: Path
    proc_dir: Optional[Path] = None
    work_dir: Optional[Path] = None

    _name: str

    timer: Dict[str, Dict] = {"prepare": {}, "run": {}, "post": {}}

    @abstractmethod
    def __init__(self, info: Info) -> None:
        info_base = info["base"]
        self.root_dir = info_base["root_dir"]
        self.output_dir = info_base["output_dir"]
        self._name = ""

    @abstractmethod
    def get_run_scheme(self):
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
    def prepare(self, message: Message) -> None:
        pass

    @abstractmethod
    def get_results(self) -> float:
        pass

    def get_working_directory(self) -> Path:
        if self.work_dir is None:
            raise RuntimeError("work_dir is not set")
        return self.work_dir
