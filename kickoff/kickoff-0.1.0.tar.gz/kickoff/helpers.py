import os
from pathlib import Path
from textwrap import dedent
from .logger import log

KICKOFF_ERROR_CODE = 255

def abort(exit_code=KICKOFF_ERROR_CODE):
    exit(exit_code)

def in_dev_mode():
    """KICKOFF_DEV_MODE is unset, empty, or '0' -> False, otherwise -> True"""
    val = os.getenv('KICKOFF_DEV_MODE')
    return bool(val) and val != '0'


def load_customize_file():
    """Load kickoffcustomize.py from CWD"""
    try:
        import kickoffcustomize
    except ModuleNotFoundError:
        log.debug(f"kickoffcustomize.py not found")
    except Exception as exc:
        log.warning(f"Error in kickoffcustomize.py: {exc}")


def parse_args(argv):
    exe_name = Path(argv[0]).name

    try:
        kickoff_arg = argv[1]
    except:
        print_usage(exe_name)
        abort()

    app_args = argv[2:]

    sep = ':'
    parts = kickoff_arg.split(sep)
    field1 = sep.join(parts[:-1])
    field2 = parts[-1]

    if len(parts) == 1:
        path = field2
        name = None
    else:
        path = field1
        name = field2

    if not name:
        name = None

    if not path:
        path = None

    log.debug(f"Resource name: {name!r}")
    log.debug(f"Resource path: {path!r}")

    return path, name, app_args

def print_usage(exe_name):
    print(dedent(f"""
    Turns your Python script or module into an application with decent CLI.

    Usage:
        # Running a script
        {exe_name} PATH[:] COMMAND ... [ARGS ...]

        Note: Semicolon at the end of PATH is required when PATH itself includes semicolons.

        # Running a module
        {exe_name} [PATH]:MODULE COMMAND ... [ARGS ...]

        Note: If PATH is skipped, MODULE is expected to be available in system locations or on PYTHONPATH.

    Examples:
        {exe_name} some\\relative\\location\\myscript.py foo --bar 123
        {exe_name} C:\\some\\absolute\\location\\myscript.py: foo --bar 123
        {exe_name} C:\\some\\absolute\\location:mymodule foo --bar 123
        {exe_name} :re findall "b\\w*d" "beer bear bird bore beard"

    """).strip())


