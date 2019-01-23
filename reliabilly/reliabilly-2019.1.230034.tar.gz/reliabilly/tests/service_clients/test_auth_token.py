from unittest import TestCase
from unittest.mock import MagicMock

from reliabilly.components.authorization import Authorization, get_acceptable_token_list
from reliabilly.settings import Constants, Settings


TEST = 'test'
DUMMY = 'dummy'


def token_list():
    return [TEST]


class AuthTests(TestCase):
    def test_auth_token(self):
        mock = MagicMock()
        mock.headers = {Constants.AUTHORIZATION_HEADER: TEST}
        auth = Authorization()
        self.assertEqual(auth.get_auth_token(mock), TEST)
        self.assertEqual(auth.get_auth_token_log(mock), TEST[-3:])
        self.assertTrue(auth.is_permitted(mock, token_list))
        mock.headers = {Constants.AUTHORIZATION_HEADER: TEST[:-2]}
        self.assertEqual(auth.get_auth_token_log(mock), Constants.NONE)

    def test_token_list(self):
        mock = MagicMock()
        mock.get_secret.return_value = None
        Settings.ENV = Constants.PROD
        tokens = get_acceptable_token_list(DUMMY, mock)
        self.assertIn(DUMMY, tokens)
        mock.get_secret.return_value = '["test1", "test2"]'
        tokens = get_acceptable_token_list(Constants.EMPTY, mock)
        self.assertNotIn(DUMMY, tokens)
        self.assertIn('test1', tokens)
        self.assertIn('test2', tokens)

    def test_response(self):
        code, _, _2 = Authorization.get_unauthorized_response()
        self.assertEqual(code, Constants.UNAUTHORIZED_CODE)

    def test_bearer_token(self):
        mock = MagicMock()
        mock.headers = {Constants.AUTHORIZATION_HEADER: Constants.BEARER_PREFIX}
        mock.return_value = True
        auth = Authorization()
        self.assertTrue(auth.is_permitted(mock, mock, mock))
