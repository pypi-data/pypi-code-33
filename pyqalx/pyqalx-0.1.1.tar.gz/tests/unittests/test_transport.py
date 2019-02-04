"""Tests for pyqalx.transport."""

import unittest
import pytest
import os

from requests import exceptions

from unittest.mock import patch, call

from pyqalx.transport.api import PyQalxAPI
from pyqalx.transport.core import PyQalxAPIException


class TestTransportAPI(unittest.TestCase):
    def setUp(self):
        token = '1234567890'
        self.api = PyQalxAPI(config={'TOKEN': token})
        self.headers = {
            'Authorization': 'Token {token}'.format(
                token=token
            )
        }
        self.url = 'https://api.qalx.io'

    def test_base_url_override(self):
        """
        Tests that if the config specifies `BASE_URL` that the pyqalxapi
        base_url is changed. This makes it easier for testing
        """
        api = PyQalxAPI(config={'TOKEN': '12345'})
        assert api.base_url == 'https://api.qalx.io/'

        api = PyQalxAPI(config={'TOKEN': '12345',
                                'BASE_URL': 'http://changed.com'})
        assert api.base_url == 'http://changed.com'

    @patch('requests.request')
    def test_list_item(self, mocked_request):
        """
        Tests listing items including a limit, skip and data.
        This also tests that if the user supplies `params` that
        they are sent off as `json`
        """
        params = {
            'limit': 2,
            'skip': 1,
            'data': ['nested=key=2', 'another=nested=3'],
        }
        self.api.get('item',
                     json=params)
        self.once_with = mocked_request.assert_called_once_with(
            url=self.url + '/item',
            method='GET',
            params=params,
            headers=self.headers)

    @patch('requests.request')
    def test_get_item(self, mocked_request):
        """
        Tests getting a specific item
        """
        self.api.get('item/494b775f-7c95-437b-9989-1c9b730ea67e')
        mocked_request.assert_called_once_with(
            url=self.url + '/item/494b775f-7c95-437b-9989-1c9b730ea67e',
            method='GET',
            headers=self.headers
        )

    @patch('requests.request')
    def test_get_item_params_and_json(self, mocked_request):
        """
        Tests that an exception is raised if `json` and `params`
        are supplied to `get`
        """
        with pytest.raises(PyQalxAPIException):
            self.api.get('item/494b775f-7c95-437b-9989-1c9b730ea67e',
                         params={'some': 'params'},
                         json={'json': 'params'})
        assert mocked_request.called is False

    @patch('requests.request')
    def test_post_item(self, mocked_request):
        """
        Tests creating an item
        """
        self.api.post('item',
                      json={'data': {'a': 'b'},
                            'meta': {'some': 'meta'}},)
        mocked_request.assert_called_once_with(
            url=self.url + '/item',
            method='POST',
            json={'data': {'a': 'b'},
                  'meta': {'some': 'meta'}},
            headers=self.headers
        )

    @patch('requests.request')
    def test_post_file_item_success(self, mocked_request):
        """
        Tests creating a file and uploading it to S3
        """
        mocked_request.return_value.ok = True
        mocked_request.return_value.json.return_value = {
            'file': {
                'put_url': 'https://s3-signed-url.com'
            }
        }

        file_path = os.path.abspath(__file__)
        file_name = os.path.basename(file_path)
        resp = self.api.post('item',
                             json={'data': {'a': 'b'}},
                             file_path=file_path)
        assert 'put_url' not in resp[1]['file'].keys()
        assert mocked_request.call_count == 2
        # First call to create the item
        call1 = call(
            url=self.url + '/item',
            method='POST',
            json={'data': {'a': 'b'},
                  'file': {
                      'name': file_name}},
            headers=self.headers
        )
        # Second call is getting the response
        call2 = call1.json()
        # Third call to PUT the file on S3
        call3 = call(
            url='https://s3-signed-url.com',
            method='PUT',
            data=open(file_path, 'rb').read(),
        )
        calls = [
            call1, call2, call3
        ]
        mocked_request.assert_has_calls(calls)

    @patch('requests.request')
    def test_post_file_item_success_no_upload(self, mocked_request):
        """
        Tests creating a file with upload=False to ensure we don't
        attempt to upload to S3
        """
        mocked_request.return_value.ok = True
        mocked_request.return_value.json.return_value = {
            'file': {
                'put_url': 'https://s3-signed-url.com'
            }
        }

        file_path = os.path.abspath(__file__)
        file_name = os.path.basename(file_path)
        resp = self.api.post('item',
                             json={'data': {'a': 'b'}},
                             file_path=file_path,
                             upload=False)
        # put_url will be there as the user will have to upload manually
        assert 'put_url' in resp[1]['file'].keys()
        assert mocked_request.call_count == 1
        mocked_request.assert_called_once_with(
            url=self.url + '/item',
            method='POST',
            json={'data': {'a': 'b'},
                  'file': {
                      'name': file_name}},
            headers=self.headers
        )

    @patch('requests.request')
    def test_post_file_item_failure(self, mocked_request):
        """
        Tests that we don't attempt to upload to S3 if the file item
        creation failed
        """
        class FirstCall(object):
            def json(self):
                return {
                    'file': {
                        'put_url': 'https://s3-signed-url.com'
                    }
                }

            @property
            def ok(self):
                return True

            @property
            def status_code(self):
                return 200

        class SecondCall(object):
            def json(self):
                return ['some-errors']

            @property
            def ok(self):
                return False

            @property
            def status_code(self):
                return 404

            @property
            def reason(self):
                return 'Bad Request'

        mocked_request.side_effect = [FirstCall(),
                                      SecondCall()]

        file_path = os.path.abspath(__file__)

        resp = self.api.post('item',
                             json={'data': {'a': 'b'}},
                             file_path=file_path)
        expected_data = {
            'status_code': SecondCall().status_code,
            'reason': SecondCall().reason,
            'errors': SecondCall().json()
        }
        assert resp[0] is False
        assert resp[1] == expected_data
        assert mocked_request.call_count == 2

    @patch('requests.request')
    def test_post_file_invalid_file(self, mocked_request):
        """
        Tests that we raise an exception if an invalid file
        is provided
        """
        mocked_request.return_value.ok = True
        mocked_request.return_value.json.return_value = {
            'file': {
                'put_url': 'https://s3-signed-url.com'
            }
        }

        with pytest.raises(PyQalxAPIException):
            self.api.post('item',
                          json={'data': {'a': 'b'}},
                          file_path='INVALIDFILEPATH')
            assert mocked_request.called is False

    @patch('requests.request')
    def test_patch(self, mocked_request):
        """
        Tests a patch request to a specific endpoint
        """
        self.api.patch(
            'queues/494b775f-7c95-437b-9989-1c9b730ea67e',
            json={'data': {'a': 'b'}})
        mocked_request.assert_called_once_with(
            url=self.url + '/queues/494b775f-7c95-437b-9989-1c9b730ea67e',
            method='PATCH',
            json={'data': {'a': 'b'}},
            headers=self.headers
        )

    @patch('requests.request')
    def test_patch_delete_file(self, mocked_request):
        """
        Tests deleting a file from an item
        """
        mocked_request.return_value.ok = True
        mocked_request.return_value.json.return_value = {
            'data': {
                'some': 'data'
            }
        }

        self.api.patch('item/494b775f-7c95-437b-9989-1c9b730ea67e',
                       json={'data': {'some': 'data'}},
                       delete_file=True)
        assert mocked_request.call_count == 1

        url = self.url + '/item/494b775f-7c95-437b-9989-1c9b730ea67e'
        mocked_request.assert_called_once_with(url=url,
                                               method='PATCH',
                                               json={'data': {'some': 'data'},
                                                     'file': {}},
                                               headers=self.headers)

    def test_patch_delete_file_with_file(self):
        """
        Tests that an exception is raised if a user attempts to delete
        a file while also specifying file data
        """
        with pytest.raises(PyQalxAPIException):
            self.api.patch('item/494b775f-7c95-437b-9989-1c9b730ea67e',
                           json={'data': {'some': 'data'}},
                           file_path='/path/to/file',
                           delete_file=True)

    @patch('requests.request')
    def test_delete(self, mocked_request):
        """
        Tests a delete request to a specific endpoint
        """
        self.api.delete('bot/494b775f-7c95-437b-9989-1c9b730ea67e')
        mocked_request.assert_called_once_with(
            url=self.url + '/bot/494b775f-7c95-437b-9989-1c9b730ea67e',
            method='DELETE',
            headers=self.headers
        )

    @patch('requests.request')
    def test_build_request_error(self, mocked_request):
        """
        Tests that we return the correct error data
        if the response is not OK.
        """
        mocked_request.return_value.ok = False
        mocked_request.return_value.status_code = 400
        mocked_request.return_value.json.return_value = 'some-errors'
        mocked_request.return_value.reason = 'Bad Request'
        url = self.api._get_url('item/')
        method = 'GET'
        is_ok, data = self.api._build_request(url=url,
                                              method=method,)
        expected_data = {
            'status_code': 400,
            'reason': 'Bad Request',
            'errors': 'some-errors'
        }
        assert is_ok is False
        assert data == expected_data

    @patch('requests.request')
    def test_patch_file_item_success(self, mocked_request):
        """
        Tests updating a file item and uploading it to S3
        """
        mocked_request.return_value.ok = True
        mocked_request.return_value.json.return_value = {
            'file': {
                'put_url': 'https://s3-signed-url.com'
            }
        }

        file_path = os.path.abspath(__file__)
        file_name = os.path.basename(file_path)
        resp = self.api.patch('item/494b775f-7c95-437b-9989-1c9b730ea67e',
                              json={'data': {'a': 'b'}},
                              file_path=file_path)
        assert 'put_url' not in resp[1]['file'].keys()
        assert mocked_request.call_count == 2
        # First call to create the item
        call1 = call(
            url=self.url + '/item/494b775f-7c95-437b-9989-1c9b730ea67e',
            method='PATCH',
            json={'data': {'a': 'b'},
                  'file': {
                      'name': file_name}},
            headers=self.headers
        )
        # Second call is getting the response
        call2 = call1.json()
        # Third call to PUT the file on S3
        call3 = call(
            url='https://s3-signed-url.com',
            method='PUT',
            data=open(file_path, 'rb').read(),
        )
        calls = [
            call1, call2, call3
        ]
        mocked_request.assert_has_calls(calls)

    @patch('requests.request')
    def test_put(self, mocked_request):
        """
        Tests a put request to a specific endpoint
        """
        self.api.put(
            'queues/494b775f-7c95-437b-9989-1c9b730ea67e',
            json={'data': {'a': 'b'}})
        mocked_request.assert_called_once_with(
            url=self.url + '/queues/494b775f-7c95-437b-9989-1c9b730ea67e',
            method='PUT',
            json={'data': {'a': 'b'}},
            headers=self.headers
        )

    @patch('requests.request')
    def test_put_file_item_success(self, mocked_request):
        """
        Tests replacing a file item and uploading it to S3
        """
        mocked_request.return_value.ok = True
        mocked_request.return_value.json.return_value = {
            'file': {
                'put_url': 'https://s3-signed-url.com'
            }
        }

        file_path = os.path.abspath(__file__)
        file_name = os.path.basename(file_path)
        resp = self.api.put('item/494b775f-7c95-437b-9989-1c9b730ea67e',
                            json={'data': {'a': 'b'}},
                            file_path=file_path)
        assert 'put_url' not in resp[1]['file'].keys()
        assert mocked_request.call_count == 2
        # First call to create the item
        call1 = call(
            url=self.url + '/item/494b775f-7c95-437b-9989-1c9b730ea67e',
            method='PUT',
            json={'data': {'a': 'b'},
                  'file': {
                      'name': file_name}},
            headers=self.headers
        )
        # Second call is getting the response
        call2 = call1.json()
        # Third call to PUT the file on S3
        call3 = call(
            url='https://s3-signed-url.com',
            method='PUT',
            data=open(file_path, 'rb').read(),
        )
        calls = [
            call1, call2, call3
        ]
        mocked_request.assert_has_calls(calls)

    def test_put_delete_file_with_file(self):
        """
        Tests that an exception is raised if a user attempts to delete
        a file while also specifying file data
        """
        with pytest.raises(PyQalxAPIException):
            self.api.put('item/494b775f-7c95-437b-9989-1c9b730ea67e',
                         json={'data': {'some': 'data'}},
                         file_path='/path/to/file',
                         delete_file=True)

    @patch('requests.request')
    def test_put_delete_file(self, mocked_request):
        """
        Tests deleting a file from an item
        """
        mocked_request.return_value.ok = True
        mocked_request.return_value.json.return_value = {
            'data': {
                'some': 'data'
            }
        }

        self.api.put('item/494b775f-7c95-437b-9989-1c9b730ea67e',
                     json={'data': {'some': 'data'}},
                     delete_file=True)
        assert mocked_request.call_count == 1

        url = self.url + '/item/494b775f-7c95-437b-9989-1c9b730ea67e'
        mocked_request.assert_called_once_with(url=url,
                                               method='PUT',
                                               json={'data': {'some': 'data'},
                                                     'file': {}},
                                               headers=self.headers)

    @patch('requests.request')
    def test_requests_exception(self, mocked_request):
        """
        Tests handling of the response if requests raises an exception
        """
        mocked_request.side_effect = exceptions.ConnectionError()

        resp = self.api.get('item')
        expected_resp = (False, {
            'status_code': '',
            'reason': mocked_request.side_effect,
            'errors': []

        })
        assert mocked_request.call_count == 1
        assert resp == expected_resp
