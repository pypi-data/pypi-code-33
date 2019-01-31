

__all__ = ('Error', 'InvalidSession')


class Error(Exception):

    """
    Raised when something flops.
    """

    __slots__ = ()


class InvalidSession(Error):

    """
    Raised when reconnecting is not possible.
    """

    __slots__ = ()
