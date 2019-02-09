#! /usr/bin/env python3
""" Script to run Vigil."""
# Standard modules
import gettext
import logging
import os
import sys

# External dependencies
import plac

# Local modules
sys.path.insert(0, os.path.abspath('.'))
# pylint: disable=wrong-import-position
from vigil import cli
from vigil.utils import logger
# pylint: enable=wrong-import-position

gettext.install('vigil', 'locale')

def main():
    """
    Main function to run Vigil.
    """
    logger.setup_logging()
    log = logging.getLogger('vigil')

    localization = gettext.translation('vigil', localedir='locale', fallback=True)
    localization.install()

    try:
        plac.Interpreter.call(cli.CLI, prompt='vigil> ')
    except Exception as ex:  # pylint: disable=broad-except
        log.exception(ex)


if __name__ == '__main__':
    main()
