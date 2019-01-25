
from . import abstract


__all__ = ('flag', 'group', 'split')


escape = '\\'


def clean(values, escape = escape, strip = True, empty = True):

    """
    Strip ends and selectively yield and values.
    """

    revert = len(escape)

    for value in values:

        if strip:

            value = value.strip()

        if value.startswith(escape):

            value = value[revert:]

        if value.endswith(escape):

            value = value[:-revert]

        if not value and empty:

            continue

        yield value


def flag(values, *keys, escape = escape, clean = clean):

    """
    Differenciate values according to keywords.
    """

    pairs = abstract.flag(escape, values, keys)

    if clean:

        keys, values = zip(*pairs)

        values = clean(values)

        pairs = zip(keys, values)

    return pairs


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
