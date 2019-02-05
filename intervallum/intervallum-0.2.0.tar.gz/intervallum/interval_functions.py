from typing import Callable, List, Tuple
import math
from itertools import accumulate

from intervallum.interval import Interval, IntervalNumber, IntervalExceptions, IntervalConstants
from intervallum.interval import reduce_result, monotonic


def _get_points_for_trig(left: float, right: float) -> List[float]:
    c = 0.5 * math.pi
    left_bound = int(math.ceil(left / c))
    right_bound = int(math.floor(right / c))
    return [left, right] + list(map(lambda v: c * v, range(left_bound, right_bound + 1)))


@reduce_result
@monotonic
def sin(i: IntervalNumber) -> Tuple[Callable[[float], float], List[float]]:
    if isinstance(i, float):
        return lambda x: math.sin(x), [i]
    elif i.width >= 2 * math.pi:
        return lambda x: x, [-1.0, 1.0]
    else:
        return lambda x: math.sin(x), _get_points_for_trig(i.lb, i.ub)


@reduce_result
@monotonic
def cos(i: IntervalNumber) -> Tuple[Callable[[float], float], List[float]]:
    if isinstance(i, float):
        return lambda x: math.cos(x), [i]
    elif i.width >= 2 * math.pi:
        return lambda x: x, [-1.0, 1.0]
    else:
        return lambda x: math.cos(x), _get_points_for_trig(i.lb, i.ub)


@reduce_result
@monotonic
def abs(i: IntervalNumber) -> Tuple[Callable[[float], float], List[float]]:
    if isinstance(i, float):
        return lambda x: math.fabs(x), [i]
    points = [i.lb, i.ub]
    if i.lb * i.ub < 0:
        points.append(0.0)
    return lambda x: math.fabs(x), points


@reduce_result
@monotonic
def exp(i: IntervalNumber) -> Tuple[Callable[[float], float], List[float]]:
    if isinstance(i, float):
        return lambda x: math.exp(x), [i]
    else:
        return lambda x: math.exp(x), [i.lb, i.ub]


@reduce_result
@monotonic
def sqrt(i: IntervalNumber) -> Tuple[Callable[[float], float], List[float]]:
    def f(x): return math.sqrt(x)
    if isinstance(i, float):
        return f, [i]
    elif i.ub < 0.0:
        raise IntervalExceptions.OperationIsNotDefined("sqrt", i)
    elif i.lb < 0.0:
        return f, [0.0, i.ub]
    else:
        return f, [i.lb, i.ub]


@reduce_result
@monotonic
def log(i: IntervalNumber) -> Tuple[Callable[[float], float], List[float]]:
    def f(x): return math.log(x) if x != 0.0 else -math.inf
    if isinstance(i, float):
        return f, [i]
    elif i.ub <= 0.0:
        raise IntervalExceptions.OperationIsNotDefined("log", i)
    elif i.lb < 0.0:
        return f, [0.0, i.ub]
    else:
        return f, [i.lb, i.ub]


def split(i: IntervalNumber, ratios: List[float]) -> List[IntervalNumber]:
    if isinstance(i, Interval):
        ratio_sum = sum(ratios)
        w = i.width
        intervals = []
        cum_sums = list(accumulate([0.0] + ratios))
        for r1, r2 in zip(cum_sums[:-1], cum_sums[1:]):
            i = Interval(i.lb + r1 * w / ratio_sum, i.lb + r2 * w / ratio_sum)
            intervals.append(i._try_to_reduce() if IntervalConstants._reduce_intervals_to_numbers else i)
        return intervals
    else:
        return [i] * len(ratios)


def bisect(i: IntervalNumber) -> List[IntervalNumber]:
    return split(i, [1.0, 1.0])
