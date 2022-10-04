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

from typing import Dict, List
import pathlib
from os import PathLike
from collections import namedtuple

import numpy as np

from py2dmat import mpi

Entry = namedtuple("Entry", ["step", "walker", "fx", "xs"])


def separateT(Ts: np.ndarray, nwalkers: int, output_dir: PathLike, comm: mpi.Comm, use_beta:bool) -> None:
    if comm is None:
        mpisize = 1
        mpirank = 0
    else:
        mpisize = comm.size
        mpirank = comm.rank
    output_dir = pathlib.Path(output_dir)
    proc_dir = output_dir / str(mpirank)

    T2idx = {T: i for i, T in enumerate(Ts)}
    T2rank = {}
    results = []
    for rank, Ts_local in enumerate(np.array_split(Ts, mpisize)):
        d: Dict[str, List[Entry]] = {}
        for T in Ts_local:
            T2rank[str(T)] = rank
            d[str(T)] = []
        results.append(d)

    with open(proc_dir / "result.txt") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if len(line) == 0:
                continue
            words = line.split()
            step = int(words[0])
            walker = mpirank * nwalkers + int(words[1])
            Tstr = words[2]
            fx = words[3]
            xs = words[4:]
            entry = Entry(step=step, walker=walker, fx=fx, xs=xs)
            rank = T2rank[Tstr]
            results[rank][Tstr].append(entry)
    if mpisize > 1:
        results = comm.alltoall(results)
    d = results[0]
    for i in range(1, len(results)):
        for key in d.keys():
            d[key].extend(results[i][key])
    for T in Ts[mpirank * nwalkers : (mpirank + 1) * nwalkers]:
        idx = T2idx[T]
        d[str(T)].sort(key=lambda e: e.step)
        with open(output_dir / f"result_T{idx}.txt", "w") as f:
            if use_beta:
                f.write(f"# beta = {T}\n")
            else:
                f.write(f"# T = {T}\n")
            for e in d[str(T)]:
                f.write(f"{e.step} ")
                f.write(f"{e.walker} ")
                f.write(f"{e.fx} ")
                for x in e.xs:
                    f.write(f"{x} ")
                f.write("\n")
