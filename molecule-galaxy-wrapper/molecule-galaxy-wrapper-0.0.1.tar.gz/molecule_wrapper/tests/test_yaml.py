import os
import unittest

from ..yaml import load

current_dir = os.path.dirname(os.path.realpath(__file__))
fixtures_path = "{}/fixtures".format(current_dir)


def test_load():
    expected = {"foo": "bar"}
    got = load("{}/test_load.yaml".format(fixtures_path))
    assert expected == got
