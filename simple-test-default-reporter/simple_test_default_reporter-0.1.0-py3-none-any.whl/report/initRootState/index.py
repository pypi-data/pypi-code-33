# ------- #
# Imports #
# ------- #

from ...fns import passThrough
from .applyIndentLevels import applyIndentLevels
from .removeSucceededTestsInSuites import removeSucceededTestsInSuites


# ---- #
# Main #
# ---- #


def initRootState(state):
    return passThrough(
        state,
        [
            removeSucceededTestsInSuites,
            applyIndentLevels,
            initializeHasBlankLineAfter,
            initializeParentState,
        ],
    )


# ------- #
# Helpers #
# ------- #


def initializeHasBlankLineAfter(state):
    for suite in state.rootSuites:
        suite.hasBlankLineAfter = False

    return state


def initializeParentState(state):
    for suite in state.rootSuites:
        suite.parentState = state

    for test in state.rootTests:
        test.parentState = state

    return state
