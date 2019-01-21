# ------- #
# Imports #
# ------- #

from .internal.getTypedResult import getTypedResult
from .mAppendAll import typeToMAppendAll


# ---- #
# Main #
# ---- #


def mAppendAllTo(collection):
    def mAppendAllTo_inner(collectionToAppend):
        typedMAppendAllTo = getTypedResult(
            collection, typeToMAppendAll, mAppendAllTo.__name__
        )
        return typedMAppendAllTo(collectionToAppend, collection)

    return mAppendAllTo_inner
