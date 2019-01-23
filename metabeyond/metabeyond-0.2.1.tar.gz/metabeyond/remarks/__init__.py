#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"Annotation" decorators that can be applied to functions and classes as a way of tagging the object with
some form of metadata. This is designed to function in a similar way to Java 6 annotation interfaces.

Note:
    It is imperative to remember that remark decorators hand must be invoked with an argument list. An example being
    `@remark()` or `@remark(foo, bar)` or `@remark(f='foo', b='bar')`. These will add metadata to the decorated
    function or class that specifies the presence of that decorator on the object, and this can be
    queried at runtime, which requires marginally more resources than if we were to not use it at all.
    Calling *without* parenthesis `()` is invalid.

    Hints (provided by :mod:`metabeyond.hints`), on the other hand, are purely descriptive notes added to the docstring.
    They *must not* be called with arguments, for example `@hint`. Calling *with* parenthesis `()` will produce an
    invalid result, not decorating the given object correctly.

    Using the presence of parenthesis is a good way to determine if it is a documentation hint or a
    metadata remark. Metadata remarks are much more complicated than hints.

    To document parameter types and return types, one should use type annotations or comment-based
    annotations as per PEP 3107: `def foo(bar: int, baz: int) -> float:`. Utilities for this are in the
    Python :mod:`typing` module.

As this functionality is fairly difficult to debug due to its dynamic nature, enabling the `DEBUG` logging
level for `metabeyond.remarks` in the standard Python logging module will enable exposing information regarding
what is happening internally, such as the predicates and constraints that are failing, etc.
"""

from .impl import *
from .introspect import *
from .predication import *
