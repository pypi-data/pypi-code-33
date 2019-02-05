import warnings


def async_run( cmds, on_stdout, on_stderr, check = False, stdin = None ):
    warnings.warn( "Deprecated - use subprocess_helper" )
    from mhelper import subprocess_helper
    subprocess_helper.execute( cmds,
                               on_stdout = on_stdout,
                               on_stderr = on_stderr,
                               err = check,
                               tx = stdin )
