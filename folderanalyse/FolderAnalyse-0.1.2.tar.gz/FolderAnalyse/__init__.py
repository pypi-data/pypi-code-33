import pytest
import glob
import os
name='FolderAnalyse'

path = os.path.dirname(__file__)


def runtests():
    """
    runtests()
    
    Run the test suite for FolderAnalyse
    
    Notes
    -----
    Adapted from:
    https://docs.pytest.org/en/latest/usage.html#calling-pytest-from-python-code
    """

    from pytest import main
    pytest.main(['-v', 'tests'])


