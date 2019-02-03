from Fortuna import *
# from fortuna_extras.fortuna_pure import *

from datetime import datetime
import random  # Base Cases


def tests(label: str):
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
    distribution_timer(random.random, call_sig="Base Case:\nrandom.random()", dist=False)
    distribution_timer(random_float, dist=False)
    distribution_timer(d, 10)
    distribution_timer(dice, 3, 6)
    distribution_timer(plus_or_minus, 5)
    distribution_timer(plus_or_minus_linear, 5)
    distribution_timer(plus_or_minus_curve, 5)
    distribution_timer(plus_or_minus_linear_down, 5)
    distribution_timer(plus_or_minus_curve_down, 5)
    distribution_timer(stretched_bell, 5)
    distribution_timer(zero_flat, 10)
    distribution_timer(zero_cool, 10)
    distribution_timer(zero_extreme, 10)
    distribution_timer(max_cool, 10)
    distribution_timer(max_extreme, 10)
    distribution_timer(mostly_middle, 10)
    distribution_timer(mostly_center, 10)
    distribution_timer(mostly_not_middle, 10)
    distribution_timer(mostly_not_center, 10)

    print("\nRandom Truth")
    print(f"{'-' * 73}\n")
    distribution_timer(percent_true, 25)
    distribution_timer(percent_true_float, 33.33333)

    print("\nRandom Values from a Sequence")
    print(f"{'-' * 73}\n")
    some_list = ["Alpha", "Beta", "Delta", "Eta", "Gamma", "Kappa", "Zeta"]
    print(f"some_list = {some_list}\n")
    distribution_timer(random.choice, some_list, call_sig="Base Case:\nrandom.choice(some_list)")
    distribution_timer(random_value, some_list, call_sig="random_value(some_list)")

    monty = QuantumMonty(some_list)
    print("monty = QuantumMonty(some_list)\n")
    distribution_timer(monty.mostly_flat)
    distribution_timer(monty.mostly_middle, call_sig="monty.mostly_middle()")
    distribution_timer(monty.mostly_center, call_sig="monty.mostly_center()")
    distribution_timer(monty.mostly_front, call_sig="monty.mostly_front()")
    distribution_timer(monty.mostly_back, call_sig="monty.mostly_back()")
    distribution_timer(monty.mostly_first, call_sig="monty.mostly_first()")
    distribution_timer(monty.mostly_last, call_sig="monty.mostly_last()")
    distribution_timer(monty.quantum_monty, call_sig="monty.quantum_monty()")
    distribution_timer(monty.mostly_cycle, call_sig="monty.mostly_cycle()")
    distribution_timer(monty.mostly_not_middle, call_sig="monty.mostly_not_middle()")
    distribution_timer(monty.mostly_not_center, call_sig="monty.mostly_not_center()")

    truffle_shuffle = TruffleShuffle(some_list)
    print("truffle_shuffle = TruffleShuffle(some_list)\n")
    distribution_timer(truffle_shuffle, call_sig="truffle_shuffle()")

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
        random.choices, population, weights=rel_weights,
        call_sig="Relative Base Case:\nrandom.choices(population, weights=rel_weights)"
    )
    cumulative_table = list(zip(cum_weights, population))
    print("cumulative_table = list(zip(cum_weights, population))\n")
    distribution_timer(
        cumulative_weighted_choice, cumulative_table,
        call_sig="Fortuna.cumulative_weighted_choice(cumulative_table)"
    )
    cumulative_choice = CumulativeWeightedChoice(cumulative_table)
    print("cumulative_choice = CumulativeWeightedChoice(cumulative_table)\n")
    distribution_timer(cumulative_choice, call_sig="cumulative_choice()")

    relative_table = list(zip(rel_weights, population))
    print("relative_table = list(zip(rel_weights, population))")
    relative_choice = RelativeWeightedChoice(relative_table)
    print("relative_choice = RelativeWeightedChoice(relative_table)\n")
    distribution_timer(relative_choice, call_sig="relative_choice()")

    print("\nRandom Values by Category")
    print(f"{'-' * 73}\n")
    flex_cat = FlexCat({
        'Cat_A': ('A1', 'A2', 'A3'),
        'Cat_B': ('B1', 'B2', 'B3'),
        'Cat_C': ('C1', 'C2', 'C3'),
    }, y_bias='front', x_bias='cycle')
    print("flex_cat = FlexCat({"
          "\n\t'Cat_A': ('A1', 'A2', 'A3'),"
          "\n\t'Cat_B': ('B1', 'B2', 'B3'),"
          "\n\t'Cat_C': ('C1', 'C2', 'C3'),"
          "\n}, y_bias='front', x_bias='cycle')\n")
    distribution_timer(flex_cat, 'Cat_A', call_sig=f"flex_cat('Cat_A')")
    distribution_timer(flex_cat, 'Cat_B', call_sig=f"flex_cat('Cat_B')")
    distribution_timer(flex_cat, 'Cat_C', call_sig=f"flex_cat('Cat_C')")
    distribution_timer(flex_cat, call_sig="flex_cat()")

    print("\nRandom Walks")
    print(f"{'-' * 73}\n")
    walk_list = ["Alpha", "Beta", "Delta", "Eta", "Gamma", "Kappa", "Zeta"]
    print(f"walk_list = {walk_list}")
    random_walk = RandomWalk(walk_list)
    print("random_walk = RandomWalk(walk_list)\n")
    distribution_timer(random_walk, call_sig="random_walk()")

    catwalk_table = [
        (10, 11, 12, 13, 14),
        (20, 21, 22, 23, 24),
        (30, 31, 32, 33, 34),
    ]
    print(f"catwalk_table = {catwalk_table}")
    catwalk = CatWalk(catwalk_table)
    print("catwalk = CatWalk(catwalk_table)\n")
    distribution_timer(catwalk, call_sig="catwalk()")

    print("\nList Shuffle")
    print(f"{'-' * 73}\n")
    some_list = ["Alpha", "Beta", "Delta", "Eta", "Gamma", "Kappa", "Zeta"]
    print(f"some_list = {some_list}\n")
    distribution_timer(random.shuffle, some_list, call_sig="Base Case:\nrandom.shuffle(some_list)")
    distribution_timer(shuffle, some_list, call_sig="Fortuna.shuffle(some_list)")

    print(f"\n{'-' * 73}")
    total_test_time = round((datetime.now() - t0).total_seconds(), 2)
    print(f"Total Test Time: {total_test_time} sec\n")


if __name__ == "__main__":
    tests("Fortuna 1.23.5.1 Sample Distribution and Performance Test Suite")
