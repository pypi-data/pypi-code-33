"""
OpenTMI python client decorators
"""
from enum import Enum
import re
import functools

def requires_logged_in(func):
    """
    Decorator which verify that client are logged in
    if not but env variables are available
    it tries to loggin using them
    :param fn: function to decorated
    :return: wrapper function
    """
    def ret_fn(*args):
        """
        wrapper function
        :param args: argument for decorated function
        :return: return decorated function return values
        """
        self = args[0]
        if not self.is_logged_in:
            self.try_login(raise_if_fail=True)
        return func(*args)
    return ret_fn

def setter_rules(value_type=str, each_type=None, enum=None, match=None):
    """
    setter rules
    :param value_type: required Type
    :param each_type: required type for each items in case of list
    :param enum: String, only allowed items
    :param match: string, regex pattern to be match
    :return: decorator function
    :raises: ValueError or TypeError
    example: require int type for setter - otherwise raise ValueError
    @count.setter
    @setter_rules(type=int)
    def count(self, value):
        self.value = value
    """
    def decorator_wrapper(func):
        """
        Decorator wrapper
        :param func: function for wrap
        :return: decorator wrapper
        """
        @functools.wraps(func)
        def function_wrapper(key, value):
            """
            Function wrapper
            :param key:
            :param value: value given for setter
            :return: target function return value
            """
            if not isinstance(value, value_type):
                raise TypeError("type of value must be an {}".format(value_type.__name__))
            if each_type:
                if not all(isinstance(i, each_type) for i in value):
                    raise TypeError("{} list values must be {}".format(key, each_type.__name__))
            elif isinstance(value, str) and match:
                if not re.match(match, value):
                    raise ValueError("Value does not match to regex: {}".format(match))
            if enum:
                members = Enum("values", enum)
                enum_values = [e.name for e in members] # pylint: disable=not-an-iterable
                if value not in enum_values:
                    raise ValueError("Value {} not in allowed list ({})".format(value, enum))
            return func(key, value)
        return function_wrapper
    return decorator_wrapper
