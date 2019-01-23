from unittest import TestCase
from unittest.mock import MagicMock

from reliabilly.components.services.okta import check_session
from reliabilly.settings import Constants


class OktaTests(TestCase):
    def test_session_valid(self):
        mock = MagicMock()
        mock.json.return_value = {Constants.STATUS: Constants.OKTA_ACTIVE_STATUS}
        mock.get.return_value = mock
        self.assertTrue(check_session(Constants.EMPTY, mock, mock))

    def test_session_invalid(self):
        mock = MagicMock()
        mock.json.return_value = {Constants.STATUS: Constants.EMPTY}
        mock.get.return_value = mock
        self.assertFalse(check_session(Constants.EMPTY, mock, mock))

    def test_session_error(self):
        mock = MagicMock()
        mock.json.side_effect = Exception
        mock.get.return_value = mock
        self.assertFalse(check_session(Constants.EMPTY, mock, mock))
