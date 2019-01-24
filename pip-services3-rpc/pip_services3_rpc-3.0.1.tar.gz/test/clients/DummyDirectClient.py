# -*- coding: utf-8 -*-
"""
    test.rest.DummyDirectClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy direct client implementation
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_rpc.clients import DirectClient
from pip_services3_commons.refer import Descriptor
from .IDummyClient import IDummyClient

class DummyDirectClient(DirectClient, IDummyClient):

    def __init__(self):
        super(DummyDirectClient, self).__init__()
        self._dependency_resolver.put('controller', Descriptor('pip-services-dummies', 'controller', '*', '*', '*'))


    def get_page_by_filter(self, correlation_id, filter, paging):
        timing = self._instrument(correlation_id, 'dummy.get_page_by_filter')
        try:
            return self._controller.get_page_by_filter(correlation_id, filter, paging)
        finally:
            timing.end_timing()


    def get_one_by_id(self, correlation_id, id):
        timing = self._instrument(correlation_id, 'dummy.get_one_by_id')
        try:
            return self._controller.get_one_by_id(correlation_id, id)
        finally:
            timing.end_timing()


    def create(self, correlation_id, item):
        timing = self._instrument(correlation_id, 'dummy.create')
        try:
            return self._controller.create(correlation_id, item)
        finally:
            timing.end_timing()


    def update(self, correlation_id, item):
        timing = self._instrument(correlation_id, 'dummy.update')
        try:
            return self._controller.update(correlation_id, item)
        finally:
            timing.end_timing()


    def delete_by_id(self, correlation_id, id):
        timing = self._instrument(correlation_id, 'dummy.delete_by_id')
        try:
            return self._controller.delete_by_id(correlation_id, id)
        finally:
            timing.end_timing()
