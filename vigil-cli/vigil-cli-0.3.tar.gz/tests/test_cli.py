# Standard modules
import os

# External dependencies
import plac
import pytest

# Local modules
from .context import vigil
from vigil.config import Config
from vigil import cli


@pytest.fixture
def setup(monkeypatch, testfile, config, configfile):
    monkeypatch.setattr(Config, '_savepath', lambda x: testfile)
    config.save()
    return config


@pytest.mark.skip(reason="broken until new version of plac is released")
def test_cli(setup):
    placet = os.path.join('tests', 'data', 'cli.placet')
    plac.Interpreter(cli.CLI).doctest(open(placet), verbose=True)
