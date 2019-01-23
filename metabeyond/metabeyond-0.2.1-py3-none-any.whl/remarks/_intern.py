#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shared elements used internally only. These should not be changed or manipulated at runtime.
"""
import inspect
import logging
from typing import Any, Callable, Type, Union, List

#: Name of the hidden dunder attribute storing remarks.
REMARK_COLLECTION_ATTR = "__metabeyond_remarks__"

#: Frozen set that is reused internally.
# noinspection NonAsciiCharacters
Ø = frozenset()

#: Used for logging debugging information about checks.
logger = logging.getLogger("metabeyond.remarks")

#: Used internally to hold constraints dynamically.
CONSTRAINT_ATTR = "_constraints"

#: Used internally to hold predicates dynamically.
PREDICATE_ATTR = "_predicates"

#: Single constraint
CONSTRAINT_ARG = "constraint"

#: Multiple constraints.
CONSTRAINTS_ARG = "constraints"

#: Single predicate
PREDICATE_ARG = "predicate"

#: Multiple predicates
PREDICATES_ARG = "predicates"

#: Type hint for valid things to decorate.
ToDecorate = Union[Callable[..., Any], Type[Any]]


def members_in_this_class(cls: Type[Any], predicate=lambda _: True) -> List[Any]:
    """
    Performs analysis of the given class object's MRO and extracts members only belonging to the
    class itself, not members inherited from other classes.
    """
    # Maps class in mro to methods they have.
    mro_lookup = dict()

    # Store string names, since some members may not be hashable, we cannot make them into a set.
    for class_ in inspect.getmro(cls):
        mro_lookup[class_] = {name for name, _ in inspect.getmembers(class_)}

    all_members = mro_lookup.pop(cls)

    # Calculate members only in this class.
    for _, member_list in mro_lookup.items():
        all_members -= member_list

    # Resolve to a list of member objects, rather than names, filter by the predicate.
    all_member_objects = [getattr(cls, member) for member in all_members]
    return [member for member in all_member_objects if predicate(member)]
