# -*- coding: utf-8 -*-
"""
    test.services.TestDummyCommandableHttpService
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
from pip_services3_commons.data import IdGenerator

from ..Dummy import Dummy
from ..DummyController import DummyController
from .DummyCommandableHttpService import DummyCommandableHttpService


rest_config = ConfigParams.from_tuples(
    'connection.host', 'localhost',
    'connection.port', 3002
)

DUMMY1 = Dummy(None, 'Key 1', 'Content 1')
DUMMY2 = Dummy(None, 'Key 2', 'Content 2')

#todo return dummy object from response in invoke()
class TestDummyCommandableHttpService():
    controller = None
    service = None

    @classmethod
    def setup_class(cls):
        cls.controller = DummyController()

        cls.service = DummyCommandableHttpService()
        cls.service.configure(rest_config)

        cls.references = References.from_tuples(
            Descriptor("pip-services-dummies", "controller", "default", "default", "1.0"), cls.controller,
            Descriptor("pip-services-dummies", "service", "http", "default", "1.0"), cls.service
        )

        cls.service.set_references(cls.references)


    def setup_method(self, method):
        self.service.open(None)


    def teardown_method(self, method):
        self.service.close(None)

    # #todo
    def test_crud_operations(self):
        time.sleep(2)
        # Create one dummy
        dummy1 = self.invoke("/dummies/create_dummy", Parameters.from_tuples("dummy", DUMMY1))
        
        assert None != dummy1
        assert DUMMY1['key'] == dummy1['key']
        assert DUMMY1['content'] == dummy1['content']

        # Create another dummy
        dummy2 = self.invoke("/dummies/create_dummy", Parameters.from_tuples("dummy", DUMMY2))

        assert None != dummy2
        assert DUMMY2['key'] == dummy2['key']
        assert DUMMY2['content'] == dummy2['content']

        # Get all dummies
        dummies = self.invoke("/dummies/get_dummies", Parameters.from_tuples("dummies"))

        assert None != dummies
        assert 2 == len(dummies['data'])

        # Update the dummy
        dummy1['content'] = "Updated Content 1"
        dummy = self.invoke("/dummies/update_dummy", Parameters.from_tuples("dummy", dummy1))

        assert None != dummy
        assert dummy1['id'] == dummy['id']
        assert dummy1['key'] == dummy['key']
        assert "Updated Content 1" == dummy['content']

        # Delete the dummy
        self.invoke("/dummies/delete_dummy_by_id", Parameters.from_tuples("dummy_id", dummy1['id']))

        # Try to get deleted dummy
        get_dummy = self.invoke("/dummies/get_dummy_by_id", Parameters.from_tuples("dummy_id", dummy1['id']))
        assert False == get_dummy


    def invoke(self, route, entity):
        params = {}
        route = "http://localhost:3002" + route
        response = None
        timeout = 10000
        try:
            # Call the service
            data = json.dumps(entity)
            response = requests.request('POST', route, params=params, json=data, timeout=timeout)
            return response.json()
        except Exception as ex:
            return False