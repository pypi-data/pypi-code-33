"""
Ryan Pepper (2018)

__init__.py

Module base
"""

import pytest
import os
name='FolderAnalyse'

dirname = os.path.dirname(__file__)


def runtests():
    """
    runtests()

    Run the test suite for FolderAnalyse

    Notes
    -----
    Adapted from:
    https://docs.pytest.org/en/latest/usage.html#calling-pytest-from-python-code
    """

    pytest.main(['-v', os.path.join(dirname, 'tests')])
