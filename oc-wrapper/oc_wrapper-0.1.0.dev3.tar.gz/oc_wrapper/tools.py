from subprocess import CalledProcessError


def called_process_error_repr(e):
    # type: (CalledProcessError) -> str
    cmd = e.cmd

    if isinstance(cmd, list):
        cmd = ' '.join(cmd)

    return "Execution of '{cmd}' failed with error code {code} and message '{msg}'. Console output: '{out}'.".format(
        cmd=cmd, code=e.returncode, out=e.output, msg=e.message)
