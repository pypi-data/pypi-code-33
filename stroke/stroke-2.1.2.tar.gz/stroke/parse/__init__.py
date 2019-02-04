
from . import abstract


__all__ = ('flag', 'group', 'split')


escape = '\\'


def strip(value, escape = escape, full = True, ghost = 1):

    if full:

        value = value.strip()

    revert = len(escape)

    for index in range(ghost):

        if value.startswith(escape):

            value = value[revert:]

        if value.endswith(escape):

            value = value[:-revert]

    return value


def clean(values, strip = strip, empty = True):

    """
    Strip ends and selectively yield and values.
    """

    for value in values:

        value = strip(value)

        if not value and empty:

            continue

        yield value


def flag(values, *keys, escape = escape):

    """
    Differenciate values according to keywords.
    """

    return abstract.flag(escape, values, keys)


def group(values, *keys, flag = flag):

    """
    Group key-value pairs by the key.
    """

    initial, *extras = flag(values, *keys)

    junk, initial = initial

    store = {key: [] for key in keys}

    for (key, value) in extras:

        store[key].append(value)

    keys, values = zip(*store.items())

    return (initial, *values)


def split(values, key, group = group):

    """
    Separate flags by the key.
    """

    value, values = group(values, key)

    values.insert(0, value)

    return values
