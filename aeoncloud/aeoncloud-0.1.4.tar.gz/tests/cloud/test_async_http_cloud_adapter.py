import json
from asynctest import patch

import pytest

from aeoncloud.cloud.async_http_cloud_adapter import AsyncCloudAdapter
from aeoncloud.exceptions.aeon_cloud_error import AeonCloudError

from tests.utils.equals import dict_equals


async def test_init_adapter_with_correct_arguments():
    # Arrange
    aeon_cloud_url = 'http://test'
    credentials = {
        'apiHost': '',
        'username': '',
        'password': '',
        'organization': '',
        'space': 'aeon'
    }
    callback_url = 'http://test/call_back'
    
    # Act
    http_cloud_adapter = AsyncCloudAdapter(aeon_cloud_url, credentials, callback_url)

    # Assert
    dict_equals(http_cloud_adapter.credentials, credentials)
    assert http_cloud_adapter.aeon_cloud_url == aeon_cloud_url
    assert http_cloud_adapter.callback_url == callback_url


async def test_init_adapter_with_correct_arguments_without_callback():
    # Arrange
    aeon_cloud_url = 'http://test'
    credentials = {
        'apiHost': '',
        'username': '',
        'password': '',
        'organization': '',
        'space': 'aeon'
    }
    
    # Act
    http_cloud_adapter = AsyncCloudAdapter(aeon_cloud_url, credentials)

    # Assert
    dict_equals(http_cloud_adapter.credentials, credentials)
    assert http_cloud_adapter.aeon_cloud_url == aeon_cloud_url
    assert http_cloud_adapter.callback_url == ''


async def test_init_adapter_with_incorrect_url():
    # Arrange
    aeon_cloud_url = None
    credentials = {
        'apiHost': '',
        'username': '',
        'password': '',
        'organization': '',
        'space': 'aeon'
    }
    callback_url = 'http://test/call_back'
    
    # Act
    with pytest.raises(AeonCloudError):
        http_cloud_adapter = AsyncCloudAdapter(aeon_cloud_url, credentials, callback_url)

    # Assert


async def test_init_adapter_with_incorrect_credentials():
    # Arrange
    aeon_cloud_url = 'http://test'
    credentials = 'test'
    
    # Act
    with pytest.raises(AeonCloudError):
        http_cloud_adapter = AsyncCloudAdapter(aeon_cloud_url, credentials)

    # Assert


@patch('aeoncloud.cloud.async_http_cloud_adapter.post')
async def test_deploy_runners(mock_post):
    # Arrange
    aeon_cloud_url = 'http://test'
    credentials = {
        'apiHost': '',
        'username': '',
        'password': '',
        'organization': '',
        'space': 'aeon'
    }
    callback_url = 'http://test/call_back'
    body = json.dumps({
            "count": 2,
            "type": "aeon-runner",
            "credentials": credentials,
            "callbackUrl": callback_url
        })
    mock_result = {'tests': [1]}
    mock_post.return_value = mock_result
    http_cloud_adapter = AsyncCloudAdapter(aeon_cloud_url, credentials, callback_url)

    # Act
    result = await http_cloud_adapter.create_runners(2)

    # Assert
    mock_post.assert_called_with(f'{aeon_cloud_url}/runners', body)
    dict_equals(mock_result, result)


@patch('aeoncloud.cloud.async_http_cloud_adapter.delete')
async def test_delete_runner(mock_delete):
    # Arrange
    aeon_cloud_url = 'http://test'
    credentials = {
        'apiHost': '',
        'username': '',
        'password': '',
        'organization': '',
        'space': 'aeon'
    }
    callback_url = 'http://test/call_back'
    body = json.dumps({
            "credentials": credentials,
            "callbackUrl": callback_url
        })
    mock_result = {'tests': [1]}
    mock_delete.return_value = mock_result
    http_cloud_adapter = AsyncCloudAdapter(aeon_cloud_url, credentials, callback_url)

    # Act
    result = await http_cloud_adapter.delete_runner('z')

    # Assert
    mock_delete.assert_called_with(f'{aeon_cloud_url}/runners/z?force=False', body)
    dict_equals(mock_result, result)


@patch('aeoncloud.cloud.async_http_cloud_adapter.delete')
async def test_delete_runners(mock_delete):
    # Arrange
    aeon_cloud_url = 'http://test'
    credentials = {
        'apiHost': '',
        'username': '',
        'password': '',
        'organization': '',
        'space': 'aeon'
    }
    callback_url = 'http://test/call_back'
    body = json.dumps({
            "credentials": credentials,
            "callbackUrl": callback_url
        })
    mock_result = {'tests': [1]}
    mock_delete.return_value = mock_result
    http_cloud_adapter = AsyncCloudAdapter(aeon_cloud_url, credentials, callback_url)

    # Act
    result = await http_cloud_adapter.delete_runners()

    # Assert
    mock_delete.assert_called_with(f'{aeon_cloud_url}/runners/delete-all?force=False', body)
    dict_equals(mock_result, result)


@patch('aeoncloud.cloud.async_http_cloud_adapter.get')
async def test_get_runner(mock_get):
    # Arrange
    aeon_cloud_url = 'http://test'
    credentials = {
        'apiHost': '',
        'username': '',
        'password': '',
        'organization': '',
        'space': 'aeon'
    }
    callback_url = 'http://test/call_back'
    mock_result = {'tests': [1]}
    mock_get.return_value = mock_result
    http_cloud_adapter = AsyncCloudAdapter(aeon_cloud_url, credentials, callback_url)

    # Act
    result = await http_cloud_adapter.get_runner('id')

    # Assert
    mock_get.assert_called_with(f'{aeon_cloud_url}/runners/id')
    dict_equals(mock_result, result)


@patch('aeoncloud.cloud.async_http_cloud_adapter.get')
async def test_get_runner(mock_get):
    # Arrange
    aeon_cloud_url = 'http://test'
    credentials = {
        'apiHost': '',
        'username': '',
        'password': '',
        'organization': '',
        'space': 'aeon'
    }
    callback_url = 'http://test/call_back'
    mock_result = {'tests': [1]}
    mock_get.return_value = mock_result
    http_cloud_adapter = AsyncCloudAdapter(aeon_cloud_url, credentials, callback_url)

    # Act
    result = await http_cloud_adapter.get_runners()

    # Assert
    mock_get.assert_called_with(f'{aeon_cloud_url}/runners')
    dict_equals(mock_result, result)
