
# The library doesn't yet have a way to "undo", so we are only going to execute once.

import os, sys
from os.path import dirname, join

import autoconfig
autoconfig.init(searchfrom=__file__, env=['env', 'other'], relpath='local',
                otherfiles=['one.cfg', 'two.cfg'])


def test_filename():
    "Ensure the path of the config file is made available"
    fqn = join(dirname(__file__), '.config')
    assert autoconfig.get_filename() == fqn


def test_otherfiles():
    "Ensure otherfiles is read and read in order."
    assert os.environ.get('A') == 'TWO'  # should have been defined in one but overridden by two
    assert os.environ.get('B') == 'ONE'
    assert os.environ.get('C') == 'TWO'


def test_vars():
    "Ensure environment variables are set"
    assert os.environ.get('TESTA') == 'a'
    assert os.environ.get('TESTB') == 'b'


def test_othervars():
    "Ensure environment variables are set from [other]"
    assert os.environ.get('TESTOTHER') == 'a'


def test_import():
    "Ensure the [import] section is processed"
    # The .config file imports the uuid package.  Notice it isn't imported directly in this
    # module but it is in sys.modules.  (Since we're using pytest, there could be a ton of
    # stuff imported.  Choose a module that it doesn't import by ensuring this fails before
    # putting a different module in the config file.)
    keys = list(sys.modules.keys())  # for a nicer assertion
    assert 'uuid' in keys


def test_syspath():
    "Ensure [env] PYTHONPATH entries were added to the system path"
    # The regular env has these: lib:/var/autoconfig
    #
    # Since 'lib' is relative, it will be relative to the .config file which is this file's
    # directory.  The other is absolute, so it should be on the path too.
    relative = join(dirname(__file__), 'lib')
    assert relative in sys.path

    absolute = '/var/autoconfig'
    assert absolute in sys.path


def test_othersyspath():
    "Ensure [other] PYTHONPATH entries were added to the system path"
    # PYTHONPATH=otherlib:/var/otherautoconfig
    relative = join(dirname(__file__), 'otherlib')
    assert relative in sys.path

    absolute = '/var/otherautoconfig'
    assert absolute in sys.path


def test_relpath():
    "Ensure relpath was set local to this file."
    fqn = join(dirname(__file__), 'local')
    assert fqn in sys.path
