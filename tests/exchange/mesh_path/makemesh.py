import itertools
import numpy as np

D = 2
xmin = -5.0
xmax = 5.0
N = 101
xs = np.linspace(xmin, stop=xmax, num=N)

i = 0
for x, y in itertools.product(xs, xs):
    if x < y: continue
    print(f"{i} {x:1.4} {y:1.4}")
    i += 1
