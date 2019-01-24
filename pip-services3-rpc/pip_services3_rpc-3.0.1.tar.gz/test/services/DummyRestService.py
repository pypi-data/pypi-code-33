# -*- coding: utf-8 -*-
"""
    test.rest.DummyRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy REST service
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import threading

from pip_services3_commons.data import FilterParams, PagingParams, IdGenerator
from pip_services3_commons.refer import Descriptor
from pip_services3_rpc.services import RestService

class DummyRestService(RestService):
    _logic = None

    def __init__(self):
        super(DummyRestService, self).__init__()

    def set_references(self, references):
        self._logic = references.get_one_required(
            Descriptor("pip-services-dummies", "controller", "*", "*", "*")
        )

        super(DummyRestService, self).set_references(references)

    def get_page_by_filter(self):
        correlation_id = self.get_correlation_id()
        filter = self.get_filter_params()
        paging = self.get_paging_params()
        return self.send_result(self._logic.get_page_by_filter(correlation_id, filter, paging))

    def get_one_by_id(self, id):
        correlation_id = self.get_correlation_id()
        return self.send_result(self._logic.get_one_by_id(correlation_id, id))

    def create(self):
        correlation_id = self.get_correlation_id()
        entity = self.get_data()
        return self.send_created_result(self._logic.create(correlation_id, entity))

    def update(self, id):
        correlation_id = self.get_correlation_id()
        entity = self.get_data()
        return self.send_result(self._logic.update(correlation_id, entity))

    def delete_by_id(self, id):
        correlation_id = self.get_correlation_id()
        self._logic.delete_by_id(correlation_id, id)
        return self.send_deleted_result()

    def handled_error(self):
        raise UnsupportedError('NotSupported', 'Test handled error')

    def unhandled_error(self):
        raise TypeError('Test unhandled error')

    def add_route(self):
        self.register_route('get', '/dummies', None, self.get_page_by_filter)
        self.register_route('get', '/dummies/<id>', None, self.get_one_by_id)
        self.register_route('post', '/dummies', None, self.create)
        self.register_route('put', '/dummies/<id>', None, self.update)
        self.register_route('delete', '/dummies/<id>', None, self.delete_by_id)
        self.register_route('get', '/dummies/handled_error', None, self.handled_error)
        self.register_route('get', '/dummies/unhandled_error', None, self.unhandled_error)
