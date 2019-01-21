# ------- #
# Imports #
# ------- #

from types import SimpleNamespace
from .internal.getTypedResult import getTypedResult


# ---- #
# Main #
# ---- #


def getListOfCollectionKeys(collection):
    fnName = getListOfCollectionKeys.__name__
    typedKeys = getTypedResult(collection, typeToKeys, fnName)
    return typedKeys(collection)


# ------- #
# Helpers #
# ------- #


def getListOfCollectionKeys_dict(aDict):
    return list(aDict.keys())


def getListOfCollectionKeys_simpleNamespace(aSimpleNamespace):
    return list(aSimpleNamespace.__dict__.keys())


typeToKeys = {
    dict: getListOfCollectionKeys_dict,
    SimpleNamespace: getListOfCollectionKeys_simpleNamespace,
}
