#
# README
#  - Similar to javascript's Object.assign, this assigns properties right to
#    left, meaning objects to the right take precedence to those on the left
#

# ------- #
# Imports #
# ------- #

from types import SimpleNamespace
from .decorators.argIsListOfType import argIsListOfType
from .internal.NotCallable import NotCallable


# ---- #
# Main #
# ---- #


@argIsListOfType(SimpleNamespace)
def assignAll_simpleNamespace(aList):
    result = SimpleNamespace()

    for obj in aList:
        for key, val in obj.__dict__.items():
            setattr(result, key, val)

    return result


assignAll = NotCallable("assignAll", simpleNamespaces=assignAll_simpleNamespace)
