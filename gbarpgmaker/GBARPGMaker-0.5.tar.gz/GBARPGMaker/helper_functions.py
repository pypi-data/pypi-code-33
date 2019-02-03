def get_lowest_option(x, options):
    options = list(reversed(sorted(options))) + [0, 8]
    for i, option in enumerate(options):
        if x > option:
            return options[i - 1]
    return 0


SHAPE_SIZE_DICTIONARY = {
        str([1, 1]): [0, 0],
        str([2, 1]): [1, 0],
        str([1, 2]): [2, 0],
        str([2, 2]): [0, 1],
        str([4, 1]): [1, 1],
        str([1, 4]): [2, 1],
        str([4, 4]): [0, 2],
        str([4, 2]): [1, 2],
        str([2, 4]): [2, 2],
        str([8, 8]): [0, 3],
        str([8, 4]): [1, 3],
        str([4, 8]): [1, 3],
}
