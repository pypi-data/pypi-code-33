import os
import unittest

from ..io import read_yaml

current_dir = os.path.dirname(os.path.realpath(__file__))
fixtures_path = "{}/fixtures".format(current_dir)


def test_load():
    expected = {"foo": "bar"}
    got = read_yaml("{}/test_load.yaml".format(fixtures_path))
    assert expected == got
