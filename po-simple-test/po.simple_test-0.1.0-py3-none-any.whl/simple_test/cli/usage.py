from textwrap import dedent

usage = dedent(
    f"""
    Usage
      simple-test [options]
      simple-test (--help | --version)

    Options
      --project-dir  the project dir from which tests are found. Defaults
                     to `os.getcwd()`
      --silent       a flag which disables output and prevents the reporter from
                     being called.
      --reporter     module name with a 'report' function.  The default reporter
                     is 'simple_test_default_reporter'.  Relative modules e.g.
                     "..myModule" are not yet supported.

    Returns an exit code of
        0 for a successful run
        1 for a failed run
        2 for an error
    """
)
