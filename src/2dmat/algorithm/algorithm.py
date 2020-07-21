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