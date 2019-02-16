#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Message List, outer wrapper for Object, Scene, and Property messages.

Generally not used directly by client applications.
"""

"""
Apache2 License Notice
Copyright 2018 Alex Barry
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import copy

class AeselDataList(object):
    def __init__(self):
        self.num_records = None
        self.start_record = None
        self.error_code = None
        self.error_message = None
        self.event_destination_port = None
        self.event_destination_key = None
        self.event_destination_salt = None
        self.data = []

    def to_dict(self, data_type):
        return_dict = copy.deepcopy(vars(self))
        return_dict[data_type] = []
        del return_dict["data"]
        for elt in self.data:
            elt_dict = elt.to_dict()
            return_dict[data_type].append(elt_dict)
        return return_dict
