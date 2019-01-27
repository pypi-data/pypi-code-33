#
# morestd: More standard libraries for Python
#
# Copyright 2010-2019 Ferry Boender, released under the MIT license
#

import subprocess


def cmd(cmd, input=None, env=None):
    """
    Run command `cmd` in a shell. `input` (string) is passed in the
    process' STDIN.

    Returns a dictionary: `{'stdout': <string>, 'stderr': <string>, 'exitcode':
    <int>}`.
    """
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(input)
    return {
        'stdout': stdout,
        'stderr': stderr,
        'exitcode': p.returncode
    }


if __name__ == '__main__':
    import doctest
    doctest.testmod()
