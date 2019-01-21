# ------- #
# Imports #
# ------- #

from .internal.getTypedResult import getTypedResult
from types import SimpleNamespace


# ---- #
# Main #
# ---- #


def mAssign(collection):
    fnName = mAssign.__name__
    assignFn = getTypedResult(collection, typeToAssign, fnName)

    return assignFn(collection)


# ------- #
# Helpers #
# ------- #


def mAssign_simpleNamespace(primary):
    def mAssign_simpleNamespace_inner(secondary):
        for k, v in primary.__dict__.items():
            setattr(secondary, k, v)

        return secondary

    return mAssign_simpleNamespace_inner


def mAssign_dict(primary):
    def mAssign_dict_inner(secondary):
        for k, v in primary.items():
            secondary[k] = v

        return secondary

    return mAssign_dict_inner


typeToAssign = {dict: mAssign_dict, SimpleNamespace: mAssign_simpleNamespace}
