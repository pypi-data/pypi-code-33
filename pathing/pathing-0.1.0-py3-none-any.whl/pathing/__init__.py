import collections


__version__ = '0.1.0'


__all__ = ('derive',)


def derive(root, old = None, get = None, min = - 1, max = float('inf')):

    if old is None:

        old = ()

    length = len(old)

    if length > max:

        return

    if not get is None:

        root = get(root, old)

    if not length < min:

        yield old, root

    if not isinstance(root, collections.Mapping):

        return

    for key, value in root.items():

        new = old + (key,)

        yield from derive(value, old = new, get = get, min = min, max = max)
