# -*- coding: utf-8 -*-

"""Top-level package for DIALS Regression Data."""

from __future__ import absolute_import, division, print_function

import pytest
from .download import DataFetcher

__all__ = ["pytest_addoption", "dials_data"]
__author__ = """Markus Gerstel"""
__email__ = "dials-support@lists.sourceforge.net"
__version__ = "0.6.0"


def pytest_addoption(parser):
    """Adds '--regression' option to pytest exactly once."""
    if not hasattr(pytest_addoption, "done"):
        parser.addoption(
            "--regression",
            action="store_true",
            default=False,
            help="run regression tests. Download data for those tests if required",
        )
    setattr(pytest_addoption, "done", True)


@pytest.fixture(scope="session")
def dials_data(request):
    """
    Return the location of a regression dataset as py.path object.
    Download the files if they are not on disk already.
    Skip the test if the dataset can not be downloaded.
    """
    if not request.config.getoption("--regression"):
        pytest.skip("Test requires --regression option to run.")
    df = DataFetcher()

    def skip_test_if_lookup_failed(result):
        if not result:
            pytest.skip(
                "Automated download of test data failed. Download manually using dials.data"
            )
        return result

    setattr(df, "result_filter", skip_test_if_lookup_failed)
    return df
