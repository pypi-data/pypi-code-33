import sys
import unittest

from argparse import ArgumentParser
from unittest.mock import MagicMock

from console_cone.get_parser import get_parser


class ArgumentParserError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class TestableArgumentParser(ArgumentParser):

    def error(self, message):
        self.print_usage(sys.stderr)
        raise ArgumentParserError(message)

    def exit(self, status=0, message=None):
        if status != 0:
            raise ArgumentParserError(message)

    def _print_message(self, message, file=None):
        pass


class TestGetParser(unittest.TestCase):

    def setUp(self):
        self.parser = get_parser(TestableArgumentParser())

    def test_missing_command_fail(self):
        with self.assertRaises(ArgumentParserError):
            self.parser.parse_args([])

    def test_command_help(self):
        args = self.parser.parse_args(["help"])

        self.assertEqual(args.command, "help")

    def test_command_test(self):
        args = self.parser.parse_args(["test"])

        self.assertEqual(args.command, "test")

    def test_command_test_help(self):
        args = self.parser.parse_args(["test", "--help"])

        self.assertEqual(args.command, "test")

    def test_command_deploy_help(self):
        args = self.parser.parse_args(["deploy", "--help"])

        self.assertEqual(args.command, "deploy")

    def test_command_deploy(self):
        args = self.parser.parse_args(["deploy"])

        self.assertEqual(args.command, "deploy")

    def test_command_version(self):
        args = self.parser.parse_args(["version"])

        self.assertEqual(args.command, "version")
