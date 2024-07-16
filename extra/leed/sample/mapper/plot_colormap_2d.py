import matplotlib.pyplot as plt
import numpy as np

x,y,f = np.loadtxt("output/ColorMap.txt", unpack=True)

plt.scatter(x, y, c=f, s=100, vmin=0.00, vmax=1.00, cmap='RdYlBu', linewidth=2, alpha=1.0)
plt.xlabel("z1")
plt.ylabel("z2")
#plt.xlim(3.0, 6.5)
#plt.ylim(3.0, 6.5)
plt.colorbar()
plt.savefig('ColorMapFig.png')
plt.savefig('ColorMapFig.pdf')
