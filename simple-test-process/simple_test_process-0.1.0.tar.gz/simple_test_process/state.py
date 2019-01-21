from copy import deepcopy
from types import SimpleNamespace as o

_initialState = o(
    rootTests=[],
    rootSuites=[],
    currentSuite=None,
    testsFound=False,
    succeeded=True,
)


state = deepcopy(_initialState)


def _getState():
    return state


def initState():
    global state
    state = deepcopy(_initialState)
    return state


def addSuite(label, fn):
    currentSuite = state.currentSuite
    newSuite = o(
        label=label,
        fn=fn,
        tests=[],
        suites=[],
        parentSuite=currentSuite,
        rootState=state,
        succeeded=True,
    )

    if currentSuite is None:
        state.rootSuites.append(newSuite)
    else:
        currentSuite.suites.append(newSuite)

    return state


def addTest(label, fn):
    global state
    currentSuite = state.currentSuite
    test = o(label=label, fn=fn, parentSuite=currentSuite, rootState=state)

    if currentSuite is None:
        state.rootTests.append(test)
    else:
        currentSuite.tests.append(test)

    state.testsFound = True

    return state
