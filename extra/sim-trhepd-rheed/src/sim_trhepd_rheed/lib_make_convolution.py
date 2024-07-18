import numpy as np

def calc(data, omega):
    sigma = 0.5 * omega / (np.sqrt(2.0 * np.log(2.0)))

    def g(x):
        g = (1.0 / (sigma * np.sqrt(2.0 * np.pi))) * np.exp(-0.5 * x**2 / sigma**2)
        return g

    conv = np.zeros(data.shape)

    xs = np.array(data[:,0])
    vs = data[:,1:]

    dxs = np.roll(xs,-1) - xs
    dxs[-1] = dxs[-2]

    ys = np.zeros(vs.shape)

    for idx in range(xs.shape[0]):
        ys[idx] = np.einsum('ik,i,i->k', vs, g(xs-xs[idx]), dxs)

    conv[:,0] = xs
    conv[:,1:] = ys

    # if verbose_mode:
    #     print("conv =\n", conv)

    return conv

