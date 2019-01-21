# ------- #
# Imports #
# ------- #

from os import path
from .validateRunParams import validateRunParams
from ..fns import raise_
import os
import sys


# ---- #
# Main #
# ---- #


def createRun(subprocessRun):
    return lambda **kwargs: run(subprocessRun, **kwargs)


def run(subprocessRun, *, projectDir=None, reporter=None, silent=False):
    validateRunParams(projectDir, reporter, silent)

    if projectDir is None:
        projectDir = os.getcwd()
    else:
        projectDir = path.normpath(projectDir)

    if reporter is None:
        reporter = "simple_test_default_reporter"

    ensureTestsDirExists(projectDir)

    subprocessResult = subprocessRun(
        [
            sys.executable,
            "-m",
            "simple_test_process",
            projectDir,
            reporter,
            str(silent),
        ],
        cwd=projectDir,
    )

    return subprocessResult.returncode


# ------- #
# Helpers #
# ------- #


def ensureTestsDirExists(projectDir):
    testsDir = path.join(projectDir, "tests")
    if not path.isdir(testsDir):
        raise_(
            Exception,
            f"""
            projectDir must contain a directory 'tests'
            projectDir: {projectDir}
            """,
        )
