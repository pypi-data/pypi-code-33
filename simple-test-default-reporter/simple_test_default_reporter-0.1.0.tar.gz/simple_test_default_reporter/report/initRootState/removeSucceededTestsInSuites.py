# ------- #
# Imports #
# ------- #

from types import SimpleNamespace as o
from ...fns import mAssign, discardWhen, map_, set_


# ---- #
# Main #
# ---- #


def removeSucceededTestsInSuites(state):
    rootSuites = map_(removeSucceededTests)(state.rootSuites)
    return set_("rootSuites", rootSuites)(state)


# ------- #
# Helpers #
# ------- #


def isSucceeded(aTest):
    return aTest.succeeded


def removeSucceededTests(aSuite):
    tests = discardWhen(isSucceeded)(aSuite.tests)
    suites = map_(removeSucceededTests)(aSuite.suites)
    return mAssign(o(tests=tests, suites=suites))(aSuite)
