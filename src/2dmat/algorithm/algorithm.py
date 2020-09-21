#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class Algorithm(metaclass =ABCMeta):

    def __init__(self, Solver, myconfig):
        self.solver = Solver
        self.config = myconfig

    @abstractmethod
    def run(self, run_info):
        pass

class Param(metaclass =ABCMeta):

    def __init__(self):
        pass

    def from_dict(cls, dict):
        params = cls()
        return params

    def from_toml(cls, file_name):
        import toml
        return cls.from_dict(toml.load(file_name))

