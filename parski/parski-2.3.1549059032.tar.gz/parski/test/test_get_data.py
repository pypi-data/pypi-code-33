"""tests for checking get_data method"""

import os
import sys
from copy import deepcopy
import pytest

from parski.get_data import GetData

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

WRONG_URL = "https://test_url_wrong.com"
RIGHT_URL = "https://pctapi.cloudpod.apps.ge.com/aws/v2.1/accounts"


GENERIC_OPTIONS = {
    'url': RIGHT_URL,
    'silent': False,
    'file_name': os.path.join(DIR_PATH, 'accounts.json'),
    'key_var': 'PCT_API_READ_KEY',
    'source': 'api',
    'api_retry': 3,
    'naapi': False,
    'key': None,
    'ssl_verify': True
}

##### api_call #####

def test_call_no_key():
    options = deepcopy(GENERIC_OPTIONS)

    get_data_object = GetData(options)
    request = get_data_object._api_call(None)[0]
    print request['error_msg']
    assert request['status_code'] == 401 and request['data'] is None

def test_call_bad_url():
    options = deepcopy(GENERIC_OPTIONS)
    options['url'] = WRONG_URL
    os.environ['PCT_API_READ_KEY'] = "bad_key"

    get_data_object = GetData(options)
    request = get_data_object._api_call(None)[0]
    print request['error_msg']
    del os.environ['PCT_API_READ_KEY']
    assert request['status_code'] == 404 and request['data'] is None

def test_call_bad_key():
    options = deepcopy(GENERIC_OPTIONS)
    os.environ['PCT_API_READ_KEY'] = "bad_key"

    get_data_object = GetData(options)
    request = get_data_object._api_call(None)[0]
    print request['error_msg']
    del os.environ['PCT_API_READ_KEY']
    assert request['status_code'] == 401 and request['data'] is None


##### api_try #####

def test_try():
    options = deepcopy(GENERIC_OPTIONS)
    options['url'] = WRONG_URL

    get_data_object = GetData(options)
    request = get_data_object._api_try(None)[0]
    print request['error_msg']
    assert request['status_code'] == 404 and request['data'] is None


##### api_load #####

def test_load_no_key():
    options = deepcopy(GENERIC_OPTIONS)
    options['url'] = WRONG_URL

    get_data_object = GetData(options)
    request = get_data_object._api_load()
    print request['error_msg']
    assert request['status_code'] == 401 and request['data'] is None

def test_load_bad_url():
    options = deepcopy(GENERIC_OPTIONS)
    options['url'] = WRONG_URL
    os.environ['PCT_API_READ_KEY'] = "bad_key"

    get_data_object = GetData(options)
    request = get_data_object._api_load()
    print request['error_msg']
    del os.environ['PCT_API_READ_KEY']
    assert request['status_code'] == 404 and request['data'] is None

def test_load_bad_key():
    options = deepcopy(GENERIC_OPTIONS)
    os.environ['PCT_API_READ_KEY'] = "bad_key"

    get_data_object = GetData(options)
    request = get_data_object._api_load()
    print request['error_msg']
    del os.environ['PCT_API_READ_KEY']
    assert request['status_code'] == 401 and request['data'] is None


##### get_data #####

def test_get_missing_file():
    options = deepcopy(GENERIC_OPTIONS)
    options['source'] = "file"
    options['file_name'] = os.path.join(DIR_PATH, 'no_file.json')

    get_data_object = GetData(options)
    request = get_data_object.get_data()
    print request['error_msg']
    assert request['status_code'] == 401 and request['data'] is None

def test_get_bad_json():
    options = deepcopy(GENERIC_OPTIONS)
    options['source'] = "file"
    options['file_name'] = os.path.join(DIR_PATH, 'bad.json')

    get_data_object = GetData(options)
    request = get_data_object.get_data()
    print request['error_msg']
    assert request['status_code'] == 401 and request['data'] is None

def test_get_bad_source():
    options = deepcopy(GENERIC_OPTIONS)
    options['source'] = "banana"

    get_data_object = GetData(options)
    request = get_data_object.get_data()
    print request['error_msg']
    assert request['status_code'] == 500 and request['data'] is None

def test_get_file_load():
    options = deepcopy(GENERIC_OPTIONS)
    options['source'] = "file"

    get_data_object = GetData(options)
    request = get_data_object.get_data()
    print request['error_msg']
    assert request['status_code'] == 200 and request['data']
