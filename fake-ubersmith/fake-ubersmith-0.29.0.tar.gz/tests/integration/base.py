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

import logging
import unittest

import ubersmith_client

logger = logging.getLogger()


class Base(unittest.TestCase):

    ub_client = None
    host = '127.0.0.1'
    port = 9131
    endpoint = 'http://{}:{}'.format(host, port)

    @classmethod
    def setUpClass(cls):
        cls.ub_client = ubersmith_client.api.init(
            url="{}/api/2.0/".format(cls.endpoint),
            user='username',
            password='password'
        )
