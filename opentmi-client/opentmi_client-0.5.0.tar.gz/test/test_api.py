# pylint: disable=missing-docstring

import unittest
import os
from mock import mock, MagicMock, patch, call
from opentmi_client.api import Client, create, Event
from opentmi_client.utils import TransportException, OpentmiException
from opentmi_client.transport.transport import Transport


def mocked_post(*args, **kwargs):
    if args[1].get("exception") == "TransportException":
        raise TransportException("")
    elif args[1].get("exception") == 'OpentmiException':
        raise OpentmiException("")
    elif args[1].get("status_code") == 404:
        return None
    return args[1]

def mocked_put(*args, **kwargs):
    if args[1].get("exception") == "TransportException":
        raise TransportException("")
    elif args[1].get("exception") == 'OpentmiException':
        raise OpentmiException("")
    elif args[1].get("status_code") == 404:
        return None
    return args[1]

def mocked_get(*args, **kwargs):
    if kwargs.get('params', {}).get('tcid') == "notfound":
        return []
    return [{"tcid": "abc"}]

def mock_transport(transport):
    transport.set_token =  MagicMock()
    transport.set_host =  MagicMock()
    transport.get_json = MagicMock()
    transport.post_json = MagicMock()
    transport.put_json = MagicMock()

DUMMY_TOKEN = "abc"


class TestClient(unittest.TestCase):

    def test_create(self):
        client = create()
        self.assertIsInstance(client, Client)

    def test_token(self):
        tr_mock = Transport()
        mock_transport(tr_mock)
        tr_mock.has_token = MagicMock()
        def has_token(*args):
            return True
        tr_mock.has_token.return_value = True
        client = Client(transport=tr_mock)
        client.set_token(DUMMY_TOKEN)
        tr_mock.set_token.assert_called_once_with(DUMMY_TOKEN)
        self.assertEqual(client.is_logged_in, True)

    def test_login(self):
        tr_mock = Transport()
        mock_transport(tr_mock)
        client = Client(transport=tr_mock)
        client.login("user", "passwd")
        tr_mock.post_json.assert_called_once_with("http://127.0.0.1/auth/login",
                                                  {"email": "user", "password": "passwd"})
    def test_login_with_access_token(self):
        tr_mock = Transport()
        mock_transport(tr_mock)
        client = Client(transport=tr_mock)
        client.login_with_access_token("token", "github")
        tr_mock.post_json.assert_called_once_with("http://127.0.0.1/auth/github/token",
                                                  {"access_token": "token"})

    def test_logout(self):
        tr_mock = Transport()
        mock_transport(tr_mock)
        client = Client(transport=tr_mock)
        client.logout()
        tr_mock.set_token.assert_called_once_with(None)

    def test_version(self):
        client = Client()
        self.assertEqual(client.get_version(), 0)

    def test_try_login_raise_when_required(self):
        client = Client()
        with self.assertRaises(OpentmiException):
            client.try_login(raise_if_fail=True)

    def test_try_login_not_raise_by_default(self):
        client = Client()
        client.try_login()

    @mock.patch.dict(os.environ, {'OPENTMI_GITHUB_ACCESS_TOKEN': 'a.b.c'})
    @patch('opentmi_client.transport.Transport.post_json', side_effect=mocked_post)
    def test_try_login_token(self,  mock_post):
        client = Client()
        mock_post.assert_called_once_with("http://127.0.0.1/auth/github/token", {"token": "a.b.c"})

    @mock.patch.dict(os.environ, {'OPENTMI_USERNAME': 'username', "OPENTMI_PASSWORD": "passw"})
    @patch('opentmi_client.transport.Transport.post_json', side_effect=mocked_post)
    def test_try_login_token(self, mock_post):
        client = Client()
        mock_post.assert_called_once_with("http://127.0.0.1/auth/login", {"email": "username", "password": "passw"})

    @patch('opentmi_client.transport.Transport.post_json', side_effect=mocked_post)
    def test_upload_build(self, mock_post):
        client = Client()
        client.set_token(DUMMY_TOKEN)
        self.assertDictEqual(client.upload_build({}), {})
        mock_post.assert_called_once_with("http://127.0.0.1/api/v0/duts/builds", {})

    @patch('opentmi_client.transport.Transport.post_json', side_effect=mocked_post)
    def test_upload_build_exceptions(self, mock_post):
        client = Client()
        client.set_token(DUMMY_TOKEN)
        self.assertEqual(client.upload_build({"exception": "TransportException"}), None)
        self.assertEqual(client.upload_build({"exception": "OpentmiException"}), None)

    @patch('opentmi_client.transport.Transport.get_json', side_effect=mocked_get)
    @patch.dict(os.environ, {'OPENTMI_GITHUB_ACCESS_TOKEN': DUMMY_TOKEN})
    @patch('opentmi_client.transport.Transport.post_json', side_effect=mocked_post)
    def test_upload_results_new_test(self, mock_post, mock_get):
        client = Client()
        tc_data = {"tcid": "notfound"}
        client.upload_results(tc_data)
        mock_get.assert_called_once_with("http://127.0.0.1/api/v0/testcases", params={"tcid": "notfound"})
        mock_post.assert_has_calls([
            #call("http://127.0.0.1/auth/github/token", {"access_token": DUMMY_TOKEN}),
            call("http://127.0.0.1/api/v0/testcases", tc_data),
            call("http://127.0.0.1/api/v0/results", tc_data, files=None)])

    @patch('opentmi_client.transport.Transport.get_json', side_effect=mocked_get)
    @patch.dict(os.environ, {'OPENTMI_GITHUB_ACCESS_TOKEN': DUMMY_TOKEN})
    @patch('opentmi_client.transport.Transport.post_json', side_effect=mocked_post)
    def test_upload_results_update_test(self, mock_post, mock_get):
        client = Client()
        tc_data = {"tcid": "abc", "hauki": {"on": "kala"}}
        client.upload_results(tc_data)
        mock_get.assert_called_once_with("http://127.0.0.1/api/v0/testcases", params={"tcid": "abc"})
        mock_post.assert_has_calls([
            # call("http://127.0.0.1/auth/github/token", {"access_token": DUMMY_TOKEN}),
            call("http://127.0.0.1/api/v0/results", tc_data, files=None)
        ])

    @patch('opentmi_client.transport.Transport.get_json', side_effect=mocked_get)
    @patch.dict(os.environ, {'OPENTMI_GITHUB_ACCESS_TOKEN': DUMMY_TOKEN})
    @patch('opentmi_client.transport.Transport.post_json', side_effect=mocked_post)
    def test_get_test(self, mock_post, mock_get):
        client = Client()
        tc_data = {"tcid": "abc %s"}
        client.get_testcases(tc_data)
        mock_get.assert_called_once_with("http://127.0.0.1/api/v0/testcases", params={"tcid": "abc %s"})
        # mock_post.assert_called_once_with("http://127.0.0.1/auth/github/token", {"access_token": DUMMY_TOKEN})

    @patch('opentmi_client.transport.Transport.post_json', side_effect=mocked_post)
    def test_upload_event(self, mock_post):
        client = Client()
        client.set_token(DUMMY_TOKEN)
        event = Event()
        event.eid = "123"
        client.post_event(event)
        mock_post.assert_called_once_with("http://127.0.0.1/api/v0/events", {"id": "123"})

    @patch('opentmi_client.transport.Transport.post_json', side_effect=TransportException("error"))
    def test_upload_event_exception_transport(self, mock_post):
        client = Client()
        client.set_token(DUMMY_TOKEN)
        event = Event()
        self.assertEqual(client.post_event(event), None)

    @patch('opentmi_client.transport.Transport.post_json', side_effect=OpentmiException("error"))
    def test_upload_event_exceptions_opentmi(self, mock_post):
        client = Client()
        client.set_token(DUMMY_TOKEN)
        event = Event()
        self.assertEqual(client.post_event(event), None)
