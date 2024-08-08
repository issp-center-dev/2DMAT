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

def quadratics(xs: np.ndarray) -> float:
    """quadratic (sphear) function

    It has one global miminum f(xs)=0 at xs = [0,0,...,0].
    """
    return np.sum(xs * xs)

class Quadratics(Solver):
    def __init__(self, info):
        super().__init__(info, fn=quadratics)
