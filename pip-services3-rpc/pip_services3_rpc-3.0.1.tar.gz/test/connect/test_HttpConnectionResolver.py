# -*- coding: utf-8 -*-
"""
    tests.connect.test_HttpConnectionResolver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from pip_services3_commons.config import ConfigParams
from pip_services3_rpc.connect import HttpConnectionResolver

class TestHttpConnectionResolver():
    def test_connection_params(self):
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples("connection.protocol", "http",
                                                               "connection.host", "somewhere.com",
                                                               "connection.port", 123))
        connection = connection_resolver.resolve(None)

        assert connection.get_protocol() == "http"
        assert connection.get_host() == "somewhere.com"
        assert connection.get_port() == 123
        assert connection.get_uri() == "http://somewhere.com:123"

    def test_connection_uri(self):
        # pass
        connection_resolver = HttpConnectionResolver()
        connection_resolver.configure(ConfigParams.from_tuples("connection.uri", "https://somewhere.com:123"))

        connection = connection_resolver.resolve(None)

        assert connection.get_protocol() == "https"
        assert connection.get_host() == "somewhere.com"
        assert connection.get_port() == 123
        assert connection.get_uri() == "https://somewhere.com:123"
