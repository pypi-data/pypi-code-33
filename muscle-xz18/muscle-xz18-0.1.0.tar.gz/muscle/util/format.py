def num_to_ordinal(num):
    """
    Convert an integer number to an ordinal.

    :param num: the integer number to be converted
    :return: an ordinal number as a string
    """
    if num <= 0:
        return str(num)

    if num % 100 in [11, 12, 13]:
        return str(num) + "th"

    switch = {
        1: str(num) + "st",
        2: str(num) + "nd",
        3: str(num) + "rd"
    }

    try:
        return switch[num % 10]
    except KeyError:
        return str(num) + "th"
