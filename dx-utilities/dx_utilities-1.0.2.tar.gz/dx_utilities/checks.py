# Copyright (C) 2019 demetriou engineering ltd.
# Part of `dx-utilities`, licensed under the AGPLv3+
"""Collection of common logical checks raising appropriate exceptions."""
from .exceptions import CodedValueError


def check_positive(*args, emsg=None):
    """Check if arguments are all positive values.

    :param \*args: One or more numeric values.
    :param emsg: Optional error message.
    :type emsg: str or None
    :raises ValueError: If any value is not positive.
    """
    if any([a <= 0. for a in args]):
        raise CodedValueError(1002, emsg or "Values should be positive")


def check_non_negative(*args, emsg=None):
    """Check if arguments are all non-negative values.

    :param \*args: One or more numeric values.
    :param emsg: Optional error message.
    :type emsg: str or None
    :raises ValueError: If any value is not positive.
    """
    if any([a < 0. for a in args]):
        raise CodedValueError(1003, emsg or "Values should be non-negative")


def check_numerical_value(value, emsg=None):
    """Verify that value is numerical, and raise an exception
    otherwise

    :param value:
    :param emsg: The error message to accompany the exception
        in case the check fails.
    :type emsg: str or None
    """
    if emsg is None:
        emsg = f'Variable {value} is not numerical'
    try:
        value / 3
    except TypeError:
        raise CodedValueError(1004, emsg)
