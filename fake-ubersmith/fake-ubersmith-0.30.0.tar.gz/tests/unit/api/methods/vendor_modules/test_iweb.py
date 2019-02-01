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
import json
import unittest

from flask import Flask

from fake_ubersmith.api.adapters.data_store import DataStore
from fake_ubersmith.api.methods.vendor_modules.iweb import IWeb
from fake_ubersmith.api.ubersmith import UbersmithBase


class TestIwebModule(unittest.TestCase):

    def setUp(self):
        self.data_store = DataStore()
        self.iweb = IWeb(self.data_store)

        self.app = Flask(__name__)
        self.base_iweb_api = UbersmithBase(self.data_store)

        self.iweb.hook_to(self.base_iweb_api)
        self.base_iweb_api.hook_to(self.app)

    def test_log_event_successfully(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "iweb.log_event",
                    "event_type": "Some event type",
                    "reference_type": "client",
                    "action": "Client Id 12345 performed a 'method'.",
                    "clientid": "clientid",
                    "user": "username",
                    "reference_id": "clientid"
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "1",
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )
        self.assertEqual(
            self.data_store.event_log[0],
            {
                "event_type": "Some event type",
                "reference_type": "client",
                "action": "Client Id 12345 performed a 'method'.",
                "clientid": "clientid",
                "user": "username",
                "reference_id": "clientid"
            }

        )

    def test_add_role_successfully(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "iweb.acl_admin_role_add",
                    'name': 'A Admin Role',
                    'descr': 'A Admin Role',
                    'acls[admin.portal][read]': 1,
                }
            )

        role_id = next(iter(self.data_store.roles))

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": role_id,
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )
        self.assertEqual(
            self.data_store.roles,
            {
                role_id: {
                    'role_id': role_id,
                    'name': 'A Admin Role',
                    'descr': 'A Admin Role',
                    'acls': {
                        'admin.portal': {'read': '1'}
                    }
                }
            }
        )

    def test_add_role_that_already_exists_fails(self):
        self.data_store.roles = {
            'some_role_id': {
                'role_id': 'some_role_id',
                'name': 'A Admin Role'
            }
        }

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "iweb.acl_admin_role_add",
                    'name': 'A Admin Role',
                    'descr': 'A Admin Role',
                    'acls[admin.portal][read]': 1,
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 1,
                "error_message": "The specified Role Name is already in use",
                "status": False
            }
        )

    def test_add_user_role_successfully(self):
        user_id = 'some_user_id'
        self.data_store.roles = {'a_role_id': {}, 'another_role_id': {}}
        with self.app.test_client() as c:
            c.post(
                'api/2.0/',
                data={
                    "method": "iweb.user_role_assign",
                    "user_id": user_id,
                    "role_id": "a_role_id"
                }
            )
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "iweb.user_role_assign",
                    "user_id": user_id,
                    "role_id": "another_role_id"
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "status": True,
                "error_code": None,
                "error_message": "",
                "data": 1
            }
        )
        self.assertEqual(
            self.data_store.user_mapping[user_id],
            {'roles': {'a_role_id', 'another_role_id'}}
        )

    def test_add_same_role_to_user_not_allowed(self):
        role_id = 'some_role_id'
        user_id = 'some_user_id'
        self.data_store.roles = {'1': {}}
        self.data_store.user_mapping[user_id] = {'roles': {role_id}}
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "iweb.user_role_assign",
                    "user_id": user_id,
                    "role_id": role_id
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "error_code": 1,
                "error_message": "Can't assign role with id '{}' to user "
                                 "with id '{}'".format(role_id, user_id),
                "status": False,
                "data": ""
            }
        )
