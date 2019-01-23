#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lightweight annotations to classes and methods for descriptive purposes.

These do not actually do anything useful other than appending to the object's docstring, they just make the code
easier to self document in a consistent way without using hungarian-notation-like names.

Note:
    Remember that hints are purely descriptive notes added to the docstring. They must not called
    with arguments, for example, you would use `@hint`. Calling *with* parenthesis `()` is invalid.

    :mod:`metabeyond.remarks` decorators on the other hand must be invoked with an argument list. An example being
    `@remark()` or `@remark(foo, bar)` or `@remark(f='foo', b='bar')`. These will add metadata to the decorated
    function or class that specifies the presence of that decorator on the object, and this can be queried at runtime.
    Calling *without* parenthesis will produce an invalid result.

    Using the presence of parenthesis is a good way to determine if it is a documentation hint or a
    metadata remark. Metadata remarks are much more complicated than hints.

    To document parameter types and return types, one should use type annotations or comment-based
    annotations as per PEP 3107: `def foo(bar: int, baz: int) -> float:`. Utilities for this are in the
    Python :mod:`typing` module.

Warning:
    Enabling CPython's second level optimisation `-OO` will prevent docstrings from being retained by classes and
    functions. Applying decorators will force those docstrings to be implemented, so it will appear that the other
    contents will have been replaced by the hint docstring. This is due to how Python handles optimisation, and it is
    out of scope of this module to take this into consideration.

    TL;DR don't run Sphinx with optimisation flags enabled, and if you reflect on your docstrings at runtime, don't
    use `-OO`. Usage of first level optimisation `-O` is fine.
"""
import textwrap
from typing import Any, Callable, Type, Union

#: Type hint for valid things to decorate.
_ToDecorate = Union[Callable[..., Any], Type[Any]]


def append_to_docstring(new_content: str, existing_object: Any) -> None:
    """
    Appends a given string to the docstring of an existing object. If no docstring exists, one is injected.

    Will fail on frozen objects, such as C modules.

    Will fail if the docstring is a non-string or non-None type.
    """
    existing_doc = getattr(existing_object, "__doc__", "")
    if existing_doc is None:
        existing_doc = ""

    elif not isinstance(existing_doc, str):
        raise TypeError(
            f"{existing_object} was expected to have a string docstring, but it was {existing_doc}"
        )

    # Dedent to add the documentation, then reindent again to maintain formatting.
    start_index = existing_doc.index(existing_doc.lstrip())
    indent = existing_doc[:start_index]
    existing_doc = textwrap.dedent(existing_doc)

    if existing_doc and not existing_doc.isspace():
        existing_doc += "\n"

    existing_doc += new_content
    existing_doc = textwrap.indent(existing_doc, indent, lambda _: None)
    setattr(existing_object, "__doc__", existing_doc)


class Hint:
    """
    Simple hint base implementation which produces a decorator object with some description.

    The decorator always returns what was input without any modification other than appending to the docstring.
    This mechanism is purely for documentation purposes only.

        >>> interface = Hint('This is an abstract class with no internal state.')

        >>> @interface
        ... class Playable:
        ...     "A thing that you can play."
        ...     def play(self):
        ...         ...

        >>> import inspect
        >>> print(inspect.cleandoc(inspect.getdoc(Playable)))

    The above example would produce the following

    .. code-block:: none

        A thing that you can play.

        This is an abstract class with no internal state.

    Hints implement a custom `__repr__` method to allow them to self-document
    in a Sphinx environment.
    """

    def __init__(self, description: str) -> None:
        self.description = description

    def __call__(self, item):
        append_to_docstring(self.description, item)
        return item

    def __repr__(self):
        return "This hint reads: " + self.description


#: Decorates anything used as a decorator.
decorator = Hint("This is a class or function used as a decorator.")

#: Decorates anything that behaves like an interface with no underlying state.
interface = Hint("This is a pure abstract class with no underlying state.")

#: Decorates anything that might be a placeholder forward declaration.
forward_declaration = Hint("This is a forward declaration for another object")
