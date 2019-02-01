"""tests for checking utils methods"""

import os
import sys
import pytest

from parski.utils import filter_datetime, dict_to_paths, paths_to_dict

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

### filter_datetime ###

TEST_DATES = [
    {'date': '2017-06-05T16:54:51Z', 'bool': True},
    {'date': '2017-06-05T16:54:51.12Z', 'bool': True},
    {'date': '2017-06-04T16:54:51Z-2017-06-04T16:54:51Z', 'bool': False},
    {'date': '2017-06-04T16:54:51', 'bool': False},
    {'date': '(2012/04/01)', 'bool': True},
    {'date': '(2012/04/01)/(2012/03/01)', 'bool': False},
    {'date': 'awd2017-06-04T16:54:51Z', 'bool': False},
    {'date': '2012/04/01', 'bool': True},
    {'date': '2010/04/01', 'bool': False},
    {'date': '2012-04-01', 'bool': True},
    {'date': '2012/03/01-2012/02/01', 'bool': False}
]

TEST_RANGE = [
    '2011-06-04T16:54:51Z/2018-06-09T16:54:51Z',
    '2011-06-04T16:54:51Z',
]

def test_filter_datetime():
    """is test_filter_datetime checking dates correctly?"""



    for test in TEST_DATES:
        assert filter_datetime(TEST_RANGE[0], test['date']) == test['bool']
    for test in TEST_DATES:
        assert filter_datetime(TEST_RANGE[1], test['date']) == test['bool']



### dict to path conversions ###

CONVERSIONS = {
    "dicts": [
        {'Alias': 'digital-public'},
        {'Tags': [{'Key': 'Name', 'Value': 'barryless'}, {'Key': 'csadmin', 'Value': 'csadmin'}]},
        {'NetworkInterfaceSet': [{'PrivateIpAddresses': [{'PrivateIpAddress': '172.31.48.10'}]}]}
    ],
    "paths": [
        [
            {'path': ['Alias'], 'value': 'digital-public'}
        ],
        [
            {'path': ['Tags', 0, 'Key'], 'value': 'Name'},
            {'path': ['Tags', 0, 'Value'], 'value': 'barryless'},
            {'path': ['Tags', 1, 'Key'], 'value': 'csadmin'},
            {'path': ['Tags', 1, 'Value'], 'value': 'csadmin'}
        ],
        [
            {
                'path': ['NetworkInterfaceSet', 0, 'PrivateIpAddresses', 0, 'PrivateIpAddress'],
                'value': '172.31.48.10'
            }
        ]
    ]
}

def test_dict_to_paths():
    """Is dict_to_path correctly converting dicts?"""

    for i, test_dict in enumerate(CONVERSIONS["dicts"]):
        output = dict_to_paths(test_dict)
        output.sort()
        answer = CONVERSIONS["paths"][i]
        answer.sort()

        assert output == answer

def test_paths_to_dict():
    """Is path_to_dict correctly converting paths?"""

    for i, test_path in enumerate(CONVERSIONS["paths"]):
        output = paths_to_dict(test_path)
        answer = CONVERSIONS["dicts"][i]

        assert output == answer
