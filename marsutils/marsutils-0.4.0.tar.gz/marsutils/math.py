import math


def signed_square(value):
    """ A tiny function that returns the square of ``value`` but with the
        same sign, e.g. ``signed_square(-2)`` returns ``-4``
    """
    return math.copysign(value * value, value)
