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

def himmelblau(xs: np.ndarray) -> float:
    """Himmelblau's function

    It has four global minima f(xs) = 0 at
    xs=[3,2], [-2.805118..., 3.131312...], [-3.779310..., -3.2831860], and [3.584428..., -1.848126...].
    """
    assert xs.shape[0] == 2, f"ERROR: himmelblau expects d=2 input, but receives d={xs.shape[0]} one"
    x, y = xs
    return (x ** 2 + y - 11.0) ** 2 + (x + y ** 2 - 7.0) ** 2

class Himmelblau(Solver):
    def __init__(self, info):
        super().__init__(info, fn=himmelblau)
