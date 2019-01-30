import subprocess
from typing import Any


def run(*cmd: Any,
        out=subprocess.PIPE,
        err=subprocess.DEVNULL,
        to_string=True,
        check=True,
        **kwargs) -> subprocess.CompletedProcess:
    """subprocess.run with a better API.

    :param cmd: A list of commands to execute as parameters.
                Parameters will be passed-in to ``str()`` so they
                can be any object that can handle str().
    :param out: As ``subprocess.run.stdout``.
    :param err: As ``subprocess.run.stderr``.
    :param to_string: As ``subprocess.run.universal_newlines``.
    :param check: As ``subprocess.run.check``.
    :param kwargs: Any other parameters that ``subprocess.run``
                   accepts.
    :return: The result of executing ``subprocess.run``.
    """
    return subprocess.run(tuple(str(c) for c in cmd),
                          stdout=out,
                          stderr=err,
                          universal_newlines=to_string,
                          check=check,
                          **kwargs)
