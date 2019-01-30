from typing import Callable, List, Tuple
import math

from intervallum.interval import Interval, IntervalExceptions
from intervallum.interval import reduce_result, monotonic


def _get_points_for_trig(left: float, right: float) -> List[float]:
    c = 0.5 * math.pi
    left_bound = int(math.ceil(left / c))
    right_bound = int(math.floor(right / c))
    return [left, right] + list(map(lambda v: c * v, range(left_bound, right_bound + 1)))


@reduce_result
@monotonic
def sin(i: "Interval") -> Tuple[Callable[[float], float], List[float]]:
    if i.width >= 2 * math.pi:
        return lambda x: x, [-1.0, 1.0]
    else:
        return lambda x: math.sin(x), _get_points_for_trig(i.lb, i.ub)


@reduce_result
@monotonic
def cos(i: "Interval") -> Tuple[Callable[[float], float], List[float]]:
    if i.width >= 2 * math.pi:
        return lambda x: x, [-1.0, 1.0]
    else:
        return lambda x: math.cos(x), _get_points_for_trig(i.lb, i.ub)


@reduce_result
@monotonic
def abs(i: "Interval") -> Tuple[Callable[[float], float], List[float]]:
    points = [i.lb, i.ub]
    if i.lb * i.ub < 0:
        points.append(0.0)
    return lambda x: math.fabs(x), points


@reduce_result
@monotonic
def exp(i: "Interval") -> Tuple[Callable[[float], float], List[float]]:
    return lambda x: math.exp(x), [i.lb, i.ub]


@reduce_result
@monotonic
def sqrt(i: "Interval") -> Tuple[Callable[[float], float], List[float]]:
    def f(x): return math.sqrt(x)
    if i.ub < 0.0:
        raise IntervalExceptions.OperationIsNotDefined("sqrt", i)
    elif i.lb < 0.0:
        return f, [0.0, i.ub]
    else:
        return f, [i.lb, i.ub]


@reduce_result
@monotonic
def log(i: "Interval") -> Tuple[Callable[[float], float], List[float]]:
    def f(x): return math.log(x) if x != 0.0 else -math.inf
    if i.ub <= 0.0:
        raise IntervalExceptions.OperationIsNotDefined("log", i)
    elif i.lb < 0.0:
        return f, [0.0, i.ub]
    else:
        return f, [i.lb, i.ub]
