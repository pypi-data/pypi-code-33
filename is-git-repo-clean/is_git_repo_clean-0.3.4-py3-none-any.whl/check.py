#
# TODO: find a cross-platform way to rely only on the returncode for untracked
#   files.  Currently it returns stdout/stderr which should be unnecessary.
#

# ------- #
# Imports #
# ------- #

from textwrap import dedent
from .utils import iif, resolveAll
import asyncio
import os
import subprocess


# ---- #
# Init #
# ---- #

runAsync = asyncio.create_subprocess_exec
run = subprocess.run

headExistsCmd = ["git", "rev-parse", "HEAD"]
isAGitRepoCmd = ["git", "rev-parse", "--is-inside-work-tree"]
# Any way to remove the double negative?
allFilesAreTrackedCmd = [
    "git",
    "ls-files",
    "--other",
    "--directory",
    "--exclude-standard",
    "--no-empty-directory",
]
emptyGitTree = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


# ---- #
# Main #
# ---- #


async def check(cwd=None):
    cwd = cleanCwd(cwd)

    isAGitRepo_proc = await runAsync(
        *isAGitRepoCmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
        cwd=cwd,
    )
    isAGitRepo_result = await isAGitRepo_proc.wait()
    if isAGitRepo_result != 0:
        raise Exception(f"'{cwd}' is not a git repository")

    headExists_proc = await runAsync(
        *headExistsCmd,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
        cwd=cwd,
    )
    headExists_result = await headExists_proc.wait()
    headExists = headExists_result == 0
    hasNoChangesCmd = getHasNoChangesCmd(headExists)

    checks = [
        runAsync(
            *hasNoChangesCmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
            cwd=cwd,
        ),
        runAsync(
            *allFilesAreTrackedCmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=cwd,
        ),
    ]

    noChanges_proc, allTracked_proc = await resolveAll(checks)
    results = await resolveAll(
        [noChanges_proc.wait(), allTracked_proc.communicate()]
    )
    noChanges_result, allTracked_result = results

    if allTracked_proc.returncode != 0 or noChanges_result != 0:
        return False

    stdout, _stderr = allTracked_result
    return len(stdout.decode("utf-8")) == 0


def checkSync(cwd=None):
    cwd = cleanCwd(cwd)

    isAGitRepo = (
        run(
            isAGitRepoCmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=cwd,
        ).returncode
        == 0
    )

    if not isAGitRepo:
        raise Exception(f"'{cwd} is not a git repository")

    headExists = (
        run(
            headExistsCmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=cwd,
        ).returncode
        == 0
    )

    hasNoStagedChangesCmd = getHasNoChangesCmd(headExists, staged=True)
    hasNoUnstagedChangesCmd = getHasNoChangesCmd(headExists)

    allTracked_result = run(
        allFilesAreTrackedCmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=cwd,
    )

    hasNoStagedChanges_result = run(
        hasNoStagedChangesCmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=cwd,
    )

    hasNoUnstagedChanges_result = run(
        hasNoUnstagedChangesCmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=cwd,
    )

    return (
        hasNoStagedChanges_result.returncode == 0
        and hasNoUnstagedChanges_result.returncode == 0
        and allTracked_result.returncode == 0
        and len(allTracked_result.stdout) == 0
    )


# ------- #
# Helpers #
# ------- #


def cleanCwd(cwd):
    if cwd is None:
        return os.getcwd()
    elif not isinstance(cwd, str):
        raise TypeError(
            dedent(
                f"""\
                cwd must be an instance of str
                type(cwd): {type(cwd)}
                cwd: {cwd}
                """
            )
        )

    return cwd


def getHasNoChangesCmd(headExists, staged=False):
    cmd = [
        "git",
        "diff-index",
        "--quiet",
        iif(headExists, "HEAD", emptyGitTree),
        "--",
    ]

    if staged:
        cmd.insert(2, "--cached")

    return cmd
