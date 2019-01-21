# ------- #
# Imports #
# ------- #

from .meta import version
from traceback import format_exc
from textwrap import dedent
from types import SimpleNamespace as o
from .check import checkSync
from .utils import iif
import os


# ---- #
# Init #
# ---- #

arguments = set(["--dir", "--silent"])
helpOrVersion = set(["--help", "--version"])

twoLineSeps = os.linesep + os.linesep

usage = dedent(
    f"""
    Usage
      is-git-repo-clean [options]
      is-git-repo-clean (--help | --version)

    Options
      --dir:      path to the git repo to test.  Defaults to `os.getcwd()`
      --silent:   a flag which disables output

    Returns
      <exit code>: <output>

      0: yes
      1: no
      2: <invalid arg message>
      3: dir is not a git repository
      4: unexpected error occurred <error>
    """
)


# ---- #
# Main #
# ---- #


def getIsGitRepoClean(args):
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

    argsObj = validateAndParseArgs(args, result)

    if argsObj is result:
        return result

    isSilent = argsObj.silent

    try:
        isClean = checkSync(argsObj.dir or None)
        if not isSilent:
            if isClean:
                result.stdout = "yes"
            else:
                result.stderr = "no"

        result.code = iif(isClean, 0, 1)
        return result

    except Exception as e:
        if "is not a git repository" in str(e):
            if not isSilent:
                result.stderr = "dir is not a git repository"

            result.code = 3
        else:
            if not isSilent:
                result.stderr = (
                    f"unexpected error occurred{twoLineSeps}" + format_exc()
                )

            result.code = 4

        return result


# ------- #
# Helpers #
# ------- #


def validateAndParseArgs(args, result):
    i = 0
    argsObj = o(dir=None, silent=False)

    while i < len(args):
        arg = args[i]
        if arg not in arguments:
            if arg in helpOrVersion:
                result.stderr = f"'{arg}' must be the only argument when passed"
            else:
                result.stderr = f"invalid option '{arg}'"

            result.stderr += os.linesep + usage
            result.code = 2

            return result

        if arg == "--dir":
            if i == len(args) - 1:
                result.stderr = "'--dir' must be given a value"
                result.stderr += os.linesep + usage
                result.code = 2

                return result

            argsObj.dir = args[i + 1]
            i += 1
        else:
            argsObj.silent = True

        i += 1

    return argsObj
