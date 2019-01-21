# ------- #
# Imports #
# ------- #

from . import minimal
from ..fns import forEach, isLaden
from .explainErrors import explainErrors
from .initRootState import initRootState


# ---- #
# Main #
# ---- #


def report(state, *, showErrorDetails=True):
    state = initRootState(state)

    rootTests = state.rootTests
    rootSuites = state.rootSuites

    forEach(minimal.reportTest)(rootTests)

    if isLaden(rootTests) and isLaden(rootSuites):
        print()

    forEach(minimal.reportSuite)(rootSuites)

    if showErrorDetails and not state.succeeded:
        print(explainErrors(state))
