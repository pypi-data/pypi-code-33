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

    yield from abstract.clause(escape, start, seek, values)


def skip(value, escape = escape):

    check = value.startswith(escape)

    if check:

        value = value[len(escape):]

    return check, value


def flag(value, *keys, skip = skip, parse = tuple):

    """
    Differenciate values according to keywords.
    """

    entries = abstract.flag(skip, value, keys)

    keys, values = zip(*entries)

    yield from zip(keys, map(parse, values))


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

    yield from filter(bool, values) if clean else values
