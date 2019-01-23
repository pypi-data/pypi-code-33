import json
import os
import glob
from time import sleep
import requests
import yaml
from reliabilly.settings import Constants, Settings

EMPTY = ''
FILE_MODE = 'r'
NAME_KEY = 'name'
TESTS_KEY = 'tests'
DESCRIPTION_KEY = 'description'
VERB_KEY = 'verb'
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'
WAIT = 'WAIT'
POST_ALL = 'POST_ALL'
ENDPOINT_KEY = 'endpoint'
STATUS_KEY = 'status'
TOTAL_KEY = 'total'
BODY_KEY = 'body'
TIME_KEY = 'time'
GREATER_KEY = 'greater'
TEST_CONFIG_PATH = '*.yml'
TARGET_KEY = 'target'
LOCAL_TARGET = 'local'
UAT_TARGET = 'uat'
PROD_TARGET = 'production'
LINE = '*' * 50


def get_headers():
    return {Constants.AUTHORIZATION_HEADER: Settings.AUTH_TOKEN, Constants.SERVICE_NAME_ENV: 'integration tests'}


def check_target_run(target, target_config):
    if not target_config:
        return True
    url_checkpoint = target.split('.')[0]
    if LOCAL_TARGET in url_checkpoint:
        return LOCAL_TARGET == target_config
    if UAT_TARGET in url_checkpoint:
        return UAT_TARGET == target_config
    if PROD_TARGET == target_config:
        return LOCAL_TARGET not in url_checkpoint and UAT_TARGET not in url_checkpoint
    return False


def run_service_integration_tests(target, service_path):
    for test_path in glob.glob(os.path.join(
            service_path, TEST_CONFIG_PATH)):
        with open(test_path, FILE_MODE) as test_file:
            test_config = yaml.load(test_file)
            print(LINE)
            target_config = test_config.get(TARGET_KEY, None)
            if check_target_run(target, target_config):
                print('Running {0}'.format(test_config[NAME_KEY]))
                test_cases = test_config[TESTS_KEY]
                run_test_cases(test_cases, target)


def run_test_cases(test_cases, target):
    for test in test_cases:
        print('Executing test: {0}'.format(test[DESCRIPTION_KEY]))
        verb = test[VERB_KEY]
        request_func = get_request_method(verb, test)
        target_endpoint = target + test.get(ENDPOINT_KEY, EMPTY)
        print(target_endpoint)
        if verb == WAIT:
            time = test.get(TIME_KEY, 30)  # Default to 30sec if not set
            print(f'Waiting {time}sec...')
            sleep(time)
            continue
        if verb == POST:
            payload = test.get(BODY_KEY, None)
            if test.get('file', None):
                payload = test['file']
            result = request_func(target_endpoint, data=payload, headers=get_headers())
        else:
            result = request_func(target_endpoint, headers=get_headers())
        print(f'Status: {result.status_code}, Expected: {test[STATUS_KEY]}')
        assert result.status_code == test[STATUS_KEY]
        body = test.get(BODY_KEY, None)
        total = test.get(TOTAL_KEY, None)
        if body and verb == GET:
            assert str(body) == result.text
        if total:
            greater = bool(test.get(GREATER_KEY, False))
            if greater:
                assert result.json()[TOTAL_KEY] > total
            else:
                assert result.json()[TOTAL_KEY] == total


def post_all_from_file(target_endpoint, data, **args):
    result = None
    with open('./data/{}'.format(data)) as file:
        items = json.load(file)
        for item in items:
            json_item = json.dumps(item)
            result = requests.post(target_endpoint, json_item, **args)
            if result.status_code != 201:
                return result
        return result


def get_request_method(verb, test):
    if verb == DELETE:
        return requests.delete
    if verb == POST:
        if test.get('file', None):
            return post_all_from_file
        return requests.post
    if verb == PUT:
        return requests.put
    return requests.get
