#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `appel` package."""


import unittest
from click.testing import CliRunner

from appel import cli

class TestAppel(unittest.TestCase):
    """Tests for `appel` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        help_result = runner.invoke(cli.cli, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
