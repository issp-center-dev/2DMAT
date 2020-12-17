import matplotlib.pyplot as plt

file_input = open("RockingCurve.txt")
lines_ini = file_input.readlines()
file_input.close()

degree_list = []
I_list = []
exp_list = []
for line in lines_ini:
    if line[0] == "#":
        if line[1] == "R":
            data = line.split()
            Rfactor = float(data[2])
        continue
    data = line.split()
    print("data[0]:", data[0])
    degree_list.append(float(data[0]))
    I_list.append(float(data[3]))
    exp_list.append(float(data[4]))

print("len(degree_list):", len(degree_list))
print("len(exp_list):", len(exp_list))
print("len(I_list):", len(I_list))

plt.plot(degree_list, exp_list, marker = "$o$", linewidth = 0.0, color = "red", label = "experiment")
plt.plot(degree_list, I_list, marker = "None", color = "blue", label = "calculated(R-factor = %f)"%(Rfactor))
plt.xlabel("degree")
plt.ylabel("I")
plt.legend()
plt.savefig("RC_single.png", bbox_inches = "tight")

file_output = open("RC_single.txt", "w")
file_output.write("#R-factor = %f\n"%(Rfactor))
file_output.write("#degree experiment I(initial)\n")
for i in range(len(degree_list)):
    file_output.write("%f %f %f\n"%(degree_list[i], exp_list[i], I_list[i]))
file_output.close()
