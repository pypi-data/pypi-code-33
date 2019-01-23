#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:class:`metabeyond.hints.Hint` documentation decorators for other components in this framework.
"""
__all__ = [
    "slotted",
    "discovery",
    "class_only_decorator",
    "function_only_decorator",
    "method_only_decorator",
    "decorator",
    "interface",
    "abstract_class",
]

from metabeyond import hints


#: Decorates any class that uses `__slots__` internally.
#:
#: See https://docs.python.org/3/reference/datamodel.html#object.__slots__
slotted = hints.Hint(
    "This class is slotted, so does not allow dynamic attribute injection without subclassing."
)


#: Decorates any element that is used when discovery at runtime.
discovery = hints.Hint(
    "This element has the ability to be discovered when performing introspection at runtime."
)

#: Marks an element as a decorator that can only decorate classes.
class_only_decorator = hints.Hint("This can only decorate classes.")

#: Marks an element as a decorator that can only decorate functions.
function_only_decorator = hints.Hint("This can only decorate functions.")

#: Marks an element as a decorator that can only decorate methods (functions within a class context).
method_only_decorator = hints.Hint("This can only decorate methods.")

#: Mark an element as being a decorator for anything.
decorator = hints.decorator

#: Mark an element as being an interface.
interface = hints.interface

#: Marks an abstract class.
abstract_class = hints.Hint('This is an abstract class.')
