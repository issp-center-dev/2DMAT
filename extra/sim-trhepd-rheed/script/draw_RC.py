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

import numpy as np
import matplotlib.pyplot as plt

def read_rocking_curve(filename):
    degree_list = []
    ival_list = []
    r_factor = 0.0
    with open(filename, "r") as fp:
        lines = fp.readlines()
        for line in lines:
            if line[0] == "#":
                if line[1] == "f":
                    r_factor = float((line.split())[2])
                continue
            v = line.split()
            degree_list.append(float(v[0]))
            ival_list.append(float(v[1]))
    return degree_list, ival_list, r_factor

def read_exp(filename):
    degree_list, exp_list = np.loadtxt(filename, unpack=True)
    exp_list /= np.sum(exp_list)
    return degree_list, exp_list


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Draw rocking curves")
    parser.add_argument("inputfiles", nargs="+", help="rocking curve data")
    parser.add_argument("--exp", default="experiment.txt", help="experiment data")
    parser.add_argument("--output", default="RC.png", help="output file")
    parser.add_argument("--no-legend", action="store_true", help="hide legend")
    parser.add_argument("--version", action="version", version="0.1")
    args = parser.parse_args()

    cmap = plt.get_cmap("tab10")

    for idx, inputfile in enumerate(args.inputfiles, 1):
        print("input_file={}".format(inputfile))
        d_list, i_list, rval = read_rocking_curve(inputfile)
        plt.plot(d_list, i_list, marker="None", color=cmap(idx%10), label="Curve #%i (R-factor = %f)"%(idx, rval))

    degree_list, exp_list = read_exp(args.exp)
    plt.plot(degree_list, exp_list, marker = "$o$", linewidth = 0.0, color = "red", label = "experiment")

    plt.xlabel("degree")
    plt.ylabel("I")
    if (not args.no_legend) and len(args.inputfiles) <= 8:
        plt.legend()
    plt.savefig(args.output, bbox_inches = "tight")

if __name__ == "__main__":
    main()
