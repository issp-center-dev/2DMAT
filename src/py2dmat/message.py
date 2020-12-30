import numpy as np
from typing import Iterable, Union


class Message:
    x: np.ndarray
    step: int
    set: int

    def __init__(self, x: Union[np.ndarray, Iterable], step: int, set: int) -> None:
        self.x = x
        self.step = step
        self.set = set
