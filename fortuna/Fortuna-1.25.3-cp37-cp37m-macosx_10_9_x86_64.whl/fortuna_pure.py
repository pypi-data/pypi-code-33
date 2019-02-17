import random
from time import time_ns
from statistics import mode, mean, StatisticsError


def get_impl():
    return "Fortuna Pure"


def analytic_continuation(func: staticmethod, num: int) -> int:
    if num < 0:
        return -func(-num)
    elif num == 0:
        return 0
    else:
        return func(num)


def random_range(lo: int, hi: int) -> int:
    if lo < hi:
        return random.randrange(lo, hi + 1)
    elif lo == hi:
        return lo
    else:
        return random_range(hi, lo)


def random_float() -> float:
    return random.random()


def random_below(num: int) -> int:
    if num > 0:
        return random.randrange(0, num)
    else:
        return analytic_continuation(random_below, num)


def d(sides: int) -> int:
    if sides > 0:
        return random_range(1, sides)
    else:
        return analytic_continuation(d, sides)


def dice(rolls: int, sides: int) -> int:
    if rolls > 0:
        total = 0
        for _ in range(rolls):
            total += d(sides)
        return total
    elif rolls == 0:
        return 0
    else:
        return -dice(-rolls, sides)


def min_max(num: int, lo: int, hi: int) -> int:
    return min(max(num, lo), hi)


def percent_true(num: int = 50) -> bool:
    return d(100) <= num


def percent_true_float(num: float = 50.0) -> bool:
    return random_below(100) + random_float() <= num


def plus_or_minus(num: int) -> int:
    return random_range(-num, num)


def plus_or_minus_linear(num: int) -> int:
    n = abs(num)
    return dice(2, n + 1) - (n + 2)


def stretched_bell(num: int) -> int:
    pi = 3.14159265359
    return round(random.gauss(0.0, num / pi))


def plus_or_minus_curve(num: int) -> int:
    n = abs(num)
    result = stretched_bell(n)
    while result < -n or result > n:
        result = stretched_bell(n)
    return result


def zero_flat(num: int) -> int:
    return random_range(0, num)


def zero_cool(num: int) -> int:
    if num > 0:
        result = plus_or_minus_linear(num)
        while result < 0:
            result = plus_or_minus_linear(num)
        return result
    else:
        return analytic_continuation(zero_cool, num)


def zero_extreme(num: int) -> int:
    if num > 0:
        result = plus_or_minus_curve(num)
        while result < 0:
            result = plus_or_minus_curve(num)
        return result
    else:
        return analytic_continuation(zero_extreme, num)

    
def max_cool(num: int) -> int:
    if num > 0:
        return num - zero_cool(num)
    else:
        return analytic_continuation(max_cool, num)


def max_extreme(num: int) -> int:
    if num > 0:
        return num - zero_extreme(num)
    else:
        return analytic_continuation(max_extreme, num)


def mostly_middle(num: int) -> int:
    if num > 0:
        mid_point = num // 2
        if num % 2 == 0:
            return plus_or_minus_linear(mid_point) + mid_point
        elif percent_true(50):
            return max_cool(mid_point)
        else:
            return 1 + zero_cool(mid_point) + mid_point
    else:
        return analytic_continuation(mostly_middle, num)


def mostly_center(num: int) -> int:
    if num > 0:
        mid_point = num // 2
        if num % 2 == 0:
            return plus_or_minus_curve(mid_point) + mid_point
        elif percent_true(50):
            return max_extreme(mid_point)
        else:
            return 1 + zero_extreme(mid_point) + mid_point
    else:
        return analytic_continuation(mostly_center, num)


def half_the_zeros(func: staticmethod, *arg, **kwargs):
    if percent_true(50):
        return func(*arg, **kwargs)
    t = 0
    while t == 0:
        t = func(*arg, **kwargs)
    return t


def plus_or_minus_linear_down(num: int) -> int:
    if num == 0:
        return 0
    num = abs(num)
    if percent_true(50):
        return half_the_zeros(max_cool, num)
    else:
        return half_the_zeros(max_cool, -num)


def plus_or_minus_curve_down(num: int) -> int:
    if num == 0:
        return 0
    num = abs(num)
    if percent_true(50):
        return half_the_zeros(max_extreme, num)
    else:
        return half_the_zeros(max_extreme, -num)


def mostly_not_middle(num: int) -> int:
    if num > 0:
        mid_point = num // 2
        if num % 2 == 0:
            return plus_or_minus_linear_down(mid_point) + mid_point
        elif percent_true(50):
            return zero_cool(mid_point)
        else:
            return 1 + max_cool(mid_point) + mid_point
    else:
        return analytic_continuation(mostly_not_middle, num)


def mostly_not_center(num: int) -> int:
    if num > 0:
        mid_point = num // 2
        if num % 2 == 0:
            return plus_or_minus_curve_down(mid_point) + mid_point
        elif percent_true(50):
            return zero_extreme(mid_point)
        else:
            return 1 + max_extreme(mid_point) + mid_point
    else:
        return analytic_continuation(mostly_not_center, num)


def random_value(arr):
    return arr[random_below(len(arr))]


def pop_random_value(arr):
    return arr.pop(random_below(len(arr)))


def cumulative_weighted_choice(table):
    max_weight = table[-1][0]
    rand = random_below(max_weight)
    for weight, value in table:
        if weight > rand:
            return value


def flatten(itm, flat: bool = True):
    if flat is False or not callable(itm):
        return itm
    else:
        try:
            return flatten(itm())
        except TypeError:
            return itm


def shuffle(arr: list):
    size = len(arr)
    for i in range(1, size):
        j = zero_flat(i)
        arr[i], arr[j] = arr[j], arr[i]


class TruffleShuffle:
    __slots__ = ("data", "flat", "half_len")

    def __init__(self, arr, flat=True):
        self.data = list(arr)
        arr_len = len(self.data)
        assert arr_len is not 0, "Input Error, Empty Container"
        self.flat = flat
        self.half_len = arr_len // 2
        shuffle(self.data)

    def __call__(self):
        return flatten(self.beta_rotate(), self.flat)

    def __repr__(self):
        return f"TruffleShuffle({self.data}, flat={self.flat})"

    def beta_rotate(self):
        result = self.data.pop()
        self.data.insert(zero_flat(self.half_len), result)
        return result


class QuantumMonty:
    __slots__ = ("arr", "flat", "data", "max_id", "truffle_shuffle")

    def __init__(self, arr, flat=True):
        self.arr = arr
        self.flat = flat
        self.data = tuple(arr)
        self.max_id = len(self.data) - 1
        self.truffle_shuffle = TruffleShuffle(self.data, flat)

    def __call__(self):
        return self.quantum_monty()

    def __repr__(self):
        return f"QuantumMonty({self.arr}, flat={self.flat})"

    def dispatch(self, quantum_bias="monty"):
        return {
            "monty": self.quantum_monty,
            "cycle": self.truffle_shuffle,
            "front": self.mostly_front,
            "middle": self.mostly_middle,
            "back": self.mostly_back,
            "first": self.mostly_first,
            "center": self.mostly_center,
            "last": self.mostly_last,
            "flat": self.mostly_flat,
            "not_middle": self.mostly_not_middle,
            "not_center": self.mostly_not_center,
            "not_monty": self.quantum_not_monty,
        }[quantum_bias]

    def quantum_monty(self):
        return flatten(random_value((
            self.mostly_front,
            self.mostly_middle,
            self.mostly_back,
            self.mostly_first,
            self.mostly_center,
            self.mostly_last,
        )), self.flat)

    def quantum_not_monty(self):
        return flatten(random_value((
            self.mostly_front,
            self.mostly_not_middle,
            self.mostly_back,
            self.mostly_first,
            self.mostly_not_center,
            self.mostly_last,
        )), self.flat)

    def mostly_flat(self):
        return flatten(random_value(self.data), self.flat)

    def mostly_cycle(self):
        return self.truffle_shuffle()

    def mostly_front(self):
        return flatten(self.data[zero_cool(self.max_id)], self.flat)

    def mostly_back(self):
        return flatten(self.data[max_cool(self.max_id)], self.flat)

    def mostly_middle(self):
        return flatten(self.data[mostly_middle(self.max_id)], self.flat)

    def mostly_first(self):
        return flatten(self.data[zero_extreme(self.max_id)], self.flat)

    def mostly_last(self):
        return flatten(self.data[max_extreme(self.max_id)], self.flat)

    def mostly_center(self):
        return flatten(self.data[mostly_center(self.max_id)], self.flat)

    def mostly_not_center(self):
        return flatten(self.data[mostly_not_center(self.max_id)], self.flat)

    def mostly_not_middle(self):
        return flatten(self.data[mostly_not_middle(self.max_id)], self.flat)


class FlexCat:
    __slots__ = ("flat", "x_bias", "y_bias", "data", "random_cat", "random_selection")

    def __init__(self, data, y_bias="front", x_bias="cycle", flat=True):
        self.flat = flat
        self.y_bias = y_bias
        self.x_bias = x_bias
        self.data = data
        self.random_cat = QuantumMonty(tuple(data.keys())).dispatch(y_bias)
        self.random_selection = {
            key: QuantumMonty(sequence, flat).dispatch(x_bias) for key, sequence in data.items()
        }

    def __call__(self, cat_key=None):
        return self.random_selection[cat_key if cat_key else self.random_cat()]()

    def __repr__(self):
        return f"FlexCat({self.data}, y_bias='{self.y_bias}', x_bias='{self.x_bias}', flat={self.flat})"


class RelativeWeightedChoice:
    __slots__ = ("weighted_table", "flat", "max_weight", "data")

    def __init__(self, weighted_table, flat=True):
        self.weighted_table = weighted_table
        self.flat = flat
        optimized_data = sorted([list(itm) for itm in weighted_table], key=lambda x: x[0], reverse=True)
        cum_weight = 0
        for w_pair in optimized_data:
            cum_weight += w_pair[0]
            w_pair[0] = cum_weight
        self.max_weight = optimized_data[-1][0]
        self.data = tuple(tuple(itm) for itm in optimized_data)

    def __call__(self):
        return flatten(self.weighted_choice(), self.flat)

    def __repr__(self):
        return f"RelativeWeightedChoice({self.weighted_table}, flat={self.flat})"

    def weighted_choice(self):
        rand = random_below(self.max_weight)
        for weight, value in self.data:
            if weight > rand:
                return value


class CumulativeWeightedChoice:
    __slots__ = ("weighted_table", "flat", "max_weight", "data")

    def __init__(self, weighted_table, flat=True):
        self.weighted_table = weighted_table
        self.flat = flat
        data = sorted([list(itm) for itm in weighted_table], key=lambda x: x[0])
        prev_weight = 0
        for w_pair in data:
            w_pair[0], prev_weight = w_pair[0] - prev_weight, w_pair[0]
        optimized_data = sorted(data, key=lambda x: x[0], reverse=True)
        cum_weight = 0
        for w_pair in optimized_data:
            cum_weight += w_pair[0]
            w_pair[0] = cum_weight
        self.max_weight = optimized_data[-1][0]
        self.data = tuple(tuple(itm) for itm in optimized_data)

    def __call__(self):
        return flatten(self.weighted_choice(), self.flat)

    def __repr__(self):
        return f"CumulativeWeightedChoice({self.weighted_table}, flat={self.flat})"

    def weighted_choice(self):
        rand = random_below(self.max_weight)
        for weight, value in self.data:
            if weight > rand:
                return value


def timer(func: staticmethod, *args, **kwargs):
    def if_mode(arr):
        try:
            return mode(arr)
        except StatisticsError:
            return False
    tl = []
    outer_cycles = 32
    inner_cycles = 32
    for _ in range(outer_cycles):
        start = time_ns()
        for _ in range(inner_cycles):
            func(*args, **kwargs)
        end = time_ns()
        tl.append((end - start) // inner_cycles)
    output = (
        f"Min: {min(tl)}ns",
        f"Mode: {str(if_mode(tl)) + 'ns' if if_mode(tl) else 'N/A'}",
        f"Mean: {int(mean(tl))}ns",
        f"Max: {max(tl)}ns",
    )
    print("Time: " + ", ".join(output))


def distribution(func: staticmethod, *args, **kwargs):
    num_cycles = 10000
    results = [func(*args, **kwargs) for _ in range(num_cycles)]
    if type(results[0]) is list:
        for i, _ in enumerate(results):
            results[i] = results[i][0]
    unique_results = list(set(results))
    if all([hasattr(x, "__lt__") for x in unique_results]):
        unique_results.sort()
    result_obj = {
        key: f"{results.count(key) / (num_cycles / 100)}%" for key in unique_results
    }
    for key, val in result_obj.items():
        print(f" {key}: {val}")


def distribution_timer(func: staticmethod, *args, **kwargs):
    timer(func, *args, **kwargs)
    distribution(func, *args, **kwargs)
    print("")
