# coding: utf8
# Author:Vincent Ong
# Date:18/01/2019
"""
    List Devices request
"""
from enosapi.request.EnOSRequest import EnOSRequest
from enosapi.util.const import Const


class ListDevicesRequest(EnOSRequest):

    __url = '/connectService/devices'
    __type = Const.request_get
    __context_type = 'application/json'

    def __init__(self, org_id, product_key, page_size, page_token):
        self.org_id = org_id 
        self.product_key = product_key
        self.page_size = page_size
        self.page_token = page_token

	#This parameters are added to take into account the app signing calculation
	self.params = {"productKey" : self.product_key, "pageSize" : self.page_size, "pageToken" : self.page_token}

    def get_request_url(self):
        return self.__url

    def get_request_type(self):
        return self.__type

    def get_content_type(self):
        return self.__context_type

    def get_params(self):
        return self.params

    def replace_params_and_headers(self):
        pass

    def get_replace_params_and_headers(self):
	    pass


