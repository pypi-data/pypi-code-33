from unittest import TestCase

from mock import Mock, patch

from cloudshell.tg.breaking_point.rest_api.rest_json_client import RestJsonClient, RestClientUnauthorizedException, \
    RestClientException


class TestRestJsonClient(TestCase):
    def setUp(self):
        self.__hostname = '10.0.1.1'
        self.__uri = '/test/test'
        self.__session = Mock()

    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.requests')
    def test_session_getter(self, requests):
        requests.Session.return_value = self.__session
        instance = RestJsonClient(self.__hostname)
        self.assertIs(self.__session, instance.session)

    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.requests')
    def test_build_url_https(self, requests):
        requests.Session.return_value = self.__session
        instance = RestJsonClient(self.__hostname, use_https=True)
        self.assertEqual(instance._build_url(self.__uri), 'https://{0}{1}'.format(self.__hostname, self.__uri))

    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.requests')
    def test_build_url_http(self, requests):
        requests.Session.return_value = self.__session
        instance = RestJsonClient(self.__hostname, use_https=False)
        self.assertEqual(instance._build_url(self.__uri), 'http://{0}{1}'.format(self.__hostname, self.__uri))

    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.requests')
    def test_request_valid(self, requests):
        requests.Session.return_value = self.__session
        instance = RestJsonClient(self.__hostname, use_https=False)
        response = Mock()
        response.status_code = 200
        self.assertIs(instance._valid(response), response)
        response.status_code = 201
        self.assertIs(instance._valid(response), response)
        response.status_code = 204
        self.assertIs(instance._valid(response), response)
        with self.assertRaises(RestClientUnauthorizedException):
            response.status_code = 401
            out = instance._valid(response)

        with self.assertRaises(RestClientException):
            response.status_code = 500
            out = instance._valid(response)

    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.requests')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.RestJsonClient._valid')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.RestJsonClient._build_url')
    def test_request_put(self, build_url, valid, requests):
        requests.Session.return_value = self.__session
        instance = RestJsonClient(self.__hostname, use_https=False)
        valid_call = Mock()
        valid.return_value = valid_call
        request = Mock()
        url = Mock()
        build_url.return_value = url
        response = Mock()
        self.__session.put.return_value = response
        out = instance.request_put(self.__uri, request)
        build_url.assert_called_once_with(self.__uri)
        self.__session.put.assert_called_once_with(url, request, verify=False)
        valid.assert_called_once_with(response)
        valid_call.json.assert_called_once()

    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.requests')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.RestJsonClient._valid')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.RestJsonClient._build_url')
    def test_request_post(self, build_url, valid, requests):
        requests.Session.return_value = self.__session
        instance = RestJsonClient(self.__hostname, use_https=False)
        valid_call = Mock()
        valid.return_value = valid_call
        request = Mock()
        url = Mock()
        build_url.return_value = url
        response = Mock()
        self.__session.post.return_value = response
        out = instance.request_post(self.__uri, request)
        build_url.assert_called_once_with(self.__uri)
        self.__session.post.assert_called_once_with(url, json=request, verify=False)
        valid.assert_called_once_with(response)
        valid_call.json.assert_called_once()

    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.requests')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.RestJsonClient._valid')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.RestJsonClient._build_url')
    def test_request_post_files(self, build_url, valid, requests):
        requests.Session.return_value = self.__session
        instance = RestJsonClient(self.__hostname, use_https=False)
        valid_call = Mock()
        valid.return_value = valid_call
        request = Mock()
        url = Mock()
        build_url.return_value = url
        response = Mock()
        self.__session.post.return_value = response
        files = Mock()
        out = instance.request_post_files(self.__uri, request, files)
        build_url.assert_called_once_with(self.__uri)
        self.__session.post.assert_called_once_with(url, data=request, files=files, verify=False)
        valid.assert_called_once_with(response)
        valid_call.json.assert_called_once()

    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.requests')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.RestJsonClient._valid')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.RestJsonClient._build_url')
    def test_request_get(self, build_url, valid, requests):
        requests.Session.return_value = self.__session
        instance = RestJsonClient(self.__hostname, use_https=False)
        valid_call = Mock()
        valid.return_value = valid_call
        url = Mock()
        build_url.return_value = url
        response = Mock()
        self.__session.get.return_value = response
        out = instance.request_get(self.__uri)
        build_url.assert_called_once_with(self.__uri)
        self.__session.get.assert_called_once_with(url, verify=False)
        valid.assert_called_once_with(response)
        valid_call.json.assert_called_once()

    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.requests')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.RestJsonClient._valid')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.RestJsonClient._build_url')
    def test_request_get_files(self, build_url, valid, requests):
        requests.Session.return_value = self.__session
        instance = RestJsonClient(self.__hostname, use_https=False)
        valid_call = Mock()
        valid.return_value = valid_call
        request = Mock()
        url = Mock()
        build_url.return_value = url
        response = Mock()
        self.__session.get.return_value = response
        files = Mock()
        out = instance.request_get_files(self.__uri)
        build_url.assert_called_once_with(self.__uri)
        self.__session.get.assert_called_once_with(url, verify=False)
        valid.assert_called_once_with(response)

    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.requests')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.RestJsonClient._valid')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_json_client.RestJsonClient._build_url')
    def test_request_delete(self, build_url, valid, requests):
        requests.Session.return_value = self.__session
        instance = RestJsonClient(self.__hostname, use_https=False)
        valid_call = Mock()
        valid.return_value = valid_call
        request = Mock()
        url = Mock()
        build_url.return_value = url
        response = Mock()
        self.__session.delete.return_value = response
        out = instance.request_delete(self.__uri)
        build_url.assert_called_once_with(self.__uri)
        self.__session.delete.assert_called_once_with(url, verify=False)
        valid.assert_called_once_with(response)
        # valid_call.content.assert_called_once()

