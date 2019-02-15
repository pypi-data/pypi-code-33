__all__ = ['repr_method']


def repr_method(*args):
    """
    A convenience wrapper for creating class `__repr__` methods.
    If '__all__' is passed to the method, all properties assigned to the
    object will be included in returned string.

    Parameters
    ----------
    args
        Strings corresponding to class properties to be returned.

    Examples
    --------
    >>> class Test():
    ...     __repr__ = repr_method('x', 'y', 'z')
    ...
    ...     def __init__(self):
    ...         self.x, self.y, self.z = 1, 2, 3
    ...
    >>> repr(Test())
    'Test(x=1, y=2, z=3)'
    """
    def func(self):
        if args and args[0] == '__all__':
            props = sorted(vars(self).keys())
        else:
            props = args

        s = ['{}={!r}'.format(k, getattr(self, k)) for k in props]
        return '{}({})'.format(type(self).__name__, ', '.join(s))

    return func
