# -*- coding: utf-8 -*-
import copy
import numpy as np

# type hints
from typing import Optional


class Affine:
    A: Optional[np.ndarray]
    b: Optional[np.ndarray]

    def __init__(self, A: np.ndarray = None, b: np.ndarray = None):
        self.A = A
        self.b = b

    def __call__(self, x: np.ndarray) -> np.ndarray:
        if self.A is None:
            ret = copy.copy(x)
        else:
            ret = np.dot(self.A, x)
        if self.b is None:
            return ret
        else:
            return ret + self.b
