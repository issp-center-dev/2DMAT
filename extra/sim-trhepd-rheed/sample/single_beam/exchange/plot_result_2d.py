import numpy as np
import matplotlib.pyplot as plt

_,_,f,x,y = np.loadtxt("result_T1.txt", unpack=True)

plt.scatter(x, y, c=f, s=100, vmin=0.00, vmax=0.10, cmap='RdYlBu', linewidth=2, alpha=1.0)
plt.xlabel("z1")
plt.ylabel("z2")
plt.colorbar()
plt.savefig('result.pdf')
