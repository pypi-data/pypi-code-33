

__all__ = ()


def parse(content, lower, middle, upper):

    try:

        head, tail = content.split(middle, 1)

    except ValueError:

        head = content

        arguments = ()

    else:

        arguments = tail.split(upper)

    names = head.split(lower)

    return names, arguments


def trail(store, names):

    for name in names:

        value, store = store[name]

    return value
