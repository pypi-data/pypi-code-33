from datetime import datetime
import random


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
        return sum(d(sides) for _ in range(rolls))
    elif rolls == 0:
        return 0
    else:
        return -dice(-rolls, sides)


def min_max(num: int, lo: int, hi: int) -> int:
    return min(max(num, lo), hi)


def percent_true(num: int = 50) -> bool:
    return d(100) <= num


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


def n_samples(func: staticmethod, *args, n=10, **kwargs):
    return [func(*args, **kwargs) for _ in range(n)]


def bind(func: staticmethod, *args, **kwargs):
    return lambda: func(*args, **kwargs)


def shuffle(arr: list):
    size = len(arr)
    for i in range(1, size):
        j = zero_flat(i)
        arr[i], arr[j] = arr[j], arr[i]


class TruffleShuffle:
    __slots__ = ("flat", "data", "first_block")

    def __init__(self, arr, flat=True):
        assert len(arr) is not 0, "Input Error, Empty Container"
        self.flat = flat
        self.data = list(arr)
        shuffle(self.data)
        self.first_block = list(reversed(self.data))

    def __call__(self):
        if self.first_block:
            return flatten(self.first_block.pop(), self.flat)
        else:
            return flatten(self.beta_swap(self.data), self.flat)

    @staticmethod
    def alpha_swap(arr: list):
        """ linear front to linear back """
        max_idx = len(arr) - 1
        result, target = zero_cool(max_idx), max_cool(max_idx)
        arr[result], arr[target] = arr[target], arr[result]
        return arr[target]

    @staticmethod
    def beta_swap(arr: list):
        """ gauss front to gauss back """
        max_idx = len(arr) - 1
        result, target = zero_extreme(max_idx), max_extreme(max_idx)
        arr[result], arr[target] = arr[target], arr[result]
        return arr[target]

    @staticmethod
    def gamma_swap(arr: list):
        """ gauss inside-out swap """
        max_idx = len(arr) - 1
        result, target = mostly_center(max_idx), zero_extreme(max_idx) if percent_true(50) else max_extreme(max_idx)
        arr[result], arr[target] = arr[target], arr[result]
        return arr[target]


class QuantumMonty:
    __slots__ = ("flat", "data", "max_id", "truffle_shuffle")

    def __init__(self, data, flat=True):
        self.flat = flat
        self.data = tuple(data)
        self.max_id = len(data) - 1
        self.truffle_shuffle = TruffleShuffle(data, flat)

    def __call__(self):
        return self.quantum_monty()

    def dispatch(self, quantum_bias="monty"):
        return {
            "monty": self.quantum_monty,
            "cycle": self.mostly_cycle,
            "front": self.mostly_front,
            "middle": self.mostly_middle,
            "back": self.mostly_back,
            "first": self.mostly_first,
            "center": self.mostly_center,
            "last": self.mostly_last,
            "flat": self.mostly_flat,
        }[quantum_bias]

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

    def quantum_monty(self):
        monty_methods = (
            self.mostly_front,
            self.mostly_middle,
            self.mostly_back,
            self.mostly_first,
            self.mostly_center,
            self.mostly_last,
        )
        return random_value(monty_methods)()


class FlexCat:
    __slots__ = ("cat_keys", "random_cat", "random_selection")

    def __init__(self, data, y_bias="front", x_bias="cycle", flat=True):
        self.cat_keys = tuple(data.keys())
        self.random_cat = QuantumMonty(self.cat_keys).dispatch(y_bias)
        self.random_selection = {
            key: QuantumMonty(sequence, flat).dispatch(x_bias) for key, sequence in data.items()
        }

    def __call__(self, cat_key=None):
        return self.random_selection[cat_key if cat_key else self.random_cat()]()


class RelativeWeightedChoice:
    __slots__ = ("flat", "max_weight", "data")

    def __init__(self, weighted_table, flat=True):
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

    def weighted_choice(self):
        rand = random_below(self.max_weight)
        for weight, value in self.data:
            if weight > rand:
                return value


class CumulativeWeightedChoice:
    __slots__ = ("flat", "max_weight", "data")

    def __init__(self, weighted_table, flat=True):
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

    def weighted_choice(self):
        rand = random_below(self.max_weight)
        for weight, value in self.data:
            if weight > rand:
                return value


class RandomWalk:
    __slots__ = ("flat", "data", "len_data", "idx")

    def __init__(self, arr, flat=True):
        self.flat = flat
        self.data = arr
        self.len_data = len(self.data)
        self.idx = random_below(self.len_data)

    def __call__(self):
        modifier = 1 if percent_true(50) else -1
        self.idx = (self.idx + modifier) % self.len_data
        return flatten(self.data[self.idx], self.flat)


class CatWalk:
    __slots__ = ("flat", "data", "len_x", "len_y", "x_idx", "y_idx")

    def __init__(self, table, flat=True):
        self.flat = flat
        self.data = table
        self.len_x = max(len(itm) for itm in self.data)
        self.len_y = len(self.data)
        assert min(len(itm) for itm in self.data) == self.len_x, "All sequences in a CatWalk must be of equal length."
        self.x_idx = random_below(self.len_x)
        self.y_idx = random_below(self.len_y)

    def __call__(self):
        x_mod = 1 if percent_true(50) else -1
        y_mod = 1 if percent_true(50) else -1
        if percent_true(50):
            self.x_idx = (self.x_idx + x_mod) % self.len_x
            self.y_idx = (self.y_idx + y_mod) % self.len_y
        elif percent_true(50):
            self.x_idx = (self.x_idx + x_mod) % self.len_x
        else:
            self.y_idx = (self.y_idx + y_mod) % self.len_y
        return flatten(self.data[self.y_idx][self.x_idx], self.flat)


def distribution_timer(func: staticmethod, *args, call_sig=None, num_cycles=10000, **kwargs):
    if call_sig is None:
        if hasattr(func, "__qualname__"):
            call_sig = f"{func.__qualname__}{f'({args[0]})' if len(args) == 1 else args}"
        else:
            call_sig = f"func(*args, **kwargs)"
    start_time = datetime.now()
    results = n_samples(func, *args, n=num_cycles, **kwargs)
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    total_time_ms = round(total_time * 1000.0, 2)
    average_time_nano = round((total_time_ms / num_cycles) * 1000000)
    print(f"{call_sig} x {num_cycles}: Total time: {total_time_ms} ms, Average time: {average_time_nano} nano")
    if type(results[0]) is list:
        for i, _ in enumerate(results):
            results[i] = results[i][0]
    unique_results = list(set(results))
    if all([not callable(x) for x in unique_results]):
        unique_results.sort()
    result_obj = {
        key: f"{results.count(key) / (num_cycles / 100)}%" for key in unique_results
    }
    for key, val in result_obj.items():
        print(f" {key}: {val}")
    print("")
