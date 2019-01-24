# -*- coding: utf-8 -*-
"""
    tests.rest.test_DummyCommandableHttpClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import pytest

from pip_services3_commons.config import ConfigParams
from pip_services3_commons.refer import Descriptor, References, Referencer
from pip_services3_commons.run import Opener, Closer

from ..DummyController import DummyController
from .DummyClientFixture import DummyClientFixture
from .DummyCommandableHttpClient import DummyCommandableHttpClient
from ..services.DummyCommandableHttpService import DummyCommandableHttpService

rest_config = ConfigParams.from_tuples(
    'connection.host', 'localhost',
    'connection.port', 3001
)

class TestDummyCommandableHttpClient:
    references = None
    fixture = None

    @classmethod
    def setup_class(cls):
        cls.controller = DummyController()
        
        cls.service = DummyCommandableHttpService()
        cls.service.configure(rest_config)

        cls.client = DummyCommandableHttpClient()
        cls.client.configure(rest_config)

        cls.references = References.from_tuples(
            Descriptor("pip-services-dummies", "controller", "default", "default", "1.0"), cls.controller, 
            Descriptor("pip-services-dummies", "service", "http", "default", "1.0"), cls.service, 
            Descriptor("pip-services-dummies", "client", "http", "default", "1.0"), cls.client
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

