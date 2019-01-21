# ------- #
# Imports #
# ------- #

from traceback import format_exc
from types import SimpleNamespace as o
from ..meta import version
from .usage import usage
from .validateAndParseArgs import validateAndParseArgs
import os


# ---- #
# Init #
# ---- #

twoLineSeps = os.linesep + os.linesep


# ---- #
# Main #
# ---- #


def createRunSimpleTest(run):
    return lambda args: runSimpleTest(run, args)


def runSimpleTest(run, args):
    result = o(stdout=None, stderr=None, code=None)

    numArgs = len(args)
    if numArgs == 1:
        if args[0] == "--help":
            result.stdout = usage
            result.code = 0
            return result
        elif args[0] == "--version":
            result.stdout = version
            result.code = 0
            return result

    validationResult = validateAndParseArgs(args, result)

    if validationResult.hasError:
        return validationResult.cliResult

    argsObj = validationResult.argsObj
    isSilent = argsObj.silent

    try:
        subprocessReturnCode = run(
            reporter=argsObj.reporter,
            projectDir=argsObj.projectDir,
            silent=isSilent,
        )

        result.code = subprocessReturnCode
        return result

    except:
        if not isSilent:
            result.stderr = (
                "An unexpected error occurred" + twoLineSeps + format_exc()
            )

        result.code = 2
        return result
