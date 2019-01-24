# -*- coding: utf-8 -*-
"""
    test.rest.DummyCommandableHttpClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy commandable HTTP client
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.data import DataPage
from pip_services3_rpc.clients import CommandableHttpClient
from .IDummyClient import IDummyClient

class DummyCommandableHttpClient(CommandableHttpClient, IDummyClient):
    
    def __init__(self):
        super(DummyCommandableHttpClient, self).__init__('dummies')


    def get_page_by_filter(self, correlation_id, filter, paging):
        result = self.call_command(
            'get_dummies',
            correlation_id,
            {
                'filter': filter,
                'paging': paging
            }
        )
        return DataPage(result['data'], result['total'])
        
    def get_one_by_id(self, correlation_id, id):
        return self.call_command(
            'get_dummy_by_id', 
            correlation_id,
            {
                'dummy_id': id
            }
        )
        
    def create(self, correlation_id, entity):
        return self.call_command(
            'create_dummy', 
            correlation_id, 
            {
                'dummy': entity
            }
        )

    def update(self, correlation_id, entity):
        return self.call_command(
            'update_dummy', 
            correlation_id, 
            {
                'dummy': entity
            }
        )

    def delete_by_id(self, correlation_id, id):
        return self.call_command(
            'delete_dummy_by_id',
            correlation_id,
            {
                'dummy_id': id
            }
        )
