#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remark introspection methods.
"""
__all__ = ["quick_remark", "get_remarks_for", "has_remarks", "get_remark", "get_remarks_by_type"]

from typing import Any, FrozenSet, Iterator, Optional, Type

from . import _intern
from .impl import Remark


def quick_remark(name: str) -> Type[Remark]:
    """
    Creates a remark quickly.

    >>> foo = quick_remark('foo')

    >>> @foo()
    ... def bar(): ...

    Args:
        name:
            The name of the remark to use

    Returns:
        The remark type generated from the given name.
    """
    cls: Type[Remark] = type(name, (Remark,), {})
    return cls


def get_remarks_for(object: Any) -> FrozenSet[Remark]:
    """
    Returns a frozen set of remarks for the given object at the time of calling, or an empty set if none exist.

    Args:
        object:
            The object to get the remarks applied to. This might be any type of object, but usually will be a function
            or class reference.

    Returns:
        Frozen set of any remarks found.
    """
    return frozenset(getattr(object, _intern.REMARK_COLLECTION_ATTR, _intern.Ø))


def has_remarks(object: Any) -> bool:
    """
    Returns true if the object has any remarks applied to it.
    """
    return bool(get_remarks_for(object))


def get_remark(class_: Type[Remark], object: Any) -> Optional[Remark]:
    """
    Get the remark of the given type that is applied to the object.

    This will not consider subtypes/covariants.

    Args:
        class_:
            The type of remark to look for.
        object:
            The object with remarks applied to it to inspect.

    Returns:
        The first remark found, or None if no remarks matching this type were discovered.
    """
    remarks = get_remarks_for(object)
    for remark in remarks:
        if type(remark) == class_:
            return remark
    return None


def get_remarks_by_type(base_class: Type[Remark], object: Any) -> Iterator[Remark]:
    """
    Gets any remarks that are instances of the given base class which are applied to the given object.

    Args:
        base_class:
            The base class of remark to filter by. Set to `remark.Remark` to get all remarks, or just
            call :meth:`get_remarks_for`.
        object:
            The object with remarks applied to it to consider.

    Returns:
        An iterator of each matching remark discovered. Order is undefined.
    """
    remarks = get_remarks_for(object)
    for remark in remarks:
        if isinstance(remark, base_class):
            yield remark
