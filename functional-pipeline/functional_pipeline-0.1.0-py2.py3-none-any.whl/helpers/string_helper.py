class StringPartial(type):
    """
    Meta Class for String.

    Provides static methods for the `String` class that are the partial applied `str` methods.

    Ignores private methods.
    """

    def __getattr__(self, item: str):
        if item not in dir(str):
            raise AttributeError(f"type '{self.__name__}' has no attribute '{item}'")
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
    >>> String.startswith('a')('and')
    True
    >>> String.endswith('d')('and')
    True
    >>> String.replace(".json", "")("a.json")
    "a"
    """


if __name__ == "__main__":
    import doctest

    doctest.testmod()
