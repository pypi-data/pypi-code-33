# -*- coding: utf-8 -*-
from typing import Any


class NoneValueException(RuntimeError):
    """An exception for None value errors"""

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)


class IllegalStateException(RuntimeError):
    """An exception for unexpected states"""

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)


class IllegalArgumentException(RuntimeError):
    """An exception for illegal arguments to methods"""

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)


class Preconditions(object):
    """
    A precondition checking class.

    Provides only static utility methods that can be used to do precondition
    checks in methods with a nice syntax.  This class is heavily inspired by
    the one from Google's Guava library.
    """

    @staticmethod
    def check_not_none(reference: Any, message: str = "") -> Any:
        """
        Checks whether a provided reference is not None.

        Raises a NoneValueException if the reference was None.

        :param reference: The reference to check for None value
        :param message: An optional message for the exception
        :return: Reference in case it is not None
        """
        if reference is None:
            raise NoneValueException(message)

        return reference

    @staticmethod
    def check_state(expression: bool, message: str = "") -> None:
        """
        Checks whether a provided state expression evaluates to True.

        Raises an IllegalStateException if the expression evaluates to False.

        :param expression: The expression to check
        :param message: An optional message for the exception
        """
        if not expression:
            raise IllegalStateException(message)

    @staticmethod
    def check_argument(expression: bool, message: str = "") -> None:
        """
        Checks whether a provided argument evaluates to True.

        Raises an IllegalArgumentException if the given expression evaluates to
        False.

        :param expression: The expression to check
        :param message: An optional message for the exception
        """
        if not expression:
            raise IllegalArgumentException(message)
