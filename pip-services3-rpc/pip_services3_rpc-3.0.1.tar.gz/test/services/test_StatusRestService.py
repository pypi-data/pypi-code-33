# -*- coding: utf-8 -*-
"""
    test_DummyRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy commandable HTTP service test

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json
import time

import requests
from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import References, Descriptor
from pip_services3_commons.run import Parameters
from pip_services3_components.info import ContextInfo
from pip_services3_rpc.services import StatusRestService


rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3004
)
 
class TestStatusRestService():
    service = None

    @classmethod
    def setup_class(cls):
        cls.service = StatusRestService()
        cls.service.configure(rest_config)

        contextInfo = ContextInfo()
        contextInfo.name = "Test"
        contextInfo.description = "This is a test container"

        cls.references = References.from_tuples(
            Descriptor("pip-services", "context-info", "default", "default", "1.0"), contextInfo,
            Descriptor("pip-services-dummies", "service", "http", "default", "1.0"), cls.service
        )

        cls.service.set_references(cls.references)


    def setup_method(self, method):
        self.service.open(None)


    def teardown_method(self, method):
        self.service.close(None)
 
    def test_status(self):
        time.sleep(2)
        result = self.invoke("/status")

        assert None != result

    def invoke(self, route):
        params = { }
        route = "http://localhost:3004" + route
        response = None
        timeout = 10000
        try:
            # Call the service
            response = requests.request('GET', route, params=params,  timeout=timeout)
            return response 
        except Exception as ex:
            return False