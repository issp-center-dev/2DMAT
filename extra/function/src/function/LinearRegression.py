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
import py2dmat
from .function import Solver

class _LinearRegression:
    def __init__(self, xdata, ydata):
        self.xdata = np.array(xdata)
        self.ydata = np.array(ydata)
        self.n = len(xdata)

    def __call__(self, xs: np.ndarray) -> float:
        """ Negative log likelihood of linear regression with Gaussian noise N(0,sigma)

        y = ax + b

        example:
        trained by xdata = [1, 2, 3, 4, 5, 6] and ydata = [1, 3, 2, 4, 3, 5].

        Model parameters (a, b, sigma) are corresponding to xs as the following,
        a = xs[0], b = xs[1], log(sigma**2) = xs[2]

        It has a global minimum f(xs) = 1.005071.. at
        xs = [0.628571..., 0.8, -0.664976...].    
        """
        assert xs.shape[0] == 3, f"ERROR: regression expects d=3 input, but receives d={xs.shape[0]} one"

        a, b, w = xs
        return 0.5 * (self.n * w + np.sum((a * self.xdata + b - self.ydata) ** 2) / np.exp(w))

class LinearRegression(Solver):
    def __init__(self, info, xdata, ydata):
        super().__init__(info)
        self.set_function(_LinearRegression(xdata, ydata))
