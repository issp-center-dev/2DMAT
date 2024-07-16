import itertools
import numpy as np

x1 = np.linspace(-0.2, 0.2, 21)
x2 = np.linspace(-0.5, 0.5, 21)

for i, x in enumerate(itertools.product(x1,x2)):
    print(i+1,*x)
