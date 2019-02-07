# start by updating environment variables from .env file
import json
from base64 import b64encode

from . import load_env  # noqa

from uuid import uuid4

import pytest

import serenytics
from serenytics.helpers import make_request, HTTP_204_NO_CONTENT, HTTP_201_CREATED
from serenytics.settings import load_environment_variable, SERENYTICS_API_DOMAIN, enable_log

enable_log()

PYTHON_CLIENT_TESTS_USERNAME_PASSWORD = load_environment_variable('PYTHON_CLIENT_TESTS_USERNAME_PASSWORD')


def _delete_entity(entity, entity_name):
    entity_url = SERENYTICS_API_DOMAIN + '/api/' + entity_name + '/' + entity.uuid
    make_request('delete', entity_url, expected_status_code=HTTP_204_NO_CONTENT, headers=entity._headers)


@pytest.fixture(scope='session', autouse=True)
def serenytics_user_api_key():
    username_headers = {'Authorization': b'Basic ' + b64encode(PYTHON_CLIENT_TESTS_USERNAME_PASSWORD.encode('utf-8'))}
    user_token = make_request('get', SERENYTICS_API_DOMAIN + '/api/token', headers=username_headers).json()['token']

    token_headers = {'X-Auth-Token': user_token}
    api_key = make_request('post', SERENYTICS_API_DOMAIN + '/api/api_key', headers=token_headers).json()['api_key']
    return api_key


@pytest.fixture(scope='session', autouse=True)
def serenytics_client(serenytics_user_api_key):
    # create script used in tests
    response = make_request('post', SERENYTICS_API_DOMAIN + '/api/script',
                            data=json.dumps({'name': 'Test script', 'schedule_infos': '',
                                             'code': 'print("Hello, Serenytics!")',
                                             'kind': 'GENERIC_PYTHON'}),
                            expected_status_code=HTTP_201_CREATED,
                            headers={'X-Api-Key': serenytics_user_api_key, 'Content-Type': 'application/json'})
    script = response.json()

    # create client
    client = serenytics.Client(api_key=serenytics_user_api_key,
                               script_id=script['uuid'])
    return client


@pytest.yield_fixture(scope='function')
def storage_data_source(serenytics_client):
    name = 'test_' + str(uuid4())
    data_source = serenytics_client.get_or_create_storage_data_source_by_name(name)
    assert data_source.name == name

    yield data_source

    _delete_entity(data_source, 'data_source')


@pytest.yield_fixture(scope='session', autouse=True)
def script_test(serenytics_client):
    script = serenytics_client.get_script_by_uuid(serenytics_client._script_id)

    yield script
