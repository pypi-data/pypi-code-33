# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 22.09.2015
"""


def runtests():
    import sys
    import pytest
    from os import environ
    from os.path import dirname, join, normpath
    cfg_path = normpath(join(dirname(__file__), '../../../setup.cfg'))

    args = sys.argv[1:]
    if not args or args[0].startswith('-'):
        args = args + ['cykooz.buildout.venv']
    args = ['-c', cfg_path] + args
    environ['IS_TESTING'] = 'True'
    pytest.main(args)
