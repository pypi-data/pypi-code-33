# ------- #
# Imports #
# ------- #

from .internal.getTypedResult import getTypedResult


# ---- #
# Main #
# ---- #


def mAppendAll(collectionToAppend):
    def mAppendAll_inner(collection):
        typedMAppendAll = getTypedResult(
            collection, typeToMAppendAll, mAppendAll.__name__
        )
        return typedMAppendAll(collectionToAppend, collection)

    return mAppendAll_inner


# ------- #
# Helpers #
# ------- #


def mAppendAll_list(listToAppend, aList):
    aList += listToAppend
    return aList


typeToMAppendAll = {list: mAppendAll_list}
