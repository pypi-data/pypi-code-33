# ------- #
# Imports #
# ------- #

from os import path
from textwrap import dedent
from traceback import format_exc
from types import SimpleNamespace as o
from .fns import forEach, iif
from .runAllTests import runAllTests
from .state import initState
from .utils import gatherTests, importTests, twoLineSeps
from .validateAndGetReportFn import validateAndGetReportFn
import os
import toml


# ---- #
# Main #
# ---- #

#
# When this function is called we can assume
#  - projectDir exists on the file system
#  - reporter is a non-relative module name
#  - silent is a string boolean
#


def runProcess(projectDir, reporter, silent):
    try:
        silent = silent == "True"
        cliResult = o(stderr=None, stdout=None, code=None)

        if not silent:
            validationResult = validateAndGetReportFn(
                reporter, silent, cliResult
            )

            if validationResult.hasError:
                return validationResult.cliResult

            report = validationResult.report
            pyprojectTomlPath = path.join(projectDir, "pyproject.toml")
            reportOpts = None
            if path.isfile(pyprojectTomlPath):
                allProjectSettings = toml.load(pyprojectTomlPath)
                result = getValueAtPath(allProjectSettings, ["tool", reporter])
                if result.hasValue:
                    reportOpts = result.value

        state = initState()
        importTests(projectDir)

        forEach(gatherTests)(state.rootSuites)
        runAllTests(state)

        if not state.testsFound:
            if not silent:
                cliResult.stderr = dedent(
                    f"""
                    No tests were found in any python files under the project's
                    tests directory: '{path.join(projectDir, 'tests')}'

                    Remember you define tests by decorating a function with
                    @test("test label")
                    """
                )

            cliResult.code = 2
            return cliResult

        if not silent:
            if reportOpts is None:
                report(state)
            else:
                report(state, reportOpts)

        cliResult.code = iif(state.succeeded, 0, 1)
        return cliResult

    except Exception:
        if not silent:
            cliResult.stderr = (
                os.linesep
                + "An error occurred during simple_test_process"
                + twoLineSeps
                + format_exc()
            )

        cliResult.code = 2
        return cliResult


# ------- #
# Helpers #
# ------- #


def getValueAtPath(aDict, pathToValue):
    result = o(hasValue=None, value=None)
    val = aDict
    for segment in pathToValue:
        if segment not in val:
            result.hasValue = False
            return result

        val = val[segment]

    result.hasValue = True
    result.value = val
    return result
