import functools
from datetime import datetime

from mongoengine import DoesNotExist, ValidationError


def validate_datetime(value, value_name):
    try:
        datetime.strptime(value, '%Y.%m.%d %H.%M')
    except ValueError:
        msg = f'{value_name} should have a format %Y.%m.%d %H.%M'
        raise ValidationError(msg)


"""
Decorators
"""


def get_or_404(fn):
    """
    404 as response if document doesn't exists
    """

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except DoesNotExist:
            return "Does not exists", 404

    return wrapper
