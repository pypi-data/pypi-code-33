# ------- #
# Imports #
# ------- #

from .internal.getTypedResult import getTypedResult


# ---- #
# Main #
# ---- #


def discard(el):
    def discard_inner(collection):
        typedDiscard = getTypedResult(
            collection, typeToDiscard, discard.__name__
        )
        return typedDiscard(el, collection)

    return discard_inner


# ------- #
# Helpers #
# ------- #


def discard_list(elToDiscard, aList):
    result = []
    for el in aList:
        if el != elToDiscard:
            result.append(el)

    return result


typeToDiscard = {list: discard_list}
