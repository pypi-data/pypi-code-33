import os
import unittest
import tempfile

from molecule_wrapper.io import read_yaml, write_yaml

current_dir = os.path.dirname(os.path.realpath(__file__))
fixtures_path = "{}/fixtures".format(current_dir)


def test_load():
    expected = {"foo": "bar"}
    got = read_yaml("{}/test_load.yaml".format(fixtures_path))
    assert expected == got


def test_dump():
    content = read_yaml("{}/test_load.yaml".format(fixtures_path))
    _, filename = tempfile.mkstemp()

    write_yaml(filename, content)

    with open(filename, 'r', encoding='utf-8') as stream:
        content = stream.read()
        assert content == "---\nfoo: bar\n"

    os.remove(filename)
