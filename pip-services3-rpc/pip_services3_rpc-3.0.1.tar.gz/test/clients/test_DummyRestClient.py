# -*- coding: utf-8 -*-
"""
    tests.rest.test_DummyRestClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import pytest

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import Descriptor, References, Referencer
from pip_services3_commons.run import Opener, Closer

from ..DummyController import DummyController
from .DummyClientFixture import DummyClientFixture
from .DummyRestClient import DummyRestClient
from ..services.DummyRestService import DummyRestService

rest_config = ConfigParams.from_tuples(
    'connection.host', 'localhost',
    'connection.port', 3000
)

class TestDummyRestClient:
    references = None
    fixture = None

    @classmethod
    def setup_class(cls):
        cls.controller = DummyController()
        
        cls.service = DummyRestService()
        cls.service.configure(rest_config)

        cls.client = DummyRestClient()
        cls.client.configure(rest_config)

        cls.references = References.from_tuples(
            Descriptor("pip-services-dummies", "controller", "default", "default", "1.0"), cls.controller, 
            Descriptor("pip-services-dummies", "service", "rest", "default", "1.0"), cls.service, 
            Descriptor("pip-services-dummies", "client", "rest", "default", "1.0"), cls.client
        )
        cls.client.set_references(cls.references)
        cls.service.set_references(cls.references)

        cls.fixture = DummyClientFixture(cls.client)

    def setup_method(self, method):
        self.service.open(None)
        self.client.open(None)

    def teardown_method(self, method):
        self.service.close(None)
        self.client.close(None)
        
    def test_crud_operations(self):
        self.fixture.test_crud_operations()

