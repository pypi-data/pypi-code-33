# Copyright 2017 Internap.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import ABCMeta, abstractmethod

from flask import current_app


class Base(metaclass=ABCMeta):
    def __init__(self, data_store=None):
        self.data_store = data_store
        self.app = None
        self.methods = {}

    @property
    def logger(self):
        return current_app.logger

    @abstractmethod
    def hook_to(self, entity):
        pass
