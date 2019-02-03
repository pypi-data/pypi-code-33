import json
import pytest
from unittest.mock import patch

from aeoncloud.cloud.http_client import post, delete, get, requests, HEADERS
from aeoncloud.exceptions.aeon_cloud_error import AeonCloudError
from aeoncloud.exceptions.not_found_error import NotFoundError

from tests.utils.equals import dict_equals


@patch('requests.post')
def test_given_correct_contract_when_calling_post_then_json_returned(mock_post):
    # Arrange
    url = 'http://test/something'
    json_input = {
        'test': True
    }
    mock_result = {'tests': [1]}

    mock_post.return_value.content = json.dumps(mock_result)
    mock_post.return_value.status_code = 200

    # Act
    result = post(url, json_input)

    # Assert
    dict_equals(result, mock_result)
    mock_post.assert_called_with(url, json_input, headers=HEADERS)
    assert mock_post.call_count == 1


@patch('requests.post')
def test_given_error_occurs_on_server_when_calling_post_then_exception_raised(mock_post):
    # Arrange
    mock_result = {'tests': [1]}

    mock_post.return_value.content = mock_result
    mock_post.return_value.status_code = 400

    with pytest.raises(AeonCloudError):
        # Act
        result = post('http://test/something', {
            'test': True
        })

    # Assert


@patch('requests.delete')
def test_given_correct_contract_when_calling_delete_then_json_returned(mock_delete):
    # Arrange
    url = 'http://test/something'
    mock_result = {'tests': [1]}
    json_input = {
        'test': True
    }
    
    mock_delete.return_value.content = json.dumps(mock_result)
    mock_delete.return_value.status_code = 200

    # Act
    result = delete(url, json_input)

    # Assert
    dict_equals(result, mock_result)
    mock_delete.assert_called_with(url, json_input, headers=HEADERS)
    assert mock_delete.call_count == 1


@patch('requests.delete')
def test_given_error_occurs_on_server_when_calling_delete_then_exception_raised(mock_delete):
    # Arrange
    mock_result = {'tests': [1]}

    mock_delete.return_value.content = mock_result
    mock_delete.return_value.status_code = 400

    with pytest.raises(AeonCloudError):
        # Act
        result = delete('http://test/something', {
            'test': True
        })


@patch('requests.delete')
def test_given_not_found_error_occurs_on_server_when_calling_delete_then_exception_raised(mock_delete):
    # Arrange
    mock_result = {'tests': [1]}

    mock_delete.return_value.content = mock_result
    mock_delete.return_value.status_code = 404

    with pytest.raises(NotFoundError):
        # Act
        result = delete('http://test/something', {
            'test': True
        })


@patch('requests.get')
def test_given_correct_contract_when_calling_get_then_json_returned(mock_get):
    # Arrange
    url = 'http://test/something'
    mock_result = {'tests': [1]}

    mock_get.return_value.content = json.dumps(mock_result)
    mock_get.return_value.status_code = 200

    # Act
    result = get(url)

    # Assert
    dict_equals(result, mock_result)
    mock_get.assert_called_with(url, headers=HEADERS)
    assert mock_get.call_count == 1


@patch('requests.get')
def test_given_error_occurs_on_server_when_calling_get_then_exception_raised(mock_get):
    # Arrange
    mock_result = {'tests': [1]}

    mock_get.return_value.content = mock_result
    mock_get.return_value.status_code = 400

    with pytest.raises(AeonCloudError):
        # Act
        result = get('http://test/something')


@patch('requests.get')
def test_given_not_found_error_occurs_on_server_when_calling_get_then_exception_raised(mock_get):
    # Arrange
    mock_result = {'tests': [1]}

    mock_get.return_value.content = mock_result
    mock_get.return_value.status_code = 404

    with pytest.raises(NotFoundError):
        # Act
        result = get('http://test/something')
