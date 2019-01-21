# ------- #
# Imports #
# ------- #

from types import SimpleNamespace as o
from ...fns import assign, map_, mAssign, mSet


# ---- #
# Main #
# ---- #


def applyIndentLevels(state):
    rootTests = map_(addIndentLevelToTest(0))(state.rootTests)
    rootSuites = map_(addIndentLevelToSuite(0))(state.rootSuites)
    return assign(o(rootTests=rootTests, rootSuites=rootSuites))(state)


# ------- #
# Helpers #
# ------- #


def addIndentLevelToTest(lvl):
    def applyIndentLevel_inner(aTest):
        return mSet("indentLevel", lvl)(aTest)

    return applyIndentLevel_inner


def addIndentLevelToSuite(lvl):
    def addIndentLevelToSuite_inner(aSuite):
        indentLevel = lvl
        tests = map_(addIndentLevelToTest(lvl + 1))(aSuite.tests)
        suites = map_(addIndentLevelToSuite(lvl + 1))(aSuite.suites)
        return mAssign(o(indentLevel=indentLevel, tests=tests, suites=suites))(
            aSuite
        )

    return addIndentLevelToSuite_inner
