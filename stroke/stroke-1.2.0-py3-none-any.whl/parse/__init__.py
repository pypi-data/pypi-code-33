import functools

from . import abstract


__all__ = ('clause', 'flag', 'group', 'split')


escape = '\\'


start = '('


stop = ')'


def seek(values, escape = escape, start = start, stop = stop):

    return abstract.seek(escape, start, stop, values)


def clause(values, escape = escape, start = start, seek = seek):

    """
    Yield clauses.
    Every second clause is an inner clause.
    """

    return abstract.clause(escape, start, seek, values)


def flag(value, *keys, escape = escape):

    """
    Differenciate values according to keywords.
    """

    return abstract.flag(escape, value, keys)


def group(values, *keys, flag = flag):

    """
    Group key-value pairs by the key.
    """

    initial, *extras = flag(values, *keys)

    junk, initial = initial

    store = {key: [] for key in keys}

    for (key, value) in extras:

        store[key].append(value)

    (keys, values) = zip(*store.items())

    return (initial, *values)


def split(values, key, clean = True, group = group):

    """
    Separate and clean flags by the key.
    """

    value, values = group(values, key)

    values.insert(0, value)

    return values


def clean(values, strip = True, empty = False):

    """
    Strip ends and selectively yield and values.
    """

    for value in values:

        if strip:

            value = value.strip()

        if not value or empty:

            continue

        yield value
