from asynctest import CoroutineMock, patch
import pytest

from aeoncloud.cloud.async_http_client import post, delete, get, aiohttp
from aeoncloud.exceptions.aeon_cloud_error import AeonCloudError
from aeoncloud.exceptions.not_found_error import NotFoundError

from tests.utils.equals import dict_equals


@patch('aiohttp.ClientSession.post')
async def test_given_correct_contract_when_calling_post_then_json_returned(mock_post):
    # Arrange
    url = 'http://test/something'
    json = {
        'test': True
    }

    mock_result = {'tests': [1]}
    mock_post.return_value.__aenter__.return_value.json = CoroutineMock(side_effect=[
        mock_result
    ])
    mock_post.return_value.__aenter__.return_value.status = 200

    # Act
    result = await post(url, json)

    # Assert
    dict_equals(result, mock_result)
    mock_post.assert_called_with(url, data=json)
    assert mock_post.call_count == 1


@patch('aiohttp.ClientSession.post')
async def test_given_error_occurs_on_server_when_calling_post_then_exception_raised(mock_post):
    # Arrange
    mock_post.return_value.__aenter__.return_value.text = CoroutineMock(side_effect=[
        'error'
    ])
    mock_post.return_value.__aenter__.return_value.status = 400

    with pytest.raises(AeonCloudError):
        # Act
        result = await post('http://test/something', {
            'test': True
        })

    # Assert


@patch('aiohttp.ClientSession.delete')
async def test_given_correct_contract_when_calling_delete_then_json_returned(mock_delete):
    # Arrange
    url = 'http://test/something'
    mock_result = {'tests': [1]}
    json = {
        'test': True
    }

    mock_delete.return_value.__aenter__.return_value.json = CoroutineMock(side_effect=[
        mock_result
    ])
    mock_delete.return_value.__aenter__.return_value.status = 200

    # Act
    result = await delete(url, json)

    # Assert
    dict_equals(result, mock_result)
    mock_delete.assert_called_with(url, data=json)
    assert mock_delete.call_count == 1


@patch('aiohttp.ClientSession.delete')
async def test_given_error_occurs_on_server_when_calling_delete_then_exception_raised(mock_delete):
    # Arrange
    mock_delete.return_value.__aenter__.return_value.text = CoroutineMock(side_effect=[
        'error'
    ])
    mock_delete.return_value.__aenter__.return_value.status = 400

    with pytest.raises(AeonCloudError):
        # Act
        result = await delete('http://test/something', {
            'test': True
        })


@patch('aiohttp.ClientSession.delete')
async def test_given_not_found_error_occurs_on_server_when_calling_delete_then_exception_raised(mock_delete):
    # Arrange
    mock_delete.return_value.__aenter__.return_value.text = CoroutineMock(side_effect=[
        'error'
    ])
    mock_delete.return_value.__aenter__.return_value.status = 404

    with pytest.raises(NotFoundError):
        # Act
        result = await delete('http://test/something', {
            'test': True
        })


@patch('aiohttp.ClientSession.get')
async def test_given_correct_contract_when_calling_get_then_json_returned(mock_get):
    # Arrange
    url = 'http://test/something'
    mock_result = {'tests': [1]}

    mock_get.return_value.__aenter__.return_value.json = CoroutineMock(side_effect=[
        mock_result
    ])
    mock_get.return_value.__aenter__.return_value.status = 200

    # Act
    result = await get('http://test/something')

    # Assert
    dict_equals(result, mock_result)
    mock_get.assert_called_with(url)
    assert mock_get.call_count == 1


@patch('aiohttp.ClientSession.get')
async def test_given_error_occurs_on_server_when_calling_get_then_exception_raised(mock_get):
    # Arrange
    mock_get.return_value.__aenter__.return_value.text = CoroutineMock(side_effect=[
        'error'
    ])
    mock_get.return_value.__aenter__.return_value.status = 400

    with pytest.raises(AeonCloudError):
        # Act
        result = await get('http://test/something')


@patch('aiohttp.ClientSession.get')
async def test_given_not_found_error_occurs_on_server_when_calling_get_then_exception_raised(mock_get):
    # Arrange
    mock_get.return_value.__aenter__.return_value.text = CoroutineMock(side_effect=[
        'error'
    ])
    mock_get.return_value.__aenter__.return_value.status = 404

    with pytest.raises(NotFoundError):
        # Act
        result = await get('http://test/something')
