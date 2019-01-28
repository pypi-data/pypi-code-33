import ast
import collections.abc
import itertools
import collections
import functools
import inspect
import tempfile
import types
import sys
import json
import textwrap

import attr


UNKNOWN = "____UNKNOWN____"
NO_VALUE = None


@attr.s
class InputCollection:

    closure = attr.ib()
    args = attr.ib()


@attr.s
class FunctionCall:
    function = attr.ib()
    inputs = attr.ib()

    @classmethod
    def from_args(cls, function, args, kwargs):
        inputs = _get_inputs(function, *args, **kwargs)

        return cls(function, inputs)


def _extract_referenced_names(function):
    source = textwrap.dedent(inspect.getsource(function))
    tree = ast.parse(source)
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    parameters = set(inspect.signature(function).parameters)
    return names - parameters


def get_closure(function):
    closure = {}

    for d in reversed(inspect.getclosurevars(function)):

        if isinstance(d, collections.abc.Mapping):
            closure.update(d)

    locally_used_external_names = _extract_referenced_names(function)
    name_to_value = {
        name: closure.get(name, UNKNOWN) for name in locally_used_external_names
    }

    return name_to_value


def _get_inputs(function, *args, **kwargs):

    closure = get_closure(function)
    args = inspect.signature(function).bind(*args, **kwargs)
    args.apply_defaults()

    return InputCollection(closure, args)
