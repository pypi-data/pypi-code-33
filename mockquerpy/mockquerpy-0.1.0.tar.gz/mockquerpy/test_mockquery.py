#!/usr/bin/env pytest
# -*- coding: utf-8 -*-

from .mockquerpy import MockQuerPy
from .mockquerpy import mockquerpy_wrap

from google.cloud import bigquery as REAL_BQ

from sys import modules

TEST_DATA = [{'name': 'mydata'}, {'name': 'myotherdata'}]
TEST_PROJECTID = 'IAMPROJECT'
TEST_QUERY = 'SELECT * FROM USERS'


def test_mockquerpy_ctx_manager():
    print('\n============ test_mockquerpy_ctx_manager : RUNNING ============')
    assert(REAL_BQ == modules['google.cloud.bigquery'])

    # First basic use
    with MockQuerPy(TEST_DATA) as bigquery:
        assert(bigquery != modules['google.cloud.bigquery'])
        assert(bigquery != REAL_BQ), 'Real bigquery wasnt swapped with mock'

    # Test invalid use
    try:
        with MockQuerPy():
            raise NotImplementedError('MockQuerPy should crash before this')
    except AssertionError as e:
        assert 'Invalid use!' in str(e)
        assert 'Must match Regex' in str(e)
    print('============ test_mockquerpy_ctx_manager : SUCCESS ============')


@mockquerpy_wrap
def test_mockquerpy_decorator(bigquery):
    print('\n============= test_mockquerpy_decorator : RUNNING =============')
    assert REAL_BQ != modules['google.cloud.bigquery'], 'bigquery mock failure'
    assert REAL_BQ != bigquery, 'bigquery wasnt mocked!'
    print('============= test_mockquerpy_decorator : SUCCESS =============')


@mockquerpy_wrap
def test_mockquerpy_decorator_no_params():
    print('\n======== test_mockquerpy_decorator_no_params : RUNNING ========')
    print('======== test_mockquerpy_decorator_no_params : SUCCESS ========')


@mockquerpy_wrap
def test_mockquerpy_query(bigquery):
    print('\n=============== test_mockquerpy_query : RUNNING ===============')
    # Set the test data
    MockQuerPy.set_test_data(TEST_DATA)

    # Initialize the client and run the query like normal
    bq = bigquery.Client(project=TEST_PROJECTID)
    rslt = bq.query(TEST_QUERY)

    # Iterate over the data and check if its the same as TEST_DATA
    for idx, r in enumerate(rslt.result()):
        assert TEST_DATA[idx] == r, 'mock library returned incorrect data'
    print('=============== test_mockquerpy_query : SUCCESS ===============')

