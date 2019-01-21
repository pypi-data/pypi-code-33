# ------- #
# Imports #
# ------- #

from copy import copy
from ..fns import discardWhen, joinWith, map_, mAppendAllTo, passThrough, reduce
import os


# ---- #
# Init #
# ---- #

border = "-" * 20
twoLineSeps = os.linesep + os.linesep
separator = twoLineSeps + border + twoLineSeps


# ---- #
# Main #
# ---- #


def explainErrors(state):
    rootTestsCopy = passThrough(
        state.rootTests, [discardWhen(didSucceed), copy]
    )

    flatTests = passThrough(
        state.rootSuites,
        [discardWhen(didSucceed), reduce(flattenTests, rootTestsCopy)],
    )

    return passThrough(
        flatTests, [map_(toExplanation), joinWith(separator), wrapInBorder]
    )


# ------- #
# Helpers #
# ------- #


def toExplanation(aTest):
    explanation = []

    if aTest.parentSuite:
        explanation.append("suite: " + aTest.parentSuite.label)

    explanation.append("test: " + aTest.label)
    explanation.append("")
    explanation.append(str(aTest.error).strip())
    return os.linesep.join(explanation)


def flattenTests(result, aSuite):
    if hasattr(aSuite, "suites"):
        result = reduce(flattenTests, result)(aSuite.suites)

    return passThrough(
        aSuite.tests, [discardWhen(didSucceed), mAppendAllTo(result)]
    )


def didSucceed(testOrSuite):
    return testOrSuite.succeeded


def wrapInBorder(content):
    return (
        twoLineSeps
        + border
        + twoLineSeps
        + content
        + twoLineSeps
        + border
        + os.linesep
    )
