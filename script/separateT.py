#!/usr/bin/env python3

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


from sys import argv
from collections import namedtuple
from typing import List, Dict
from pathlib import Path

Entry = namedtuple("Entry", ["rank", "step", "fx", "xs"])


def load_best(filename: Path) -> Dict[str, str]:
    res = {}
    with open(filename) as f:
        for line in f:
            words = line.split("=")
            res[words[0].strip()] = words[1].strip()
    return res


output_dir = Path("." if len(argv) == 1 else argv[1])
nprocs: int = int(load_best(output_dir / "best_result.txt")["nprocs"])

Ts: List[float] = []
labels: List[str] = []
dim: int = 0
results: Dict[float, List[Entry]] = {}

for rank in range(nprocs):
    with open(output_dir / str(rank) / "result.txt") as f:
        line = f.readline()
        labels = line.split()[4:]

        line = f.readline()
        words = line.split()
        T = float(words[2])
        Ts.append(T)
        results[T] = []
        dim = len(words) - 4

for rank in range(nprocs):
    with open(output_dir / str(rank) / "result.txt") as f:
        f.readline()
        for line in f:
            words = line.split()
            step = int(words[0])
            T = float(words[2])
            fx = float(words[3])
            res = [float(words[i + 4]) for i in range(dim)]
            results[T].append(Entry(rank=rank, step=step, fx=fx, xs=res))

for T in Ts:
    results[T].sort(key=lambda entry: entry.step)

for i, T in enumerate(Ts):
    with open(output_dir / f"result_T{i}.txt", "w") as f:
        f.write(f"# T = {T}\n")
        f.write("# step rank fx")
        for label in labels:
            f.write(f" {label}")
        f.write("\n")
        for entry in results[T]:
            f.write(f"{entry.step} ")
            f.write(f"{entry.rank} ")
            f.write(f"{entry.fx} ")
            for x in entry.xs:
                f.write(f"{x} ")
            f.write("\n")
