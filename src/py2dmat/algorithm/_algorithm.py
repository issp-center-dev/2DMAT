# -*- coding: utf-8 -*-

# 2DMAT -- Data-analysis software of quantum beam diffraction experiments for 2D material structure
# Copyright (C) 2020- The University of Tokyo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.


from abc import ABCMeta, abstractmethod
from enum import IntEnum
import time
import os
import pathlib
import pickle
import shutil

import numpy as np

import py2dmat
import py2dmat.util.limitation
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
    rng: np.random.RandomState
    dimension: int
    label_list: List[str]
    runner: Optional[py2dmat.Runner]

    root_dir: Path
    output_dir: Path
    proc_dir: Path

    timer: Dict[str, Dict]

    status: AlgorithmStatus = AlgorithmStatus.INIT
    mode: Optional[str] = None

    @abstractmethod
    def __init__(
        self, info: py2dmat.Info, runner: Optional[py2dmat.Runner] = None
    ) -> None:
        self.mpicomm = mpi.comm()
        self.mpisize = mpi.size()
        self.mpirank = mpi.rank()
        self.timer = {"init": {}, "prepare": {}, "run": {}, "post": {}}
        self.timer["init"]["total"] = 0.0
        self.status = AlgorithmStatus.INIT
        self.mode = None

        self.dimension = info.algorithm.get("dimension") or info.base.get("dimension")
        if not self.dimension:
            raise ValueError("ERROR: dimension is not defined")

        if "label_list" in info.algorithm:
            label = info.algorithm["label_list"]
            if len(label) != self.dimension:
                raise ValueError(f"ERROR: length of label_list and dimension do not match ({len(label)} != {self.dimension})")
            self.label_list = label
        else:
            self.label_list = [f"x{d+1}" for d in range(self.dimension)]

        # initialize random number generator
        self.__init_rng(info)

        # directories
        self.root_dir = info.base["root_dir"]
        self.output_dir = info.base["output_dir"]
        self.proc_dir = self.output_dir / str(self.mpirank)
        self.proc_dir.mkdir(parents=True, exist_ok=True)
        # Some cache of the filesystem may delay making a dictionary
        # especially when mkdir just after removing the old one
        while not self.proc_dir.is_dir():
            time.sleep(0.1)
        if self.mpisize > 1:
            self.mpicomm.Barrier()

        # checkpointing
        self.checkpoint = info.algorithm.get("checkpoint", False)
        self.checkpoint_file = info.algorithm.get("checkpoint_file", "status.pickle")
        self.checkpoint_steps = info.algorithm.get("checkpoint_steps", 65536*256)  # large number
        self.checkpoint_interval = info.algorithm.get("checkpoint_interval", 86400*360)  # longer enough

        # runner
        if runner is not None:
            self.set_runner(runner)

    def __init_rng(self, info: py2dmat.Info) -> None:
        seed = info.algorithm.get("seed", None)
        seed_delta = info.algorithm.get("seed_delta", 314159)

        if seed is None:
            self.rng = np.random.RandomState()
        else:
            self.rng = np.random.RandomState(seed + self.mpirank * seed_delta)

    def set_runner(self, runner: py2dmat.Runner) -> None:
        self.runner = runner

    def prepare(self) -> None:
        if self.runner is None:
            msg = "Runner is not assigned"
            raise RuntimeError(msg)
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
        self.runner.prepare(self.proc_dir)
        self._run()
        self.runner.post()
        os.chdir(original_dir)
        self.status = AlgorithmStatus.RUN

    @abstractmethod
    def _run(self) -> None:
        pass

    def post(self) -> Dict:
        if self.status < AlgorithmStatus.RUN:
            msg = "algorithm has not run yet"
            raise RuntimeError(msg)
        original_dir = os.getcwd()
        os.chdir(self.output_dir)
        result = self._post()
        os.chdir(original_dir)
        return result

    @abstractmethod
    def _post(self) -> Dict:
        pass

    def main(self, run_mode: str = "initialize"):
        self.mode = run_mode.lower()

        time_sta = time.perf_counter()
        self.prepare()
        time_end = time.perf_counter()
        self.timer["prepare"]["total"] = time_end - time_sta
        if self.mpisize > 1:
            self.mpicomm.Barrier()

        time_sta = time.perf_counter()
        self.run()
        time_end = time.perf_counter()
        self.timer["run"]["total"] = time_end - time_sta
        print("end of run")
        if self.mpisize > 1:
            self.mpicomm.Barrier()

        time_sta = time.perf_counter()
        result = self.post()
        time_end = time.perf_counter()
        self.timer["post"]["total"] = time_end - time_sta

        self.write_timer(self.proc_dir / "time.log")

        return result

    def write_timer(self, filename: Path):
        with open(filename, "w") as fw:
            fw.write("#in units of seconds\n")

            def output_file(type):
                d = self.timer[type]
                fw.write("#{}\n total = {}\n".format(type, d["total"]))
                for key, t in d.items():
                    if key == "total":
                        continue
                    fw.write(" - {} = {}\n".format(key, t))

            output_file("init")
            output_file("prepare")
            output_file("run")
            output_file("post")

    def _save_data(self, data, filename="state.pickle", ngen=3) -> None:
        try:
            fn = Path(filename + ".tmp")
            with open(fn, "wb") as f:
                pickle.dump(data, f)
        except Exception as e:
            print("ERROR: {}".format(e))
            sys.exit(1)

        for idx in range(ngen-1, 0, -1):
            fn_from = Path(filename + "." + str(idx))
            fn_to = Path(filename + "." + str(idx+1))
            if fn_from.exists():
                shutil.move(fn_from, fn_to)
        if ngen > 0:
            if Path(filename).exists():
                fn_to = Path(filename + "." + str(1))
                shutil.move(Path(filename), fn_to)
        shutil.move(Path(filename + ".tmp"), Path(filename))
        print("save_state: write to {}".format(filename))

    def _load_data(self, filename="state.pickle") -> Dict:
        if Path(filename).exists():
            try:
                fn = Path(filename)
                with open(fn, "rb") as f:
                    data = pickle.load(f)
            except Exception as e:
                print("ERROR: {}".format(e))
                sys.exit(1)
            print("load_state: load from {}".format(filename))
        else:
            print("ERROR: file {} not exist.".format(filename))
            data = {}
        return data
