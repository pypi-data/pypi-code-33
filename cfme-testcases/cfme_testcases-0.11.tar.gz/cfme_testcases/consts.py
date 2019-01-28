# -*- coding: utf-8 -*-
"""
Constants.
"""

from __future__ import unicode_literals

TESTS_DATA_JSON = "tests_data.json"

XUNIT = "xunit"
TEST_CASE = "testcases"
REQUIREMENTS = "requirements"

# file_type: (key, file_name)
OUT_FILES = {
    "testcases": (None, TEST_CASE),
    "testsuites": (None, XUNIT),
    "requirements": (None, REQUIREMENTS),
    "init_testsuites": ("init", XUNIT),
    "missing_testcases": ("missing", TEST_CASE),
    "missing_testsuites": ("missing", XUNIT),
    "updated_testcases": ("update", TEST_CASE),
}
