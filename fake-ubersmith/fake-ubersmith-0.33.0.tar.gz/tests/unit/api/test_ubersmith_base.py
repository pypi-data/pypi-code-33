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
import unittest

from flask import Flask

from fake_ubersmith.api.adapters.data_store import DataStore
from fake_ubersmith.api.ubersmith import UbersmithBase


class TestAdministrativeLocal(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        data_store = DataStore()

        self.ubersmith_base = UbersmithBase(data_store)
        self.ubersmith_base.hook_to(self.app)

    def test_enable_crash_mode(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "hidden.enable_crash_mode",
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.ubersmith_base.crash_mode)

    def test_disable_crash_mode(self):
        self.ubersmith_base.crash_mode = True

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "hidden.disable_crash_mode",
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.ubersmith_base.crash_mode)

    def test_any_api_call_will_return_500_when_crash_mode_enabled(self):
        self.ubersmith_base.crash_mode = True

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "any.api_call",
                }
            )

        self.assertEqual(resp.status_code, 500)
