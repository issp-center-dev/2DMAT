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

from sys import exit

import py2dmat
import py2dmat.mpi
import py2dmat.util.toml

from leed import Solver

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Data-analysis software of quantum beam "
            "diffraction experiments for 2D material structure"
        )
    )
    parser.add_argument("inputfile", help="input file with TOML format")
    parser.add_argument("--version", action="version", version=py2dmat.__version__)

    args = parser.parse_args()

    file_name = args.inputfile
    inp = {}
    if py2dmat.mpi.rank() == 0:
        inp = py2dmat.util.toml.load(file_name)
    if py2dmat.mpi.size() > 1:
        inp = py2dmat.mpi.comm().bcast(inp, root=0)
    info = py2dmat.Info(inp)

    algname = info.algorithm["name"]
    if algname == "mapper":
        from py2dmat.algorithm.mapper_mpi import Algorithm
    elif algname == "minsearch":
        from py2dmat.algorithm.min_search import Algorithm
    elif algname == "exchange":
        from py2dmat.algorithm.exchange import Algorithm
    elif algname == "pamc":
        from py2dmat.algorithm.pamc import Algorithm
    elif algname == "bayes":
        from py2dmat.algorithm.bayes import Algorithm
    else:
        print(f"ERROR: Unknown algorithm ({algname})")
        exit(1)

    solver = Solver(info)
    runner = py2dmat.Runner(solver, info)
    alg = Algorithm(info, runner)
    alg.main()

if __name__ == "__main__":
    main()
