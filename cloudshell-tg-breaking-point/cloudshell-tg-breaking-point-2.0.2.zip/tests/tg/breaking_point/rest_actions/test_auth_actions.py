from unittest import TestCase

from mock import Mock

from cloudshell.tg.breaking_point.rest_actions.auth_actions import AuthActions
from cloudshell.tg.breaking_point.rest_api.rest_json_client import RestClientUnauthorizedException


class TestAuthActions(TestCase):
    def setUp(self):
        self._rest_service = Mock()
        self._logger = Mock()
        self._instance = AuthActions(self._rest_service, self._logger)

    def test_login(self):
        uri = '/api/v1/auth/session'
        username = Mock()
        password = Mock()
        json_data = {'username': username, 'password': password}
        self._instance.login(username, password)
        self._rest_service.request_post.assert_called_once_with(uri, json_data)

    def test_logout(self):
        uri = '/api/v1/auth/session'
        self._instance.logout()
        self._rest_service.request_delete.assert_called_once_with(uri)

    def test_logged_in_true(self):
        uri = '/api/v1/bps/'
        self.assertTrue(self._instance.logged_in())
        self._rest_service.request_get.assert_called_once_with(uri)

    def test_logged_in_false(self):
        uri = '/api/v1/bps/'
        self._rest_service.request_get.side_effect = RestClientUnauthorizedException()
        self.assertFalse(self._instance.logged_in())
        self._rest_service.request_get.assert_called_once_with(uri)
