# ------- #
# Imports #
# ------- #

from .internal.makeGenericCallFn import makeGenericCallFn
from .internal.getTypedResult import getTypedResult
from .decorators.argIsCallable import argIsCallable


# ---- #
# Main #
# ---- #


@argIsCallable
def keepWhen(predicate):
    fnName = keepWhen.__name__
    shouldKeep = makeGenericCallFn(predicate, 3, fnName)

    def keepWhen_inner(collection):
        typedKeepWhen = getTypedResult(collection, typeToKeepWhen, fnName)
        return typedKeepWhen(shouldKeep, collection)

    return keepWhen_inner


# ------- #
# Helpers #
# ------- #


def keepWhen_list(shouldKeep, aList):
    result = []
    for idx, el in enumerate(aList):
        if shouldKeep(el, idx, aList):
            result.append(el)

    return result


def keepWhen_dict(shouldKeep, aDict):
    result = {}
    for key, val in aDict.items():
        if shouldKeep(val, key, aDict):
            result[key] = val

    return result


typeToKeepWhen = {list: keepWhen_list, dict: keepWhen_dict}
