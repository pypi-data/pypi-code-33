# ------- #
# Imports #
# ------- #

from .internal.getTypedResult import getTypedResult
from types import SimpleNamespace
from copy import copy


# ---- #
# Main #
# ---- #


def assign(collection):
    fnName = assign.__name__
    assignFn = getTypedResult(collection, typeToAssign, fnName)

    return assignFn(collection)


# ------- #
# Helpers #
# ------- #


def assign_simpleNamespace(primary):
    def assign_simpleNamespace_inner(secondary):
        result = copy(primary)

        for k, v in secondary.__dict__.items():
            if k not in result.__dict__:
                setattr(result, k, v)

        return result

    return assign_simpleNamespace_inner


def assign_dict(primary):
    def assign_dict_inner(secondary):
        result = copy(primary)

        for k, v in secondary.items():
            if k not in result:
                result[k] = v

        return result

    return assign_dict_inner


typeToAssign = {dict: assign_dict, SimpleNamespace: assign_simpleNamespace}
