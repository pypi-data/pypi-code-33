# encoding: utf-8
# pylint: disable=missing-docstring,redefined-outer-name,no-self-use

from __future__ import unicode_literals

import os

import pytest

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@pytest.fixture(scope="module")
def source_file():
    return os.path.relpath(os.path.join(DATA_PATH, "polarion_docstrings.py"))
