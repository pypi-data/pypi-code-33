#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""MockQuerPy

This module contains the logic for running the mockquerpy test library. it
swaps out the bigquery module in python for a mock module within a context
manager or a decorator. This is to enable easy unittesting of bigquery.

The mockquerpy can be used either using the context manager or using a
decorator. See output from their docstrings on use below.

"""


# Std lib
from sys import modules
from functools import wraps
import re
import traceback

# Mockclasses and helperfunctions
from .mockquerpy_mocks import _MockBigQuery, _set_test_data


class MockQuerPy():
    """MockQuerPy context manager

    Utilized the python context manager design pattern in order to provide a
    clean interface for enabling mocking of bigquery in the code. Further it
    alters the sys.modules and sets it to the mocking library within the
    context.

    Example Usage
    -------------
    Can be used with the python `with` keyword::

        with MockQuerPy(TEST_DATA) as m:
            m.test_data = OTHER_TEST_DATA
            bigquery.query(q).result() # Gives back OTHER_TEST_DATA
    """

    def __init__(self, data=None, assert_call=True):
        if assert_call:
            VALID_MOCKQUERPY_CALL_RE = r'with MockQuerPy(.*) as bigquery:'
            (filename, line_number, func_name, text) = traceback.extract_stack()[-2]
            assert re.match(VALID_MOCKQUERPY_CALL_RE, text),\
                "Invalid use! Got:\n\t'%s'\nMust match Regex: \n\t'%s'" %\
                (text, VALID_MOCKQUERPY_CALL_RE)
        self.set_test_data(data=data)

    @staticmethod
    def set_test_data(data):
        _set_test_data(data)

    def __enter__(self):
        self.context_entered = True
        self.real_bq = modules['google.cloud.bigquery']
        modules['google.cloud.bigquery'] = _MockBigQuery
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.set_test_data(None)
        modules['google.cloud.bigquery'] = self.real_bq


def mockquerpy_wrap(func):
    """MockQuerPy decorator

    Wrapping a function with this decorator will make it use mockquerpy
    when trying to use bigquery in order to mock bigquery

    Give the function the 'mockquerpy' parameter in order to access the
    MockQuerPy object - to for example set test data.

    Example Usage
    -------------

    Can be used as a decorator::

        @mockquerpyify
        def myfunc(m):
            m.test_data = MY_TEST_DATA
            print(bigquery.query(q).result())  # prints out MY_TEST_DATA
    """
    # @wraps(func)  # Not compatible with pytest
    def wrapper_mockquerpy():
        with MockQuerPy() as bigquery:
            try:
                func(bigquery=_MockBigQuery)
            except TypeError as e:
                if "got an unexpected keyword argument 'bigquery'" in str(e):
                    func()
                else:
                    raise
    return wrapper_mockquerpy
