#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

from .. import exception

# for type hints
from typing import List
from ..runner.runner import Runner
from ..info import Info


class Algorithm(metaclass=ABCMeta):
    dimension: int
    label_list: List[str]

    def __init__(self, info:Info, runner: Runner) -> None:
        self.runner = runner
        self.dimension = info["base"]["dimension"]
        info_alg = info["algorithm"]
        if "label_list" in info_alg:
            l = info_alg["label_list"]
            if len(l) != self.dimension:
                raise exception.InputError(
                    f"ERROR: len(label_list) != dimension ({len(l)} != {self.dimension})"
                )
            self.label_list = l
        else:
            self.label_list = [f"x{d+1}" for d in range(self.dimension)]

    @abstractmethod
    def run(self, run_info) -> None:
        pass

    @abstractmethod
    def prepare(self, prepare_info) -> None:
        pass

    @abstractmethod
    def post(self, post_info) -> None:
        pass
