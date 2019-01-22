import collections


__version__ = '0.0.0'


__all__ = ('derive',)


def derive(root, level, store = None, point = None):

    level -= 1

    old = store if store else ()

    if point:

        root = point(root, level)

    if not isinstance(root, collections.Mapping):

        return

    for key, value in root.items():

        new = old + (key,)

        if level:

            yield from derive(value, level, store = new, point = point)

        else:

            yield new, value
