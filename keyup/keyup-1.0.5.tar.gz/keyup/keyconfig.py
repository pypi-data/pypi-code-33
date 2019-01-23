"""
Summary.

    Display of configuration file contents

"""

import os
import sys
import json
from keyup import about, configuration, logd, __version__
from keyup.statics import PACKAGE, CONFIG_SCRIPT, local_config
from keyup.script_utils import debug_mode
from pyaws.utils import stdout_message, export_json_object


try:
    from keyup.oscodes_unix import exit_codes
    splitchar = '/'
except Exception:
    from keyup.oscodes_win import exit_codes    # non-specific os-safe codes
    splitchar = '\\'


def display_content(data_object, header=None, halt=False):
    """
    Summary.

        Display contents of object correctly whether display on a
        terminal (tty) or redirected to a file

    """
    if header:
        print('\n  ' + str(header) + '\n')
    try:
        if is_tty():
            export_json_object(dict_obj=data_object, logging=False)
        else:
            print(json.dumps(data_object, indent=4))
    except Exception:
        print(data_object)
    if halt:
        sys.exit(0)
    return True


def is_tty():
    """
    Summary:
        Determines if output is displayed to the screen or redirected
    Returns:
        True if tty terminal | False is redirected, TYPE: bool
    """
    return sys.stdout.isatty()


def option_configure(debug=False, path=None):
    """
    Summary:
        Initiate configuration menu to customize keyup runtime options.
        Console script ```keyconfig``` invokes this option_configure directly
        in debug mode to display the contents of the local config file (if exists)
    Args:
        :path (str): full path to default local configuration file location
        :debug (bool): debug flag, when True prints out contents of local
         config file
    Returns:
        TYPE (bool):  Configuration Success | Failure
    """
    if CONFIG_SCRIPT in sys.argv[0]:
        debug = True    # set debug mode if invoked from CONFIG_SCRIPT

    if path is None:
        path = local_config['PROJECT']['CONFIG_PATH']

    if debug:
        if os.path.isfile(path):
            display_content(data_object=local_config, halt=True)

        else:
            msg = """  Local config file does not yet exist. Run:

            $ keyup --configure """

            debug_mode(
                header=msg,
                data_object={'CONFIG_PATH': path},
                halt=True
            )

    r = configuration.init(debug, path)
    return r
