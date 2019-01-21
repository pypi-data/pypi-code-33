# ------- #
# Imports #
# ------- #

from types import SimpleNamespace as o
from .bfFormat import bfFormat


# ---- #
# Init #
# ---- #

defaultIndent = 2


# ---- #
# Main #
# ---- #


def pprint(something, *, indent=defaultIndent):
    print(format(something, indent=indent))


def format(something, *, indent=defaultIndent):
    return bfFormat(something, o(indent=indent))


def wrapWith(*, indent):
    wrappedIndent = indent

    def wrappedPprint(something, *, indent=wrappedIndent):
        pprint(something, indent=indent)

    def wrappedFormat(something, *, indent=wrappedIndent):
        return format(something, indent=indent)

    return o(pprint=wrappedPprint, format=wrappedFormat)
