# 2DMAT -- Data-analysis software of quantum beam diffraction experiments for 2D material structure
# Copyright (C) 2020- The University of Tokyo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.

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

