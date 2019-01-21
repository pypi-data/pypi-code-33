# coding: utf8
# Author:xuyang.li
# Date:2018/11/20
"""
    create product request
"""
from enosapi.request.EnOSRequest import EnOSRequest
from enosapi.util.const import Const


class CreateProductRequest(EnOSRequest):

    __url = '/connectService/products'
    __type = Const.request_post
    __context_type = 'application/json'

    def __init__(self, org_id, params):
        self.org_id = org_id
        self.params = params

    def get_request_url(self):
        return self.__url

    def get_request_type(self):
        return self.__type

    def get_content_type(self):
        return self.__context_type

    def get_params(self):
        return self.params
