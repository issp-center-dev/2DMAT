from abc import ABCMeta, abstractmethod

import numpy as np

import py2dmat

# for type hints
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING, Dict, Tuple

class LimitationBase(metaclass=ABCMeta):
    @abstractmethod
    def __init__ (self, a: Optional[np.ndarray] = None, 
                        b: Optional[np.ndarray] = None):
        if (a is not None) or (b is not None):
            if a is None:
                msg = "ERROR: b is defined but a is not."
                raise RuntimeError(msg)
            if b is None:
                msg = "ERROR: a is defined but b is not."
                raise RuntimeError(msg)
        if (a is None) and (b is None):
            self.islimitary = False
        else:
            self.islimitary = True
            self.a = a
            self.b = b
            self.n_formura = a.shape[0]
            self.ndim = a.shape[1]
         
    @abstractmethod
    def judge(self, x: np.ndarray) -> bool:
        pass

class Inequality(LimitationBase):
    def __init__ (self, a: Optional[np.ndarray] = None, 
                        b: Optional[np.ndarray] = None):
        super().__init__(a, b)

    def judge(self, x: np.ndarray) -> bool:
        if self.islimitary :
            judge_formula = []
            for formula_index in range(self.n_formura):
                value_formula = 0
                for dim_index in range(self.ndim):
                    value_formula += self.a[formula_index, dim_index]*x[dim_index]
                value_formula += self.b[formula_index]
                judge_formula.append(value_formula>0)
            judge_result = all(judge_formula)
        else:
            judge_result = True
        return judge_result
