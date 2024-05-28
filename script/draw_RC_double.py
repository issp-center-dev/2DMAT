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

file_input = open("RockingCurve_ini.txt")
lines_ini = file_input.readlines()
file_input.close()

file_input = open("RockingCurve_con.txt")
lines_con = file_input.readlines()
file_input.close()

degree_list = []
I_ini_list = []
exp_list = []
for line in lines_ini:
    if line[0] == "#":
        if line[1] == "R":
            data = line.split()
            R_ini = float(data[2])
        continue
    data = line.split()
    print("data[0]:", data[0])
    degree_list.append(float(data[0]))
    I_ini_list.append(float(data[3]))
    exp_list.append(float(data[4]))

count = -1
I_con_list = []
for line in lines_con:
    count += 1
    if line[0] == "#":
        if line[1] == "R":
            data = line.split()
            R_con = float(data[2])
        continue
    data = line.split()
    I_con_list.append(float(data[3]))

print("len(degree_list):", len(degree_list))
print("len(exp_list):", len(exp_list))
print("len(I_ini_list):", len(I_ini_list))
print("len(I_con_list):", len(I_con_list))

plt.plot(degree_list, exp_list, marker = "$o$", linewidth = 0.0, color = "red", label = "experiment")
plt.plot(degree_list, I_ini_list, marker = "None", color = "blue", label = "initial(R-factor = %f)"%(R_ini))
plt.plot(degree_list, I_con_list, marker = "None", color = "green", label = "converged(R-factor = %f)"%(R_con))
plt.xlabel("degree")
plt.ylabel("I")
plt.legend()
plt.savefig("RC_double.png", bbox_inches = "tight")

file_output = open("RC_double.txt", "w")
file_output.write("#R-factor(initial) = %f\n"%(R_ini))
file_output.write("#R-factor(converged) = %f\n"%(R_con))
file_output.write("#degree experiment I(initial) I(converged)\n")
for i in range(len(degree_list)):
    file_output.write("%f %f %f %f\n"%(degree_list[i], exp_list[i], I_ini_list[i], I_con_list[i]))
file_output.close()
