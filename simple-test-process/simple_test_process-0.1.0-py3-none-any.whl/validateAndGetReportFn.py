# ------- #
# Imports #
# ------- #

from traceback import format_exc
from types import SimpleNamespace as o
from .utils import twoLineSeps
import importlib
import os


# ---- #
# Main #
# ---- #


def validateAndGetReportFn(reporter, silent, cliResult):
    validationResult = o(report=None, cliResult=cliResult, hasError=False)

    try:
        reporterModule = importlib.import_module(reporter)
    except:
        if not silent:
            err = "An error occurred while importing the reporter"
            cliResult.stderr = os.linesep + err + twoLineSeps + format_exc()

        cliResult.code = 2
        validationResult.hasError = True
        return validationResult

    if hasattr(reporterModule, "report") and callable(reporterModule.report):
        validationResult.report = reporterModule.report
    else:
        if not silent:
            cliResult.stderr = (
                os.linesep + "the reporter must expose a callable 'report'"
            )

        cliResult.code = 2
        validationResult.hasError = True

    return validationResult
