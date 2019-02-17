import os
import unittest
from unittest.mock import Mock

from analyze_objects.obj_analyzer import DumpbinParser, NmParser


_FOO_DUMPBIN_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "foo_dumpbin_output.txt")
with open(_FOO_DUMPBIN_OUTPUT_PATH, "r", encoding="utf8") as f:
    _FOO_DUMPBIN_OUTPUT = f.read()

_INVALID_DUMPBIN_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "invalid_dumpbin_output.txt")
with open(_INVALID_DUMPBIN_OUTPUT_PATH, "r", encoding="utf8") as f:
    _INVALID_DUMPBIN_OUTPUT = f.read()

_FOO_NM_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "foo_nm_output.txt")
with open(_FOO_NM_OUTPUT_PATH, "r", encoding="utf8") as f:
    _FOO_NM_OUTPUT = f.read()

_INVALID_NM_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "invalid_nm_output.txt")
with open(_INVALID_NM_OUTPUT_PATH, "r", encoding="utf8") as f:
    _INVALID_NM_OUTPUT = f.read()


class TestDumpbinParser(unittest.TestCase):

    def test_analyze_foo_obj(self):
        dumpbin_caller_mock = Mock()
        dumpbin_caller_mock.return_value = _FOO_DUMPBIN_OUTPUT
        dumpbin_parser = DumpbinParser(dumpbin_caller_mock)
        analyzed_foo = dumpbin_parser.analyze("foo.obj")
        dumpbin_caller_mock.assert_called_once_with("foo.obj")
        self.assertTrue(analyzed_foo.contains_defined_external_symbol("some_defined_foo_symbol"))
        self.assertTrue(analyzed_foo.contains_undefined_external_symbol("some_undefined_foo_symbol"))
        self.assertFalse(analyzed_foo.contains_undefined_external_symbol("some_defined_foo_symbol"))
        self.assertFalse(analyzed_foo.contains_defined_external_symbol("some_undefined_foo_symbol"))

    def test_analyze_raises_on_invalid_format(self):
        dumpbin_caller_mock = Mock()
        dumpbin_caller_mock.return_value = _INVALID_DUMPBIN_OUTPUT
        dumpbin_parser = DumpbinParser(dumpbin_caller_mock)
        self.assertRaises(RuntimeError, dumpbin_parser.analyze, "bar.txt")
        dumpbin_caller_mock.assert_called_once_with("bar.txt")


class TestNmParser(unittest.TestCase):

    def test_analyze_foo_obj(self):
        nm_caller_mock = Mock()
        nm_caller_mock.return_value = _FOO_NM_OUTPUT
        nm_parser = NmParser(nm_caller_mock)
        analyzed_foo = nm_parser.analyze("foo.o")
        nm_caller_mock.assert_called_once_with("foo.o")
        self.assertTrue(analyzed_foo.contains_defined_external_symbol("some_defined_foo_symbol"))
        self.assertTrue(analyzed_foo.contains_undefined_external_symbol("some_undefined_foo_symbol"))
        self.assertFalse(analyzed_foo.contains_undefined_external_symbol("some_defined_foo_symbol"))
        self.assertFalse(analyzed_foo.contains_defined_external_symbol("some_undefined_foo_symbol"))

    def test_analyze_raises_on_invalid_format(self):
        nm_caller_mock = Mock()
        nm_caller_mock.return_value = _INVALID_NM_OUTPUT
        nm_parser = NmParser(nm_caller_mock)
        self.assertRaises(RuntimeError, nm_parser.analyze, "bar.txt")
        nm_caller_mock.assert_called_once_with("bar.txt")
