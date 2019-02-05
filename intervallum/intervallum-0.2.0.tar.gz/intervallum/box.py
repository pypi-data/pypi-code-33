from copy import copy

import numpy as np
from typing import Union, List, Tuple
from itertools import accumulate
import random

from intervallum.interval import Interval, IntervalNumber
from intervallum.interval_functions import split


BoxVector = Union["Box", np.ndarray]


class Box(np.ndarray):

    def __new__(cls, *args, **kwargs):
        obj = np.array(args).view(cls)
        return obj

    def __str__(self) -> str:
        return " x ".join(v.__str__() for v in self)

    def __repr__(self) -> str:
        return " x ".join(v.__repr__() for v in self)

    def __eq__(self, other: object) -> bool:
        if not (isinstance(other, np.ndarray) or isinstance(other, Box)):
            raise NotImplementedError()
        return np.array_equal(self, other)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __copy__(self) -> "Box":
        return Box(*[copy(i) for i in self])

    @property
    def middle(self) -> np.ndarray:
        return np.array([i.middle if isinstance(i, Interval) else i for i in self])

    @property
    def width(self) -> Tuple[List[int], float]:
        widths = [i.width if isinstance(i, Interval) else 0 for i in self]
        max_width = max(widths)
        return [i for i, w in enumerate(widths) if w == max_width], max_width

    def _try_to_reduce(self) -> BoxVector:
        if self.width[1] == 0.0:
            return self.middle
        else:
            return copy(self)
