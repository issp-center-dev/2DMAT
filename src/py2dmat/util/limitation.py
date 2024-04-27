from abc import ABCMeta, abstractmethod

import numpy as np

from .read_matrix import read_matrix, read_vector


class LimitationBase(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, is_limitary: bool):
        self.islimitary = is_limitary

    @abstractmethod
    def judge(self, x: np.ndarray) -> bool:
        raise NotImplementedError

class Unlimited(LimitationBase):
    def __init__(self):
        super().__init__(False)
    def judge(self, x: np.ndarray) -> bool:
        return True

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

    @classmethod
    def from_dict(cls, d, dimension):
        co_a: np.ndarray = read_matrix(d.get("co_a", []))
        co_b: np.ndarray = read_matrix(d.get("co_b", []))

        if co_a.size == 0:
            is_set_co_a = False
        else:
            is_set_co_a = True
            if co_a.ndim != 2:
                raise ValueError("co_a should be a matrix")
            if co_a.shape[1] != dimension:
                msg ='The number of columns in co_a should be equal to'
                msg+='the value of "dimension" in the [base] section'
                raise ValueError(msg)
            n_row_co_a = co_a.shape[0]
        if co_b.size == 0:
            if not is_set_co_a :
                is_set_co_b = False
            else: # is_set_co_a is True
                msg = "ERROR: co_a is defined but co_b is not."
                raise ValueError(msg)
        elif co_b.ndim == 2:
            if is_set_co_a:
                if co_b.shape[0] == 1 or co_b.shape[1] == 1:
                    is_set_co_b = True
                    co_b = co_b.reshape(-1)
                else:
                    raise ValueError("co_b should be a vector")
                if co_b.size != n_row_co_a:
                    msg ='The number of row in co_a should be equal to'
                    msg+='the number of size in co_b'
                    raise ValueError(msg)
            else: # not is_set_co_a:
                msg = "ERROR: co_b is defined but co_a is not."
                raise ValueError(msg)
        elif co_b.ndim > 2:
            raise ValueError("co_b should be a vector")

        if is_set_co_a and is_set_co_b:
            is_limitation = True
        elif (not is_set_co_a) and (not is_set_co_b):
            is_limitation = False
        else:
            msg = "ERROR: Both co_a and co_b must be defined."
            raise ValueError(msg)

        return cls(co_a, co_b, is_limitation)
