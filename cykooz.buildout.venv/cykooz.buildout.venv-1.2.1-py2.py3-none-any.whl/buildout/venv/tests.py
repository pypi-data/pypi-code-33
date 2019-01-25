# -*- coding: utf-8 -*-
"""
:Authors: cykooz
:Date: 11.08.2016
"""
from __future__ import print_function, unicode_literals

import os
import platform
from collections import namedtuple

import pytest
import zc.buildout.testing

from .extension import PY_LESS_33


BUILDOUT_CFG = '''
[buildout]
extensions = cykooz.buildout.venv
eggs-directory = eggs
parts =
'''


@pytest.fixture(name='buildout_env')
def buildout_env_fixture():
    TestEnv = namedtuple('TestEnv', ['globs'])
    test_env = TestEnv(globs={})
    zc.buildout.testing.buildoutSetUp(test_env)
    zc.buildout.testing.install('cykooz.buildout.venv', test_env)
    if PY_LESS_33:
        zc.buildout.testing.install('virtualenv', test_env)
    try:
        yield test_env.globs
    finally:
        zc.buildout.testing.buildoutTearDown(test_env)


def test_extension(buildout_env):
    sample_buildout = buildout_env['sample_buildout']
    write = buildout_env['write']
    system = buildout_env['system']
    buildout = buildout_env['buildout']

    write(sample_buildout, 'buildout.cfg', BUILDOUT_CFG)
    res = system(buildout)
    assert 'Installing virtual python environment...' in res
    assert 'Virtual python environment was installed.' in res
    assert 'Recreating buildout script.' in res
    assert 'Restarting buildout under virtual python environment.' in res

    parts_dir = os.path.join(sample_buildout, 'parts')
    names = sorted(os.listdir(parts_dir))
    assert names == ['venv']

    venv_bin_path = os.path.join(parts_dir, 'venv', 'bin')
    if platform.system() == 'Windows':
        venv_bin_path = os.path.join(parts_dir, 'venv', 'Scripts')

    names = os.listdir(venv_bin_path)
    assert any(name.startswith('python') for name in names)

    buildout_script = buildout
    if not os.path.exists(buildout_script):
        buildout_script += '-script.py'  # For Windows

    with open(buildout_script, 'rt') as f:
        text = f.read()
    assert venv_bin_path in text

    res = system(buildout)
    assert 'Installing virtual python environment...' not in res
    assert 'Virtual python environment was installed.' not in res
    assert 'Recreating buildout script.' not in res
    assert 'Restarting buildout under virtual python environment.' not in res
