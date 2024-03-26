from abc import ABCMeta, abstractmethod

import numpy as np


class LimitationBase(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, a: np.ndarray, b: np.ndarray, is_limitary: bool):

        self.islimitary = is_limitary
        if self.islimitary:
            self.a = a
            self.minusb = -b
            self.n_formura = a.shape[0]
            self.ndim = a.shape[1]

    @abstractmethod
    def judge(self, x: np.ndarray) -> bool:
        pass


class Inequality(LimitationBase):
    def __init__(self, a: np.ndarray, b: np.ndarray, is_limitary: bool):
        super().__init__(a, b, is_limitary)

    def judge(self, x: np.ndarray) -> bool:
        if self.islimitary:
            Ax = np.einsum("ij,j->i", self.a, x)
            judge_result = all(Ax > self.minusb)
        else:
            judge_result = True
        return judge_result
