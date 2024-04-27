from abc import ABCMeta, abstractmethod

import numpy as np


class LimitationBase(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, is_limitary: bool):
        self.islimitary = is_limitary

    @abstractmethod
    def judge(self, x: np.ndarray) -> bool:
        raise NotImplementedError


class Inequality(LimitationBase):
    def __init__(self, a: np.ndarray, b: np.ndarray, is_limitary: bool):
        super().__init__(is_limitary)
        if self.islimitary:
            self.a = a
            self.minusb = -b
            self.n_formura = a.shape[0]
            self.ndim = a.shape[1]

    def judge(self, x: np.ndarray) -> bool:
        if self.islimitary:
            Ax = np.einsum("ij,j->i", self.a, x)
            judge_result = all(Ax > self.minusb)
        else:
            judge_result = True
        return judge_result
