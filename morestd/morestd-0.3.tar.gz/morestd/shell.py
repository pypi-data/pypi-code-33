#
# morestd: More standard libraries for Python
#
# Copyright 2010-2019 Ferry Boender, released under the MIT license
#

import sys
import os
import subprocess


class CmdError(Exception):
    def __init__(self, msg, exitcode, stderr):
        self.exitcode = exitcode
        self.stderr = stderr
        super().__init__(msg)


def cmd(cmd, input=None, env=None, raise_err=True, env_clean=False,
        auto_decode=True):
    """
    Run command `cmd` in a shell.

    `input` (string) is passed in the process' STDIN.

    If `env` (dict) is given, the environment is updated with it. If
    `env_clean` is `True`, the subprocess will start with a clean environment
    and not inherit the current process' environment. `env` is still applied.

    If `raise_err` is `True` (default), a `CmdError` is raised when the return
    code is not zero.

    Returns a dictionary:

        {
          'stdout': <string>,
          'stderr': <string>,
          'exitcode': <int>
        }

    If `auto_decode` is True, both `stdout` and `stderr` are automatically
    decoded from the system default encoding to unicode strings. This will fail
    if the output is not in that encoding (e.g. it contains binary data).
    Otherwise, stdout and stderr are of type `<bytes>`.
    """
    p_env = {}
    if env_clean is False:
        p_env.update(os.environ)
    if env is not None:
        p_env.update(env)

    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=p_env)
    stdout, stderr = p.communicate(input)

    if auto_decode is True:
        stdout = stdout.decode(sys.getdefaultencoding())
        stderr = stderr.decode(sys.getdefaultencoding())

    if p.returncode != 0 and raise_err is True:
        msg = "Command '{}' returned with exit code {}".format(cmd,
                                                               p.returncode)
        raise CmdError(msg, p.returncode, stderr)

    return {
        'stdout': stdout,
        'stderr': stderr,
        'exitcode': p.returncode
    }


if __name__ == '__main__':
    import doctest
    doctest.testmod()
