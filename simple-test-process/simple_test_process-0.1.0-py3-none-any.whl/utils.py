# ------- #
# Imports #
# ------- #

from glob import glob
from os import path
from .suite import suite
from .test import test
import importlib.util
import os

from .fns import (
    discardFirst,
    discardWhen,
    endsWith,
    forEach,
    joinWith,
    map_,
    passThrough,
    split,
)


# ---- #
# Main #
# ---- #

twoLineSeps = os.linesep + os.linesep


#
# I'm choosing to gather all the tests prior to running any because I feel that
#   will be a simpler design.
#
def gatherTests(aSuite):
    oldCurrentSuite = aSuite.rootState.currentSuite
    aSuite.rootState.currentSuite = aSuite
    aSuite.fn()
    forEach(gatherTests)(aSuite.suites)
    aSuite.rootState.currentSuite = oldCurrentSuite


#
# I can't find a clean way to do this so I'm rolling my own.  The python
#   import system is inherently hacky anyway :(
#
def importTests(projectDir):
    testsDir = path.join(projectDir, "tests")
    globStr = path.join(testsDir, "**/*.py")

    passThrough(
        globStr,
        [
            recursiveGlob,
            discardWhen(endsWith("__init__.py")),
            map_(discardFirst(len(projectDir + "/"))),
            map_(toModulePath),
            forEach(importModule),
        ],
    )


def importModule(modulePath):
    try:
        spec = importlib.util.find_spec(modulePath)
        testModule = importlib.util.module_from_spec(spec)
        testModule.test = test
        testModule.suite = suite
        spec.loader.exec_module(testModule)
    except Exception as e:
        raise Exception(f"Error occurred while importing '{modulePath}'") from e


def recursiveGlob(globStr):
    return glob(globStr, recursive=True)


def toModulePath(filePathFromTestsDir):
    return passThrough(
        filePathFromTestsDir, [removeExtension, split(os.sep), joinWith(".")]
    )


def removeExtension(filePath):
    return os.path.splitext(filePath)[0]
