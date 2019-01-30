# -*- coding: utf-8 -*-
"""
TestConnection
"""
import pytest
import pyprimed


@pytest.mark.unit
class TestConnection:

    def test_from_uri_http_valid(self):
        from pyprimed.util import Connection
        c = Connection.from_uri("http://user:password@localhost:5000")
        assert c._username == "user"
        assert c._password == "password"
        assert c._scheme == "http"
        assert c._hostname == "localhost"
        assert c._port == 5000

    def test_from_uri_http_missing_port(self):
        from pyprimed.util import Connection
        with pytest.raises(ValueError):
            c = Connection.from_uri("http://user:password@localhost")

    def test_from_uri_http_missing_credentials(self):
        from pyprimed.util import Connection
        with pytest.raises(ValueError):
            c = Connection.from_uri("http://@localhost:5000")

    def test_from_uri_http_missing_username(self):
        from pyprimed.util import Connection
        with pytest.raises(ValueError):
            c = Connection.from_uri("http://:password@localhost:5000")

    def test_from_uri_https_valid(self):
        from pyprimed.util import Connection
        c = Connection.from_uri("https://user:password@localhost")
        assert c._username == "user"
        assert c._password == "password"
        assert c._scheme == "https"
        assert c._hostname == "localhost"
        assert c._port == 443

    def test_hmac_header(self):
        from pyprimed.util import Connection
        c = Connection.from_uri("http://user:password@localhost:5000")
        assert c.hmac_header("pubkey", "secretkey", 1) == {
            'X-Authorization-Nonce': '1',
            'X-Authorization-Signature': '4c78d35e558d3acb7e6a90ef617c86bf688bb3e8140895746b6321cd2c856eb735c69e64cb6ea037da0a6674cdd9548c5e238ba53a1e08757e3379e54f8908e0',
            'X-Authorization-Key': 'pubkey'}

    def test_baseurl(self):
        from pyprimed.util import Connection
        c = Connection.from_uri("http://user:password@localhost:5000")
        assert c.baseurl == "http://localhost:5000/api/v1"

    def test_dictionary_merge(self):
        from pyprimed.util import Dictionary
        a = {"key1": "value", "key2": 1, "key3": 1.0}
        b = {"key3": "value2", "key4": {"nestedkey": "nestedvalue"}, "key5": [1.0, 2.0]}
        c = Dictionary.merge(a, b)
        assert c == {'key1': 'value', 'key2': 1, 'key3': 'value2', 'key4': {'nestedkey': 'nestedvalue'}, 'key5': [1.0, 2.0]}