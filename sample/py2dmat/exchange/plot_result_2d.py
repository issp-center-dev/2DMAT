import matplotlib.pyplot as plt

x = []
y = []
f = []
file_input = open("result_T1.txt", "r")
lines = file_input.readlines()
file_input.close()
for line in lines:
    if line.startswith("#"):
        continue
    if line[0] != "/n":
        data = line.split()
        x.append(float(data[3]))
        y.append(float(data[4]))
        f.append(float(data[2]))

plt.scatter(x, y, c=f, s=100, vmin=0.00, vmax=0.10, cmap='RdYlBu', linewidth=2, alpha=1.0)
plt.xlabel("z1")
plt.ylabel("z2")
plt.colorbar()
plt.savefig('result.pdf')
