# ------- #
# Imports #
# ------- #

from ..fns import forEach
from .utils import o, x


# ---- #
# Main #
# ---- #


def reportTest(aTest, idx, tests):
    indent = " " * 4 * aTest.indentLevel
    if aTest.succeeded:
        print(f"{indent}{aTest.label} {o}")
    else:
        print(f"{indent}{aTest.label} {x}")

    if (
        aTest.parentSuite
        and isLast(idx, tests)
        and not isFinalSuite(aTest.parentSuite)
    ):
        propagateBlankLineAfter(aTest.parentSuite)
        print()


def reportSuite(aSuite, idx, suites):
    if (
        aSuite.parentSuite is None
        and idx != 0
        and not suites[idx - 1].hasBlankLineAfter
    ):
        print()

    indent = " " * 4 * aSuite.indentLevel
    if aSuite.succeeded:
        print(f"{indent}{aSuite.label} {o}")
        # we only want to report failing tests, and if a suite succeeded then
        #   it doesn't contain any failing tests
        forEach(reportSuite)(aSuite.suites)
    else:
        print(f"{indent}{aSuite.label} {x}")
        forEach(reportTest)(aSuite.tests)
        forEach(reportSuite)(aSuite.suites)


# ------- #
# Helpers #
# ------- #


#
# TODO: initialize this state separate from the reporting logic similar to
#   applyIndentLevels.  That way the reporter can just check the properties on
#   the state instead of modifying it mid-run.
#
# this method is necessary due to two formatting preferences
#   1. root suites should be separated by one blank line
#   2. there should be a blank line between a test and the following suite
#
# these two preferences conflict when a blank line follows a failed test where
#   the following suite is a root suite.  By propagating the "hasBlankLineAfter"
#   state we can check that on root suites to prevent two blank lines.
#
def propagateBlankLineAfter(aSuite):
    if not aSuite.parentSuite:
        aSuite.hasBlankLineAfter = True
        return

    if isLastSiblingSuite(aSuite):
        propagateBlankLineAfter(aSuite.parentSuite)


def isLastSiblingSuite(suite):
    parentSuite = suite.parentSuite
    if parentSuite:
        siblingSuites = parentSuite.suites
    else:
        siblingSuites = suite.parentState.rootSuites

    indexOfSuite = siblingSuites.index(suite)
    return isLast(indexOfSuite, siblingSuites)


def isLast(idx, collection):
    return idx == len(collection) - 1


def isFinalSuite(aSuite):
    if not aSuite.parentSuite:
        return isLastSiblingSuite(aSuite)
    elif isLastSiblingSuite(aSuite):
        return isFinalSuite(aSuite.parentSuite)
