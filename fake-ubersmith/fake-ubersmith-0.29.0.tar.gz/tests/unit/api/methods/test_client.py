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
from unittest import mock

from fake_ubersmith.api.adapters.data_store import DataStore
from fake_ubersmith.api.methods.client import Client
from fake_ubersmith.api.ubersmith import FakeUbersmithError, UbersmithBase
from flask import Flask
from tests.unit.api.methods import ApiTestBase


class TestClientModule(ApiTestBase):
    def setUp(self):
        self.data_store = DataStore()
        self.client = Client(self.data_store)

        self.app = Flask(__name__)
        self.base_uber_api = UbersmithBase(self.data_store)

        self.client.hook_to(self.base_uber_api)
        self.base_uber_api.hook_to(self.app)

    def test_client_add_creates_a_client(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "client.add",
                    "first": "John",
                    "last": "Smith",
                    "email": "john.smith@invalid.com",
                    "uber_login": "john",
                    "uber_pass": "smith"
                }
            )

        self.assertEqual(resp.status_code, 200)
        body = json.loads(resp.data.decode('utf-8'))
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(body.get("error_code"))
        self.assertTrue(body.get("status"))
        self.assertEqual(body.get("error_message"), "")
        self.assertIsInstance(body.get("data"), str)
        self.assertEqual(self.data_store.clients[0]["login"], "john")
        self.assertIsInstance(self.data_store.contacts[0]["contact_id"], str)
        self.assertEqual(self.data_store.contacts[0]["client_id"], body.get("data"))
        self.assertEqual(self.data_store.contacts[0]["description"], "Primary Contact")

    @mock.patch("fake_ubersmith.api.methods.client.a_random_id")
    def test_update_a_client(self, random_id_mock):
        random_id_mock.return_value = 1
        with self.app.test_client() as c:
            self._assert_success(c.post('api/2.0/', data={"method": "client.add",
                                                          "first": "name",
                                                          "last": "lastname",
                                                          "email": "email@here.invalid",
                                                          "uber_login": "login",
                                                          "uber_pass": "password"}),
                                 content="1")

            self._assert_success(c.post('api/2.0/', data={"method": "client.update",
                                                          "client_id": "1",
                                                          "first": "name-updated",
                                                          "last": "lastname-updated",
                                                          "email": "email-updated@here.invalid",
                                                          "uber_login": "login-updated"}),
                                 content=True)

            self._assert_success(
                c.post('api/2.0/', data={"method": "client.get", "client_id": "1"}),
                content={
                    "clientid": "1",
                    "first": "name-updated",
                    "last": "lastname-updated",
                    "email": "email-updated@here.invalid",
                    "login": "login-updated"
                }
            )

    def test_client_get_returns_successfully(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "client.add",
                    "first": "John",
                }
            )
            client_id = json.loads(resp.data.decode('utf-8')).get("data")

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "client.get", "client_id": client_id}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"clientid": client_id, "first": "John"},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_client_get_with_user_login_returns_successfully(self):
        self.data_store.clients = [{"clientid": "1", "contact_id": '0'}]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "client.get", "user_login": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"clientid": "1"},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_client_get_errs_when_no_match(self):
        self.data_store.clients = [{"clientid": "100"}]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "client.get", "client_id": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 1,
                "error_message": "Client ID '1' not found.",
                "status": False
            }
        )

    def test_client_contact_add_creates_a_contact(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "client.contact_add",
                    "first": "John",
                    "last": "Smith",
                    "email": "john.smith@invalid.com",
                    "uber_login": "john",
                    "uber_pass": "smith"
                }
            )

        body = json.loads(resp.data.decode('utf-8'))
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(body.get("error_code"))
        self.assertTrue(body.get("status"))
        self.assertEqual(body.get("error_message"), "")
        self.assertIsInstance(body.get("data"), str)

    def test_client_contact_get_returns_error_when_empty_payload_provided(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "client.contact_get",
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 1,
                "error_message": "No contact ID specified",
                "status": False
            }
        )

    def test_client_contact_get_with_bad_contact_id_returns_error(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "client.contact_get",
                    "contact_id": "bad"
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 1,
                "error_message": "Invalid contact_id specified.",
                "status": False
            }
        )

    def test_client_contact_get_with_bad_user_login_returns_error(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "client.contact_get",
                    "user_login": "bad"
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 1,
                "error_message": "Invalid user_login specified.",
                "status": False
            }
        )

    def test_client_contact_get_with_contact_id_returns_a_contact(self):
        a_contact = {"contact_id": "100"}

        self.data_store.contacts.append(a_contact)

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "client.contact_get",
                    "contact_id": "100",
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": a_contact,
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_client_contact_list_returns_contacts_for_given_client_id(self):
        contact_1 = {
            "contact_id": '1',
            "client_id": '100',
            "real_name": "John Patate",
            "email": "john.patate@fake.invalid"
        }
        contact_2 = {
            "contact_id": '1',
            "client_id": '101',
            "real_name": "The Dude",
            "email": "the.dude@fake.invalid"
        }
        contact_3 = {
            "contact_id": '2',
            "client_id": '100',
            "real_name": "Joe Poutine",
            "email": "joe.poutine@fake.invalid"
        }

        self.data_store.contacts.extend([contact_1, contact_2, contact_3])

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "client.contact_list",
                    "client_id": "100",
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {'1': contact_1, '2': contact_3},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_client_contact_list_with_bad_client_id_returns_error(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "client.contact_list",
                    "client_id": "does_not_exist"
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 1,
                "error_message": "Invalid client_id specified.",
                "status": False
            }
        )

    def test_client_contact_get_with_user_login_returns_a_contact(self):
        a_contact = {
            "contact_id": "100",
            "first": "John",
            "last": "Smith",
            "email": "john.smith@invalid.com",
            "uber_login": "john",
        }

        self.data_store.contacts.append(a_contact)

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "client.contact_get",
                    "user_login": "john",
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": a_contact,
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_client_cc_add_is_successful(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "client.cc_add", "client_id": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": 1,
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_client_cc_add_fails_returns_error(self):
        self.client.credit_card_response = FakeUbersmithError(999, 'oh fail')

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "client.cc_add", "client_id": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 999,
                "error_message": "oh fail",
                "status": False}
        )

    def test_client_cc_update_is_successful(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "client.cc_update", "client_id": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": True,
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_client_cc_update_fails_returns_error(self):
        self.client.credit_card_response = FakeUbersmithError(999, 'oh fail')

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "client.cc_update", "client_id": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 999,
                "error_message": "oh fail",
                "status": False
            }
        )

    def test_client_cc_info_with_billing_info_id(self):
        self.data_store.credit_cards = [{"billing_info_id": "123"}]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "client.cc_info", "billing_info_id": "123"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"123": {"billing_info_id": "123"}},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_client_cc_info_with_client_id(self):
        self.data_store.credit_cards = [
            {
                "clientid": "1",
                "billing_info_id": "123"
            }
        ]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "client.cc_info", "client_id": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"123": {"billing_info_id": "123", "clientid": "1"}},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_client_cc_info_fails(self):
        self.data_store.credit_cards = [
            {
                "clientid": "1",
                "billing_info_id": "123"
            }
        ]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "client.cc_info", "bogus": "thing"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 1,
                "error_message":
                    "request failed: client_id parameter not supplied",
                "status": False
            }
        )

    def test_client_cc_delete_is_successful(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "client.cc_delete", "client_id": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": True,
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_client_cc_delete_fails(self):
        self.client.credit_card_delete_response = FakeUbersmithError(
            999, 'oh fail'
        )

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "client.cc_delete", "client_id": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 999,
                "error_message": "oh fail",
                "status": False
            }
        )
