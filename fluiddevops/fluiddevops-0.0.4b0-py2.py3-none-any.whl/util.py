"""
Utilities
=========

"""
import os
import subprocess
import shlex
from platform import python_implementation, python_version_tuple
import shutil

try:
    from os import scandir
except ImportError:
    from scandir import scandir

try:
    from pathlib import Path
    import inspect

    if "site-packages" in inspect.getfile(Path):
        raise ImportError("Path not in standard library.")
except ImportError:
    from pathlib2 import Path

from .logger import logger

PY2 = python_version_tuple()[0] == "2"


def run(cmd, output=False):
    logger.info(cmd)
    cmd = shlex.split(cmd)
    if output:
        output = subprocess.check_output(cmd)
        output = output.decode("utf8")
        return output
    else:
        subprocess.call(cmd)


def chdir(d):
    logger.info("cd {}".format(d))
    if PY2 or python_implementation() != "CPython":
        d = str(d)
    os.chdir(d)


def rmtree(d):
    logger.info("rm -r {}".format(d))
    if PY2 or python_implementation() != "CPython":
        d = str(d)
    shutil.rmtree(d)


def rwalk(bottom, topdown=False, onerror=None, followlinks=False):
    """Reverse variant of os.walk. Walks from the bottom directory till
    root.

    Parameters
    ----------
    bottom : str
    topdown : bool
    onerror : callable
    followlinks : bool

    Returns
    -------
    generator

    """
    try:
        bottom = os.fspath(bottom)
    except AttributeError:
        pass
    dirs = []
    nondirs = []

    bottomup = not topdown
    try:
        scandir_it = scandir(bottom)
    except OSError as error:
        if onerror is not None:
            onerror(error)
        return

    # Not supported in the backport
    # See: https://github.com/benhoyt/scandir/issues/60
    # with scandir_it:
    while True:
        try:
            try:
                entry = next(scandir_it)
            except StopIteration:
                break

        except OSError as error:
            if onerror is not None:
                onerror(error)
            return

        try:
            is_dir = entry.is_dir()
        except OSError:
            is_dir = False

        if is_dir:
            dirs.append(entry.name)
        else:
            nondirs.append(entry.name)

    try:
        scandir_it.close()
    except AttributeError:
        pass

    new_path = os.path.dirname(bottom)

    if bottomup:
        yield bottom, dirs, nondirs

    # Recurse into parent-directories
    if bottom != new_path:  # Avoid RecursionError when at the root directory
        walk_new_path = rwalk(new_path, topdown, onerror, followlinks)
        # if PY2:
        for x in walk_new_path:
            yield x
        # else:
        # SyntaxError: Python 2
        # yield from walk_new_path

        if followlinks and os.path.islink(new_path):
            walk_new_link = rwalk(
                os.path.abspath(new_path), topdown, onerror, followlinks
            )
            # if PY2:
            for x in walk_new_link:
                yield x
            # else:
            #     yield_from(walk_new_link)

    if not bottomup:
        yield bottom, dirs, nondirs
