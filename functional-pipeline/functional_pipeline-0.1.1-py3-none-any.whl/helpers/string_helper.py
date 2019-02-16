class StringPartial(type):
    """
    Meta Class for String.

    Provides static methods for the `String` class that are the partial applied `str` methods.

    Ignores private methods.
    """

    def __getattr__(cls, item: str):
        if item not in dir(str):
            raise AttributeError(f"type '{cls.__name__}' has no attribute '{item}'")
        if item.startswith('_'):
            return getattr(str, item)
        func = getattr(str, item)

        def _outer(*args, **kwargs):

            def _inner(base):
                return func(base, *args, **kwargs)

            return _inner

        return _outer


class String(metaclass=StringPartial):
    """
    A Helper Class that reflects all of the methods available on
    a string object and makes them available as a curry-able
    function.

    Each method takes what would be the argument list when used
    against a string object, and returns a function that takes
    what the base object should be.

    Examples:
    >>> String.startswith('a')('and')
    True
    >>> String.endswith('d')('and')
    True
    >>> String.replace(".json", "")("a.json")
    'a'
    >>> String.split(',')("1,2,3")
    ['1', '2', '3']
    """


if __name__ == "__main__":
    import doctest

    doctest.testmod()
