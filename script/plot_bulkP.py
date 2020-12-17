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
