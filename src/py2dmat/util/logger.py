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

import time
import py2dmat

# type hints
from pathlib import Path
from typing import List, Optional

class Logger:
    logfile: Path
    buffer_index: int
    buffer_size: int
    buffer: List[str]
    num_calls: int
    time_start: float
    time_previous: float
    to_write_result: bool
    to_write_x: bool

    def __init__(self, info: Optional[py2dmat.Info] = None) -> None:
        if info is None:
            self.buffer_size = 0
            return
        info_log = info.runner.get("log", {})
        self.buffer_size = info_log.get("interval", 0)
        if self.buffer_size <= 0:
            return
        self.filename = info_log.get("filename", "runner.log")
        self.time_start = time.perf_counter()
        self.time_previous = self.time_start
        self.num_calls = 0
        self.buffer_index = 0
        self.buffer = [""] * self.buffer_size
        self.to_write_result = info_log.get("write_result", False)
        self.to_write_x = info_log.get("write_input", False)

    def disabled(self) -> bool:
        return self.buffer_size <= 0

    def prepare(self, proc_dir: Path) -> None:
        if self.disabled():
            return
        self.logfile = proc_dir / self.filename
        if self.logfile.exists():
            self.logfile.unlink()
        with open(self.logfile, "w") as f:
            f.write("# $1: num_calls\n")
            f.write("# $2: elapsed_time_from_last_call\n")
            f.write("# $3: elapsed_time_from_start\n")
            if self.to_write_result:
                f.write("# $4: result\n")
                i = 4
            else:
                i = 5
            if self.to_write_x:
                f.write(f"# ${i}-: input\n")
            f.write("\n")

    def count(self, message: py2dmat.Message, result: float) -> None:
        if self.disabled():
            return
        self.num_calls += 1
        t = time.perf_counter()
        fields = [self.num_calls, t - self.time_previous, t - self.time_start]
        if self.to_write_result:
            fields.append(result)
        if self.to_write_x:
            for x in message.x:
                fields.append(x)
        fields.append("\n")
        self.buffer[self.buffer_index] = " ".join(map(str, fields))
        self.time_previous = t
        self.buffer_index += 1
        if self.buffer_index == self.buffer_size:
            self.write()

    def write(self) -> None:
        if self.disabled():
            return
        with open(self.logfile, "a") as f:
            for i in range(self.buffer_index):
                f.write(self.buffer[i])
        self.buffer_index = 0

