#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `marzano` package."""

import pytest

from click.testing import CliRunner

from marzano import powerlaw
from marzano import cli


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    grades = [1, 2, 3, 4]
    assert powerlaw(grades) == 4.0


def test_zero():
    grades = [0, 1, 2, 3, 4]
    assert powerlaw(grades) is not 0


def test_documented_examples():
    grades = [1, 2, 3, 4]
    assert int(powerlaw(grades)) is 4

    grades = [1, 3, 2, 4]
    assert int(powerlaw(grades)) is 3

    grades = [2, 4, 1, 3]
    assert int(powerlaw(grades)) is 2

    grades = [4, 3, 2, 1]
    assert int(powerlaw(grades)) is 1


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main, input="1\n2\n3\n\n")
    assert result.exit_code == 0
    assert "Power Score: 3" in result.output
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
