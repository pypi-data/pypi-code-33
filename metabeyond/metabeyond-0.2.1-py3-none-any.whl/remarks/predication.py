#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remarks for marking a method in a remark as a predicate or constraint.
"""
__all__ = ["RemarkPredicate", "RemarkConstraint"]

import inspect


# We cant use remarks to define core remarks as it would lead to a recursive reference and break, so we make some
# cheap modifications here to keep stuff simple.


class RemarkConstraint:
    """
    Decorates a function within a :class:`Remark`-derived class to register the function as a constraint method.

    Note:
        This decorator must not be called with any arguments.

        >>> # Correct
        >>> @RemarkConstraint
        ... def foo(self, item): ...

        >>> # Incorrect
        >>> @RemarkConstraint()
        ... def foo(self, item): ...
    """

    def __init__(self, func):
        if not inspect.isfunction(func):
            raise TypeError("Cannot mark a non-function as a remark constraint...")
        else:
            self.func = func

    def __call__(self, remark, item):
        return self.func(remark, item)


class RemarkPredicate:
    """
    Decorates a function within a :class:`Remark`-derived class to register the function as a predicate method.

    Note:
        This decorator must not be called with any arguments.

        >>> # Correct
        >>> @RemarkPredicate
        ... def foo(self, item): ...

        >>> # Incorrect
        >>> @RemarkPredicate()
        ... def foo(self, item): ...

    """

    def __init__(self, func):
        if not inspect.isfunction(func):
            raise TypeError("Cannot mark a non-function as a remark predicate...")
        else:
            self.func = func

    def __call__(self, remark, item):
        return self.func(remark, item)
