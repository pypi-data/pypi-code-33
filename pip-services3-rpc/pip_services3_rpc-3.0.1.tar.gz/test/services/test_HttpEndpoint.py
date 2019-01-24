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
from pip_services3_rpc.services import HttpEndpoint
from ..Dummy import Dummy
from ..DummyController import DummyController
from ..services.DummyRestService import DummyRestService

DUMMY1 = Dummy(None, 'Key 1', 'Content 1')
DUMMY2 = Dummy(None, 'Key 2', 'Content 2')

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3005
)
 
class TestHttpEndpointService():
    service = None
    endpoint = None

    @classmethod
    def setup_class(cls):
        cls.controller = DummyController()
        cls.service = DummyRestService()
        cls.service.configure(ConfigParams.from_tuples(
            'base_route', '/api/v1'
        ))

        cls.endpoint = HttpEndpoint()
        cls.endpoint.configure(rest_config)

        cls.references = References.from_tuples(
            Descriptor("pip-services-dummies", "controller", "default", "default", "1.0"), cls.controller,
            Descriptor('pip-services-dummies', 'service', 'rest', 'default', '1.0'), cls.service,
            Descriptor('pip-services', 'endpoint', 'http', 'default', '1.0'), cls.endpoint 
        )

        cls.service.set_references(cls.references)
        cls.endpoint.open(None)
        cls.service.open(None)


    def setup_method(self, method):
        pass


    def teardown_method(self, method):
        self.service.close(None)
        self.endpoint.close(None)


    def test_crud_operations(self):
        time.sleep(2)
        dummy1 = self.invoke("/api/v1/dummies", DUMMY1)

        assert None != dummy1
        assert DUMMY1['key'] == dummy1['key']
        assert DUMMY1['content'] == dummy1['content']

    def invoke(self, route, entity):
        params = { }
        route = "http://localhost:3005" + route
        response = None
        timeout = 10000
        try:
            # Call the service
            data = json.dumps(entity)
            response = requests.request('POST', route, params=params, json=data, timeout=timeout)
            return response.json()
        except Exception as ex:
            return False