# -*- coding: utf-8 -*-
"""
Run pytest --collect-only and generate JSONs.
"""

from __future__ import absolute_import, unicode_literals

import logging
import os
import subprocess
import sys

from cfme_testcases import consts
from cfme_testcases.exceptions import TestcasesException

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)


def json_ready(tests_data_json):
    """Check if the needed JSON file is already available."""
    if tests_data_json and not os.path.exists(tests_data_json):
        raise TestcasesException(
            "The testcases JSON file `{}` doesn't exist.".format(tests_data_json)
        )
    if not tests_data_json:
        return False
    return True


def collect(pytest_collect, tests_data_json):
    """Collects testcases data."""
    retval = None

    if not json_ready(tests_data_json):
        tests_data_json = consts.TESTS_DATA_JSON
        retval = run_pytest(pytest_collect)

    return retval, tests_data_json


def check_json():
    """Check that the JSON files were generated."""
    if not os.path.exists(consts.TESTS_DATA_JSON):
        raise TestcasesException("The JSON file `{}` doesn't exist.".format(consts.TESTS_DATA_JSON))


def check_environment():
    """Checks the environment for running pytest."""
    if not os.path.exists(".git"):
        raise TestcasesException("Not launched from the top-level directory.")
    # check that running in virtualenv
    if not hasattr(sys, "real_prefix"):
        raise TestcasesException("Not running in virtual environment.")


def cleanup():
    """Deletes JSON file generated during previous runs."""
    try:
        os.remove(consts.TESTS_DATA_JSON)
    except OSError:
        pass


def run_pytest(pytest_collect):
    """Runs the pytest command."""
    if not pytest_collect:
        raise TestcasesException(
            "The `pytest_collect` command for collecting testcases was not specified."
        )

    pytest_retval = 250
    check_environment()
    cleanup()

    pytest_args = pytest_collect.split(" ")

    logger.info("Generating the JSON using '%s'", pytest_collect)
    with open(os.devnull, "w") as devnull:
        pytest_proc = subprocess.Popen(pytest_args, stdout=devnull, stderr=devnull)
        try:
            pytest_retval = pytest_proc.wait()
        # pylint: disable=broad-except
        except Exception:
            try:
                pytest_proc.terminate()
            except OSError:
                pass
            pytest_proc.wait()

    check_json()
    return pytest_retval
