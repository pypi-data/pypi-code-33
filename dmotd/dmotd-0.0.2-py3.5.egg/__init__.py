# Copyright (c) 2019 Monolix
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from requests import get
import json

class DMOTD(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint
    
    def raw(self):
        response = get(self.endpoint + "/raw")
        return response.text
    
    def json(self):
        response = get(self.endpoint + "/json")
        return response.json()
