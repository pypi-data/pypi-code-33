"""Tests the pyinilint.py module."""

import configparser
import logging
import unittest

from pyinilint.pyinilint import get_command_line_argument_parser
from pyinilint.pyinilint import get_log_level
from pyinilint.pyinilint import validate_args
from pyinilint.pyinilint import get_config_parser
from pyinilint.pyinilint import readable_paths
from pyinilint.pyinilint import lint
from pyinilint.pyinilint import serialize

GOOD1_PATH = 'pyinilint/tests/good1.ini'
GOOD2_PATH = 'pyinilint/tests/good2.ini'
BAD_PATH = 'pyinilint/tests/bad.ini'


class TestGetCommandLineArgumentParser(unittest.TestCase):
    """ Test the get_command_line_argument_parser() function."""

    def setUp(self):
        """Construct objects used for testing."""
        self.parser = get_command_line_argument_parser()

    def test_basic(self):
        """Test the basic option."""
        self.assertTrue(
            self.parser.parse_args(['-b', GOOD1_PATH]).basic)
        self.assertTrue(
            self.parser.parse_args(['--basic', GOOD1_PATH]).basic)
        self.assertFalse(
            self.parser.parse_args([GOOD1_PATH]).basic)

    def test_debug(self):
        """Test the debug option."""
        self.assertTrue(
            self.parser.parse_args(['-d', GOOD1_PATH]).debug)
        self.assertTrue(
            self.parser.parse_args(['--debug', GOOD1_PATH]).debug)
        self.assertFalse(
            self.parser.parse_args([GOOD1_PATH]).debug)

    def test_encoding(self):
        """Test the encoding option."""
        self.assertEqual(
            self.parser.parse_args(
                ['-e', 'ascii', GOOD1_PATH]
            ).encoding, 'ascii')
        self.assertEqual(
            self.parser.parse_args(
                ['--encoding', 'ascii', GOOD1_PATH]
            ).encoding, 'ascii')
        self.assertIsNone(
            self.parser.parse_args([GOOD1_PATH]).encoding)

    def test_merge(self):
        """Test the merge option."""
        self.assertTrue(
            self.parser.parse_args(['-m', GOOD1_PATH]).merge)
        self.assertTrue(
            self.parser.parse_args(['--merge', GOOD1_PATH]).merge)
        self.assertFalse(
            self.parser.parse_args([GOOD1_PATH]).merge)

    def test_output(self):
        """Test the output option."""
        self.assertTrue(
            self.parser.parse_args(['-o', GOOD1_PATH]).output)
        self.assertTrue(
            self.parser.parse_args(['--output', GOOD1_PATH]).output)
        self.assertFalse(
            self.parser.parse_args([GOOD1_PATH]).output)

    def test_raw(self):
        """Test the raw option."""
        self.assertTrue(
            self.parser.parse_args(['-r', GOOD1_PATH]).raw)
        self.assertTrue(
            self.parser.parse_args(['--raw', GOOD1_PATH]).raw)
        self.assertFalse(
            self.parser.parse_args([GOOD1_PATH]).raw)

    def test_verbose(self):
        """Test the verbose option."""
        self.assertTrue(
            self.parser.parse_args(['-v', GOOD1_PATH]).verbose)
        self.assertTrue(
            self.parser.parse_args(['--verbose', GOOD1_PATH]).verbose)
        self.assertFalse(
            self.parser.parse_args([GOOD1_PATH]).verbose)

    def test_paths(self):
        """Test the paths argument."""
        self.assertEqual(
            self.parser.parse_args(['-v', GOOD1_PATH]).paths,
            [GOOD1_PATH])
        self.assertEqual(
            self.parser.parse_args(['--verbose', GOOD1_PATH]).paths,
            [GOOD1_PATH])
        self.assertEqual(
            self.parser.parse_args([GOOD1_PATH]).paths,
            [GOOD1_PATH])
        self.assertEqual(
            self.parser.parse_args([GOOD1_PATH, 'test/bad.ini']).paths,
            [GOOD1_PATH, 'test/bad.ini'])


class TestGetLogLevel(unittest.TestCase):
    """ Test the get_log_level(args) function."""

    def setUp(self):
        """Construct objects used for testing."""
        self.parser = get_command_line_argument_parser()

    def test_debug(self):
        """Test the logging mode when debug option is used."""
        args = self.parser.parse_args(['--debug', GOOD1_PATH])
        self.assertEqual(get_log_level(args), logging.DEBUG)

    def test_verbose(self):
        """Test the logging mode when verbose option is used."""
        args = self.parser.parse_args(['--verbose', GOOD1_PATH])
        self.assertEqual(get_log_level(args), logging.INFO)

    def test_default(self):
        """Test the logging mode when no debug or verbose option is used."""
        args = self.parser.parse_args([GOOD1_PATH])
        self.assertEqual(get_log_level(args), logging.WARNING)


class TestValidateArgs(unittest.TestCase):
    """ Test the validate_args(args) function."""

    def setUp(self):
        """Construct objects used for testing."""
        self.parser = get_command_line_argument_parser()

    def test_basic_and_raw(self):
        """Test use of basic and raw options causes exception."""
        args = self.parser.parse_args(['--basic', '--raw', GOOD1_PATH])
        with self.assertRaises(ValueError):
            validate_args(args)

    def test_debug_and_verbose(self):
        """Test use of debug and verbose options causes exception."""
        args = self.parser.parse_args(['--debug', '--verbose', GOOD1_PATH])
        with self.assertRaises(ValueError):
            validate_args(args)


class TestReadablePaths(unittest.TestCase):
    """Test the readable_paths(paths) function."""

    def test_good_paths(self):
        """Test readable_paths(paths) when good paths are used."""
        rpaths = readable_paths([GOOD1_PATH, GOOD2_PATH])
        self.assertIn(GOOD1_PATH, rpaths)
        self.assertIn(GOOD2_PATH, rpaths)

    def test_non_existant_paths(self):
        """Test readable_paths(paths) with non-existant path."""
        with self.assertRaises(FileNotFoundError):
            readable_paths(['does/not/exist.ini'])


class TestGetConfigParser(unittest.TestCase):
    """ Test the get_config_parser(args) function."""

    def setUp(self):
        """Construct objects used for testing."""
        self.parser = get_command_line_argument_parser()

    def test_raw(self):
        """Test the config_parser when raw option is used."""
        args = self.parser.parse_args(['--raw', GOOD1_PATH])
        parser = get_config_parser(args)
        parser.read(GOOD1_PATH)
        self.assertEqual(
            parser.get('interpolation-test', 'no-interpolation'),
            'my-value')
        self.assertEqual(
            parser.get('interpolation-test', 'basic-interpolation'),
            '%(my-default)s')
        self.assertEqual(
            parser.get('interpolation-test', 'extended-interpolation'),
            '${my-default}')

    def test_basic(self):
        """Test the config_parser when basic option is used."""
        args = self.parser.parse_args(['--basic', GOOD1_PATH])
        parser = get_config_parser(args)
        parser.read(GOOD1_PATH)
        self.assertEqual(
            parser.get('interpolation-test', 'no-interpolation'),
            'my-value')
        self.assertEqual(
            parser.get('interpolation-test', 'basic-interpolation'),
            '42')
        self.assertEqual(
            parser.get('interpolation-test', 'extended-interpolation'),
            '${my-default}')

    def test_default(self):
        """Test config_parser when default extended interpolation is used."""
        args = self.parser.parse_args([GOOD1_PATH])
        parser = get_config_parser(args)
        parser.read(GOOD1_PATH)
        self.assertEqual(
            parser.get('interpolation-test', 'no-interpolation'),
            'my-value')
        self.assertEqual(
            parser.get('interpolation-test', 'basic-interpolation'),
            '%(my-default)s')
        self.assertEqual(
            parser.get('interpolation-test', 'extended-interpolation'),
            '42')


class TestLint(unittest.TestCase):
    """Test the lint(config, paths, args) function."""

    def setUp(self):
        """Construct objects used for testing."""
        self.parser = get_command_line_argument_parser()

    def test_good_ini_file(self):
        """Test the linting of a good INI file."""
        args = self.parser.parse_args([GOOD1_PATH])
        config = get_config_parser(args)
        rpaths = readable_paths(args.paths)
        new_config = lint(config, rpaths, args)
        self.assertTrue(new_config)

    def test_bad_ini_file(self):
        """Test the linting of a bad INI file."""
        args = self.parser.parse_args([BAD_PATH])
        config = get_config_parser(args)
        rpaths = readable_paths(args.paths)

        with self.assertRaises(configparser.Error):
            lint(config, rpaths, args)


class TestSerialize(unittest.TestCase):
    """Test the serialize(config) function."""

    def test_raw_interpolation(self):
        """Test serializing with raw (no) interpolation."""
        config = configparser.ConfigParser(interpolation=None)

        my_section = "my_section"
        my_key = "my_key"
        my_value = "my_value"

        config.add_section(my_section)
        config.set(my_section, my_key, my_value)

        serialized = "[" + my_section + "]\n" + my_key \
            + " = " + my_value + "\n\n"
        self.assertEqual(serialize(config), serialized)


if __name__ == '__main__':
    unittest.main()
