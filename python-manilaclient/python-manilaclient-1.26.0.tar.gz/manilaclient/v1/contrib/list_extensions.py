# Copyright 2013 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys
import warnings

from manilaclient.v2.contrib import list_extensions

warnings.warn(
    "Module manilaclient.v1.contrib.list_extensions is deprecated "
    "(taken as a basis for manilaclient.v2.contrib.list_extensions). "
    "The preferable way to get a client class or object is to use "
    "the manilaclient.client module.")


class MovedModule(object):
    def __init__(self, new_module):
        self.new_module = new_module

    def __getattr__(self, attr):
        return getattr(self.new_module, attr)

sys.modules["manilaclient.v1.contrib.list_extensions"] = MovedModule(
    list_extensions)
