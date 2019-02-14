from unittest import TestCase

from mock import Mock, patch, PropertyMock, call

from cloudshell.tg.breaking_point.rest_api.rest_session_manager import RestSessionContextManager


class TestRestSessionContextManager(TestCase):
    def setUp(self):
        self.__hostname = Mock()
        self.__username = Mock()
        self.__password = Mock()
        self.__logger = Mock()
        self._instance = RestSessionContextManager(self.__hostname, self.__username, self.__password, self.__logger)

    def test_logger_getter(self):
        self.assertEqual(self._instance.logger, self.__logger)

    def test_logger_setter(self):
        new_logger = Mock()
        self._instance.logger = new_logger
        self.assertEqual(self._instance.logger, new_logger)

    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.RestJsonClient')
    def test_session_getter(self, rest_json_client):
        json_client_instance = Mock()
        rest_json_client.return_value = json_client_instance
        session = self._instance._session
        rest_json_client.assert_called_once_with(self.__hostname)
        self.assertIs(session, json_client_instance)
        session = self._instance._session
        rest_json_client.assert_called_once_with(self.__hostname)
        self.assertIs(session, json_client_instance)

    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.RestSessionContextManager._session',
           new_callable=PropertyMock)
    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.AuthActions')
    def test_auth_actions_getter(self, auth_actions_class, session_prop):
        auth_actions_instance = Mock()
        auth_actions_class.return_value = auth_actions_instance
        session = Mock()
        session_prop.return_value = session
        auth_actions = self._instance._auth_actions
        auth_actions_class.assert_called_once_with(session, self.__logger)
        self.assertIs(auth_actions, auth_actions_instance)
        auth_actions = self._instance._auth_actions
        auth_actions_class.assert_called_once_with(session, self.__logger)
        self.assertIs(auth_actions, auth_actions_instance)

    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.RestJsonClient')
    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.AuthActions')
    def test_destroy_session(self, auth_actions_class, rest_client_class):
        auth_actions_instance = Mock()
        auth_actions_class.return_value = auth_actions_instance
        rest_client_instance = Mock()
        rest_client_class.return_value = rest_client_instance
        self._instance._destroy_session()
        auth_actions_instance.logout.assert_not_called()
        auth_actions = self._instance._auth_actions
        self._instance._destroy_session()
        auth_actions_instance.logout.assert_called_once_with()
        auth_actions = self._instance._auth_actions
        auth_actions_class.assert_has_calls(
            [call(rest_client_instance, self.__logger), call(rest_client_instance, self.__logger)], any_order=True)

    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.RestSessionContextManager._session',
           new_callable=PropertyMock)
    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.RestSessionContextManager._auth_actions',
           new_callable=PropertyMock)
    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.Lock')
    def test_enter_exit_logged_in(self, lock_class, auth_actions_prop, session_prop):
        lock_instance = Mock()
        lock_class.return_value = lock_instance
        auth_actions_instance = Mock()
        auth_actions_prop.return_value = auth_actions_instance
        session_instance = Mock()
        session_prop.return_value = session_instance
        auth_actions_instance.logged_in.return_value = True
        _instance = RestSessionContextManager(self.__hostname, self.__username, self.__password, self.__logger)
        with _instance as session:
            self.assertIs(session, session_instance)
        lock_instance.acquire.assert_called_once_with()
        lock_instance.release.assert_called_once_with()
        auth_actions_instance.login.assert_not_called()

    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.RestSessionContextManager._session',
           new_callable=PropertyMock)
    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.RestSessionContextManager._auth_actions',
           new_callable=PropertyMock)
    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.Lock')
    def test_enter_exit_not_logged_in(self, lock_class, auth_actions_prop, session_prop):
        lock_instance = Mock()
        lock_class.return_value = lock_instance
        auth_actions_instance = Mock()
        auth_actions_prop.return_value = auth_actions_instance
        session_instance = Mock()
        session_prop.return_value = session_instance
        auth_actions_instance.logged_in.return_value = False
        _instance = RestSessionContextManager(self.__hostname, self.__username, self.__password, self.__logger)
        with _instance as session:
            self.assertIs(session, session_instance)
        lock_instance.acquire.assert_called_once_with()
        lock_instance.release.assert_called_once_with()
        auth_actions_instance.login.assert_called_once_with(self.__username, self.__password)

    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.RestSessionContextManager._session',
           new_callable=PropertyMock)
    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.RestSessionContextManager._auth_actions',
           new_callable=PropertyMock)
    @patch('cloudshell.tg.breaking_point.rest_api.rest_session_manager.Lock')
    def test_enter_exit_raise_exception(self, lock_class, auth_actions_prop, session_prop):
        lock_instance = Mock()
        lock_class.return_value = lock_instance
        auth_actions_instance = Mock()
        auth_actions_prop.return_value = auth_actions_instance
        session_instance = Mock()
        session_prop.return_value = session_instance
        auth_actions_instance.logged_in.return_value = False
        auth_actions_instance.login.side_effect = Exception()
        _instance = RestSessionContextManager(self.__hostname, self.__username, self.__password, self.__logger)
        with self.assertRaises(Exception):
            with _instance as session:
                pass
        lock_instance.acquire.assert_called_once_with()
        lock_instance.release.assert_called_once_with()
        auth_actions_instance.login.assert_called_once_with(self.__username, self.__password)
