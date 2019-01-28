"""
Tests deploy_docker.py
"""

from unittest.mock import call

import pytest

from brewblox_tools import deploy_docker

TESTED = deploy_docker.__name__


BUILD_OUTPUT = [
    b'{"stream":"Step 1/6 : FROM python:3.6"}',
    b'{"stream":"\n"}',
    b'{"stream":" ---\\u003e d21927554614\n"}',
    b'{"stream":"Step 2/6 : RUN mkdir -p /pkg"}',
    b'{"stream":"\n"}',
    b'{"something":"text"}',
    b'not_json',
    b'{"stream":" ---\\u003e Running in 7b0a59f4706b\n"}',
    b'{"stream":"Removing intermediate container 7b0a59f4706b\n"}',
    b'{"stream":" ---\\u003e 402bcb59fe89\n"}',
    b'{"stream":"Step 3/6 : COPY ./pkg/* /pkg/"}',
    b'{"stream":"\n"}',
    b'{"stream":" ---\\u003e 31c862396aca\n"}',
    b'{"stream":"Step 4/6 : EXPOSE 5000"}',
    b'{"stream":"\n"}',
    b'{"stream":" ---\\u003e Running in 7d6552578599\n"}',
    b'{"stream":"Removing intermediate container 7d6552578599\n"}',
    b'{"stream":" ---\\u003e a2b7dc3f9f5d\n"}',
]

PUSH_OUTPUT = [
    b'{"status":"The push refers to repository [docker.io/brewblox/brewblox-service]"}',
    b'{"status":"Preparing","progressDetail":{},"id":"64d234a0ce4c"}',
    b'{"status":"Preparing","progressDetail":{},"id":"2ca1d28f3a22"}',
    b'{"status":"Preparing","progressDetail":{},"id":"e4b347e25e5d"}',
    b'{"status":"Preparing","progressDetail":{},"id":"aec4f1507d85"}',
    b'{"status":"Pushing","progressDetail":{"current":101888,"total":98321},"progress":"[=============='
    b'====================================\\u003e]  101.9kB","id":"2ca1d28f3a22"}',
    b'{"status":"Pushing","progressDetail":{"current":267776,"total":25576721},"progress":"[\\u003e      '
    b'                                            ]  267.8kB/25.58MB","id":"64d234a0ce4c"}',
    b'{"status":"Pushing","progressDetail":{"current":800578,"total":25576721},"progress":"[=\\u003e      '
    b'                                           ]  800.6kB/25.58MB","id":"64d234a0ce4c"}',
    b'{"status":"Layer already exists","progressDetail":{},"id":"6e1b48dc2ccc"}',
    b'{"status":"Pushing","progressDetail":{"current":1593856,"total":25576721},"progress":"[===\\u003e    '
    b'                                           ]  1.594MB/25.58MB","id":"64d234a0ce4c"}',
]


@pytest.fixture
def client_mock(mocker):
    m = mocker.patch(TESTED + '.docker.APIClient').return_value
    m.build.return_value = iter(BUILD_OUTPUT)
    m.push.return_value = iter(PUSH_OUTPUT)
    return m


def test_build(client_mock):
    deploy_docker.main('-n repo-name -i dir-name'.split())
    client_mock.build.assert_called_once_with(
        path='dir-name',
        dockerfile='Dockerfile',
        tag='repo-name:temp',
        rm=True,
        nocache=False
    )


def test_deploy(client_mock):
    deploy_docker.main('-n repo-name -t humpty dumpty'.split())
    client_mock.tag.assert_has_calls([
        call('repo-name:temp', repository='repo-name', tag='humpty'),
        call('repo-name:temp', repository='repo-name', tag='dumpty'),
    ])

    client_mock.push.assert_has_calls([
        call(repository='repo-name', tag='humpty', stream=True),
        call(repository='repo-name', tag='dumpty', stream=True),
    ])


def test_no_push(client_mock):
    deploy_docker.main('-n repo-name -t humpty dumpty --no-push'.split())
    client_mock.tag.assert_has_calls([
        call('repo-name:temp', repository='repo-name', tag='humpty'),
        call('repo-name:temp', repository='repo-name', tag='dumpty'),
    ])

    assert client_mock.push.call_count == 0
