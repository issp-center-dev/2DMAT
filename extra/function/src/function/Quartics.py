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

def quartics(xs: np.ndarray) -> float:
    """quartic function with two minimum

    It has two global minimum f(xs)=0 at xs = [1,1,...,1] and [0,0,...,0].
    It has one suddle point f(0,0,...,0) = 1.0.
    """

    return np.mean((xs - 1.0) ** 2) * np.mean((xs + 1.0) ** 2)

class Quartics(Solver):
    def __init__(self, info):
        super().__init__(info, fn=quartics)
