# ------- #
# Imports #
# ------- #

from .internal.getTypedResult import getTypedResult
from .internal.sanitizeAscDesc import sanitizeAscDesc


# ---- #
# Main #
# ---- #


def mOrder(ascOrDesc):
    ascOrDesc = sanitizeAscDesc(ascOrDesc)

    def mOrder_inner(collection):
        fnName = mOrder.__name__
        typedMOrder = getTypedResult(collection, typeToMOrder, fnName)
        return typedMOrder(collection, ascOrDesc)

    return mOrder_inner


# ------- #
# Helpers #
# ------- #


def mOrder_viaSort(something, ascOrDesc):
    something.sort(reverse=(ascOrDesc == "desc"))
    return something


typeToMOrder = {list: mOrder_viaSort}
