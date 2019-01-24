# -*- coding: utf-8 -*-
"""
    test.IDummyClient
    ~~~~~~~~~~~~~~~~~
    
    Interface for dummy clients
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

class IDummyClient:
    def get_page_by_filter(self, correlation_id, filter, paging):
        raise NotImplementedError('Method from interface definition')

    def get_one_by_id(self, correlation_id, id):
        raise NotImplementedError('Method from interface definition')
        
    def create(self, correlation_id, item):
        raise NotImplementedError('Method from interface definition')

    def update(self, correlation_id, item):
        raise NotImplementedError('Method from interface definition')

    def delete_by_id(self, correlation_id, id):
        raise NotImplementedError('Method from interface definition')
