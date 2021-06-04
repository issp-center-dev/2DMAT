from typing import Union, List

import numpy as np


def read_vector(inp: Union[str, List[float]]) -> np.ndarray:
    if isinstance(inp, str):
        vlist = [float(w) for w in inp.split()]
    else:
        vlist = inp
    v = np.array(vlist)
    if v.ndim > 1:
        msg = f"input is not vector ({inp})"
        raise RuntimeError(msg)
    return v


def read_matrix(inp: Union[str, List[List[float]]]) -> np.ndarray:
    if isinstance(inp, str):
        Alist: List[List[float]] = []
        for line in inp.split("\n"):
            if not line.strip():  # empty
                continue
            Alist.append([float(w) for w in line.strip().split()])
    else:
        Alist = inp
    A = np.array(Alist)
    if A.size == 0 or A.ndim == 2:
        return A
    msg = f"input is not matrix ({inp})"
    raise RuntimeError(msg)
