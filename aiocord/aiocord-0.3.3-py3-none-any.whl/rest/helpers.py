

__all__ = ()


def get_soft(root, key, factory):

    try:

        value = root[key]

    except KeyError:

        value = root[key] = factory()

    return value


def fix_params(root, booleans = ('false', 'true')):

    for (key, value) in tuple(root.items()):

        if value is None:

            del root[key]

            continue

        if isinstance(value, bool):

            value = _booleans[value]

        elif isinstance(value, (float, int)):

            value = str(value)

        else:

            continue

        root[key] = value
