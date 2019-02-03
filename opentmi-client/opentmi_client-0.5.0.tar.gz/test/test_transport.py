# pylint: disable=missing-docstring

import unittest
from mock import patch
from requests import Response, RequestException
from opentmi_client.transport import Transport
from opentmi_client.utils.exceptions import TransportException

# This method will be used by the mock to replace requests.get, post, put
def mocked_requests(*args, **kwargs):
    class MockResponse(Response):
        def __init__(self, json_data, status_code):
            Response.__init__(self)
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'RequestException':
        raise RequestException()
    elif args[0] == 'ValueError':
        raise ValueError("")
    elif args[0] == 'TypeError':
        raise TypeError("")
    elif args[0] == 'status_300':
        return MockResponse(None, 300)

    return MockResponse({}, 200)


class TestRequest(unittest.TestCase):
    def test_is_success(self):
        resp = Response()
        resp.status_code = 200
        self.assertTrue(Transport.is_success(resp))
        resp.status_code = 299
        self.assertTrue(Transport.is_success(resp))
        resp.status_code = 300
        self.assertFalse(Transport.is_success(resp))
        resp.status_code = 199
        self.assertFalse(Transport.is_success(resp))

    def test_set_host(self):
        transport = Transport()
        HOST = "127.0.0.1"
        transport.set_host(HOST)
        self.assertEqual(transport.token, None)
        self.assertEqual(transport.host, "http://"+HOST)

        transport.set_host("http://a.b.c@"+HOST)
        self.assertEqual(transport.token, "a.b.c")
        self.assertEqual(transport.host, "http://"+HOST)

        transport.set_host("https://aa.bb.cc@"+HOST)
        self.assertEqual(transport.token, "aa.bb.cc")
        self.assertEqual(transport.host, "https://"+HOST)

    def test_get_json_not_found(self):
        transport = Transport()
        with self.assertRaises(TransportException):
            transport.get_json("localhost")

    def test_get_post_not_found(self):
        transport = Transport()
        with self.assertRaises(TransportException):
            transport.post_json("localhost", {})

    def test_get_put_not_found(self):
        transport = Transport()
        with self.assertRaises(TransportException):
            transport.put_json("localhost", {})

    def test_get_json(self):
        transport = Transport()
        transport.set_token("mytoken")
        url = "https://jsonplaceholder.typicode.com/posts"
        self.assertIsInstance(transport.get_json(url), list)

    def test_get_post_not_found(self):
        transport = Transport()
        url = "https://jsonplaceholder.typicode.com/posts/a"
        self.assertEqual(transport.get_json(url), None)

    def test_post_json(self):
        transport = Transport()
        url = "https://jsonplaceholder.typicode.com/posts"
        data = {
            "title": "foo",
            "body": 'bar',
            "userId": 1
        }
        self.assertIsInstance(transport.post_json(url, data), dict)

    def test_put_json(self):
        transport = Transport()
        url = "https://jsonplaceholder.typicode.com/posts/1"
        data = {
            "title": "foo",
            "body": 'bar',
            "userId": 1
        }
        self.assertIsInstance(transport.put_json(url, data), dict)

    @patch('requests.get', side_effect=mocked_requests)
    def test_get_json_exceptions(self, mock_get):
        transport = Transport()
        with self.assertRaises(TransportException):
            transport.get_json("RequestException")
        with self.assertRaises(TransportException):
            transport.get_json("ValueError")
        with self.assertRaises(TransportException):
            transport.get_json("TypeError")
        with self.assertRaises(TransportException):
            transport.get_json("status_300")

    @patch('requests.post', side_effect=mocked_requests)
    def test_post_json_exceptions(self, mock_get):
        transport = Transport()
        with self.assertRaises(TransportException):
            transport.post_json("RequestException", {})
        with self.assertRaises(TransportException):
            transport.post_json("ValueError", {})
        with self.assertRaises(TransportException):
            transport.post_json("TypeError", {})
        with self.assertRaises(TransportException):
            transport.post_json("status_300", {})

    @patch('requests.put', side_effect=mocked_requests)
    def test_put_json_exceptions(self, mock_get):
        transport = Transport()
        with self.assertRaises(TransportException):
            transport.put_json("RequestException", {})
        with self.assertRaises(TransportException):
            transport.put_json("ValueError", {})
        with self.assertRaises(TransportException):
            transport.put_json("TypeError", {})
        with self.assertRaises(TransportException):
            transport.put_json("status_300", {})
