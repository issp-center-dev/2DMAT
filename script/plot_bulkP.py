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

import matplotlib.pyplot as plt
import sys

args = sys.argv

input_file = "surf-bulkP.s"
if len(args) >= 2:
    input_file = args[1]

f = open(input_file, "r")
for i in range(4):
    next(f)
angles = []
peaks = []
for line in f:
    values = line.split(",")
    if len(values) > 7:
        angles.append(float(values[0]))
        peaks.append(float(values[7]))
f.close()

plt.plot(angles, peaks, marker = "$o$", linewidth = 1.0, color = "red")
plt.xlabel("degree")
plt.ylabel("I")
plt.savefig("plot_bulkP.png", bbox_inches = "tight")
