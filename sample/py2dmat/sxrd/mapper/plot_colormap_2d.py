import matplotlib.pyplot as plt

x = []
y = []
f = []
file_input = open("ColorMap.txt", "r")
lines = file_input.readlines()
file_input.close()
for line in lines:
    if line[0] != "/n":
        data = line.split()
        x.append(float(data[0]))
        y.append(float(data[1]))
        f.append(float(data[2]))

plt.scatter(x, y, c=f, s=100, vmin=0.00, vmax=0.40, cmap='RdYlBu', linewidth=2, alpha=1.0)
plt.xlabel("z1")
plt.ylabel("z2")
plt.xlim(-0.2, 0.2)
plt.ylim(-0.2, 0.2)
plt.colorbar()
plt.savefig('ColorMapFig.png')
