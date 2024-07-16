import numpy as np
import matplotlib.pyplot as plt

x,y,f = np.loadtxt("ColorMap.txt", unpack=True)

plt.scatter(x, y, c=f, s=100, vmin=0.00, vmax=0.10, cmap='RdYlBu', linewidth=2, alpha=1.0)
plt.xlabel("z2")
plt.ylabel("z3")
plt.xlim(3.0, 6.5)
plt.ylim(3.0, 6.5)
plt.colorbar()
plt.savefig('ColorMapFig.png')
