import random
from datetime import datetime


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


def plus_or_minus_curve(num: int, bounded: bool = True) -> int:
    def stretched_bell(x):
        pi = 3.14159265359
        return round(random.gauss(0.0, x / pi))
    n = abs(num)
    result = stretched_bell(n)
    while bounded and (result < -n or result > n):
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


def flatten(itm):
    if not callable(itm):
        return itm
    else:
        try:
            return flatten(itm())
        except TypeError:
            return itm


def n_samples(func: staticmethod, *args, n=10, **kwargs):
    return [func(*args, **kwargs) for _ in range(n)]


def n_samples_flat(func: staticmethod, *args, n=10, **kwargs):
    return [flatten(func(*args, **kwargs)) for _ in range(n)]


def bind(func: staticmethod, *args, **kwargs):
    return lambda: func(*args, **kwargs)


class RandomCycle:

    def __init__(self, arr, flat_map=True):
        self.arr = arr
        self.flat_map = flat_map
        self.size = len(arr)
        assert self.size >= 3, f"Input Error, sequence length must be >= 3."
        self.data = list(arr)
        random.shuffle(self.data)
        self.next = self.data.pop()
        self.out_idx = len(self.data) - 1
        self.in_idx = len(self.data) - 2

    def __call__(self):
        result = self.next
        self.next = self.data.pop(max_extreme(self.out_idx))
        self.data.insert(zero_extreme(self.in_idx), result)
        return flatten(result) if self.flat_map else result

    def __repr__(self):
        return f"RandomCycle({self.arr})"


class BlockCycle:

    def __init__(self, arr, flat_map=True):
        self.arr = arr
        self.flat_map = flat_map
        assert len(arr) >= 3, f"Input Error, sequence length must be >= 3."
        self.data = list(arr)
        random.shuffle(self.data)
        self.next = pop_random_value(self.data)

    def __call__(self):
        result = self.next
        while result is self.next:
            self.next = pop_random_value(self.data)
        if len(self.data) < 1:
            self.data = list(self.arr)
            random.shuffle(self.data)
        return flatten(result) if self.flat_map else result

    def __repr__(self):
        return f"BlockCycle({self.arr})"


class QuantumMonty:

    def __init__(self, data, flat_map=True):
        self.flat_map = flat_map
        self.data = tuple(data)
        self.max_id = len(data) - 1
        self.random_cycle = RandomCycle(data, flat_map)

    def flatten(self, itm):
        return flatten(itm) if self.flat_map else itm

    def __call__(self):
        return self.quantum_monty()

    def __repr__(self):
        return f"QuantumMonty({self.data})"

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
        return self.flatten(random_value(self.data))

    def mostly_cycle(self):
        return self.random_cycle()

    def mostly_front(self):
        return self.flatten(self.data[zero_cool(self.max_id)])

    def mostly_back(self):
        return self.flatten(self.data[max_cool(self.max_id)])

    def mostly_middle(self):
        return self.flatten(self.data[mostly_middle(self.max_id)])

    def mostly_first(self):
        return self.flatten(self.data[zero_extreme(self.max_id)])

    def mostly_last(self):
        return self.flatten(self.data[max_extreme(self.max_id)])

    def mostly_center(self):
        return self.flatten(self.data[mostly_center(self.max_id)])

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

    def __init__(self, data, y_bias="front", x_bias="cycle", flat_map=True):
        self.data = data
        self.y_bias = y_bias
        self.x_bias = x_bias
        self.flat_map = flat_map
        self.cat_keys = tuple(data.keys())
        self.random_cat = QuantumMonty(self.cat_keys).dispatch(y_bias)
        self.random_selection = {
            key: QuantumMonty(sequence, flat_map=flat_map).dispatch(x_bias) for key, sequence in data.items()
        }

    def __call__(self, cat_key=None):
        return self.random_selection[cat_key if cat_key else self.random_cat()]()

    def __repr__(self):
        return f"FlexCat({self.data}, y_bias='{self.y_bias}', x_bias='{self.x_bias}')"


class RelativeWeightedChoice:

    def __init__(self, weighted_table, flat_map=True):
        self.flat_map = flat_map
        self.weighted_table = weighted_table
        optimized_data = sorted([list(itm) for itm in weighted_table], key=lambda x: x[0], reverse=True)
        cum_weight = 0
        for w_pair in optimized_data:
            cum_weight += w_pair[0]
            w_pair[0] = cum_weight
        self.max_weight = optimized_data[-1][0]
        self.data = tuple(tuple(itm) for itm in optimized_data)

    def __call__(self):
        result = self.weighted_choice()
        return flatten(result) if self.flat_map else result

    def weighted_choice(self):
        rand = random_below(self.max_weight)
        for weight, value in self.data:
            if weight > rand:
                return value

    def __repr__(self):
        return f"RelativeWeightedChoice({self.weighted_table})"


class CumulativeWeightedChoice:

    def __init__(self, weighted_table, flat_map=True):
        self.flat_map = flat_map
        self.weighted_table = weighted_table
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
        result = self.weighted_choice()
        return flatten(result) if self.flat_map else result

    def weighted_choice(self):
        rand = random_below(self.max_weight)
        for weight, value in self.data:
            if weight > rand:
                return value

    def __repr__(self):
        return f"CumulativeWeightedChoice({self.weighted_table})"


class RandomWalk:

    def __init__(self, arr, flat_map=True):
        self.flat = flat_map
        self.data = arr
        self.len_data = len(self.data)
        assert self.len_data > 0, "RandomWalk requires a non-empty container."
        self.idx = random_below(self.len_data)

    def __call__(self):
        modifier = 1 if percent_true(50) else -1
        self.idx = (self.idx + modifier) % self.len_data
        result = self.data[self.idx]
        return flatten(result) if self.flat else result

    def __repr__(self):
        return f"RandomWalk({self.data})"


class CatWalk:

    def __init__(self, table, flat_map=True):
        self.flat = flat_map
        self.data = table
        self.len_x = max(len(itm) for itm in self.data)
        self.len_y = len(self.data)
        assert self.len_y > 0 and self.len_x > 0, "Containers in CatWalk must not be empty."
        assert min(len(itm) for itm in self.data) == self.len_x, "Containers in CatWalk must be of equal length."
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
        result = self.data[self.y_idx][self.x_idx]
        return flatten(result) if self.flat else result

    def __repr__(self):
        return f"CatWalk({self.data})"


def distribution_timer(func: staticmethod, *args, call_sig=None, num_cycles=100000, **kwargs):
    start_time = datetime.now()
    results = n_samples(func, *args, n=num_cycles, **kwargs)
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    if call_sig is None:
        if hasattr(func, "__qualname__"):
            call_sig = f"{func.__qualname__}{f'({args[0]})' if len(args) == 1 else args}"
        else:
            call_sig = f"f(x)"
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


def pure_tests(label: str):
    t0 = datetime.now()
    print()
    print(label)
    print()
    print("Random Numbers")
    print(f"{'-' * 73}\n")
    distribution_timer(random.randint, 1, 10, call_sig="Base Case:\nrandom.randint(1, 10)")
    distribution_timer(random_range, 1, 10)
    distribution_timer(random.randrange, 10, call_sig="Base Case:\nrandom.randrange(10)")
    distribution_timer(random_below, 10)
    distribution_timer(d, 10)
    distribution_timer(dice, 2, 6)
    distribution_timer(plus_or_minus, 5)
    distribution_timer(plus_or_minus_linear, 5)
    distribution_timer(plus_or_minus_curve, 5)
    distribution_timer(plus_or_minus_curve, 5, bounded=False, call_sig="plus_or_minus_curve(5, bounded=False)"),
    distribution_timer(zero_flat, 10)
    distribution_timer(zero_cool, 10)
    distribution_timer(zero_extreme, 10)
    distribution_timer(max_cool, 10)
    distribution_timer(max_extreme, 10)
    distribution_timer(mostly_middle, 10)
    distribution_timer(mostly_center, 10)

    print("\nRandom Truth")
    print(f"{'-' * 73}\n")
    distribution_timer(percent_true, 25)

    print("\nRandom Values from a Sequence")
    print(f"{'-' * 73}\n")
    some_list = ("Alpha", "Beta", "Delta", "Eta", "Gamma", "Kappa", "Zeta")
    print(f"some_list = {some_list}\n")
    distribution_timer(random.choice, some_list, call_sig="Base Case:\nrandom.choice(some_list)")
    distribution_timer(random_value, some_list, call_sig="random_value(some_list)")

    monty = QuantumMonty(some_list)
    print(f"monty = Fortuna.QuantumMonty(some_list)\n")
    distribution_timer(monty.mostly_flat, call_sig="monty.mostly_flat()")
    distribution_timer(monty.mostly_middle, call_sig="monty.mostly_middle()")
    distribution_timer(monty.mostly_center, call_sig="monty.mostly_center()")
    distribution_timer(monty.mostly_front, call_sig="monty.mostly_front()")
    distribution_timer(monty.mostly_back, call_sig="monty.mostly_back()")
    distribution_timer(monty.mostly_first, call_sig="monty.mostly_first()")
    distribution_timer(monty.mostly_last, call_sig="monty.mostly_last()")
    distribution_timer(monty.quantum_monty, call_sig="monty.quantum_monty()")
    distribution_timer(monty.mostly_cycle, call_sig="monty.mostly_cycle()")

    random_cycle = RandomCycle(some_list)
    print(f"random_cycle = Fortuna.RandomCycle(some_list)\n")
    distribution_timer(random_cycle, call_sig="random_cycle()")

    block_cycle = BlockCycle(some_list)
    print(f"block_cycle = Fortuna.BlockCycle(some_list)\n")
    distribution_timer(block_cycle, call_sig="block_cycle()")

    print("\nRandom Values by Weighted Table")
    print(f"{'-' * 73}\n")
    population = ("Apple", "Banana", "Cherry", "Grape", "Lime", "Orange")
    cum_weights = (7, 11, 13, 23, 26, 30)
    rel_weights = (7, 4, 2, 10, 3, 4)
    print(f"population = {population}")
    print(f"cum_weights = {cum_weights}")
    print(f"rel_weights = {rel_weights}\n")
    distribution_timer(
        random.choices, population, cum_weights=cum_weights,
        call_sig="Cumulative Base Case:\nrandom.choices(population, cum_weights=cum_weights)"
    )
    distribution_timer(
        random.choices, population, rel_weights,
        call_sig="Relative Base Case:\nrandom.choices(population, rel_weights)"
    )
    cumulative_table = [
        (7, "Apple"),
        (11, "Banana"),
        (13, "Cherry"),
        (23, "Grape"),
        (26, "Lime"),
        (30, "Orange"),
    ]
    print(f"cumulative_table = {cumulative_table}\n")
    distribution_timer(
        cumulative_weighted_choice, cumulative_table,
        call_sig="Fortuna.cumulative_weighted_choice(cumulative_table)"
    )
    cumulative_choice = CumulativeWeightedChoice(cumulative_table)
    print(f"cumulative_choice = CumulativeWeightedChoice(cumulative_table)\n")
    distribution_timer(cumulative_choice, call_sig="cumulative_choice()")

    relative_table = [
        (7, "Apple"),
        (4, "Banana"),
        (2, "Cherry"),
        (10, "Grape"),
        (3, "Lime"),
        (4, "Orange"),
    ]
    relative_choice = RelativeWeightedChoice(relative_table)
    print(f"relative_choice = RelativeWeightedChoice(relative_table)\n")
    distribution_timer(relative_choice, call_sig="relative_choice()")

    print("\nRandom Values by Category")
    print(f"{'-' * 73}\n")
    flex_cat = FlexCat(
        {
            'Cat_A': ('A1', 'A2', 'A3'),
            'Cat_B': ('B1', 'B2', 'B3'),
            'Cat_C': ('C1', 'C2', 'C3'),
        },
        y_bias='front', x_bias='cycle',
    )
    print(f"flex_cat = {flex_cat}\n")
    distribution_timer(flex_cat, 'Cat_A', call_sig=f"flex_cat('Cat_A')")
    distribution_timer(flex_cat, 'Cat_B', call_sig=f"flex_cat('Cat_B')")
    distribution_timer(flex_cat, 'Cat_C', call_sig=f"flex_cat('Cat_C')")
    distribution_timer(flex_cat, call_sig="flex_cat()")

    print("\nRandom Walks")
    print(f"{'-' * 73}\n")
    walk_list = ("Alpha", "Beta", "Delta", "Eta", "Gamma", "Kappa", "Zeta")
    random_walk = RandomWalk(walk_list)
    print(f"random_walk = Fortuna.RandomWalk({walk_list})\n")
    distribution_timer(random_walk, call_sig="random_walk()")

    catwalk_table = (
        (10, 11, 12, 13, 14, 15),
        (20, 21, 22, 23, 24, 25),
        (30, 31, 32, 33, 34, 35),
    )
    catwalk = CatWalk(catwalk_table)
    print(f"catwalk = {catwalk}\n")
    distribution_timer(catwalk, call_sig="catwalk()")

    print(f"\n{'-' * 73}")
    total_test_time = round((datetime.now() - t0).total_seconds(), 2)
    print(f"Total Test Time: {total_test_time} sec\n")


if __name__ == "__main__":
    pure_tests("Fortuna Pure 0.22.2 Sample Distribution and Performance Test Suite")
