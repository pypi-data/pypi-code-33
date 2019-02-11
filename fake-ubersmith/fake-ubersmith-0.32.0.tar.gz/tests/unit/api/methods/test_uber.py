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

from flask import Flask

from fake_ubersmith.api.adapters.data_store import DataStore
from fake_ubersmith.api.methods.client import Client
from fake_ubersmith.api.methods.uber import Uber
from fake_ubersmith.api.ubersmith import FakeUbersmithError, UbersmithBase
from tests.unit.api.methods import ApiTestBase


class TestUberModule(ApiTestBase):

    def setUp(self):
        self.data_store = DataStore()
        self.uber = Uber(self.data_store)
        self.client = Client(self.data_store)

        self.app = Flask(__name__)
        self.base_uber_api = UbersmithBase(self.data_store)

        self.uber.hook_to(self.base_uber_api)
        self.client.hook_to(self.base_uber_api)
        self.base_uber_api.hook_to(self.app)

    def test_service_plan_get_returns_if_service_plan_found(self):
        self.data_store.service_plans = [{"plan_id": "1"}]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "uber.service_plan_get", "plan_id": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"plan_id": "1"},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_service_plan_get_errs_if_service_plan_not_found(self):
        self.data_store.service_plans = [{"plan_id": 1}]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "uber.service_plan_get", "plan_id": "100"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 3,
                "error_message": "No Service Plan found",
                "status": False
            }
        )

    def test_service_plan_get_errs_with_service_plan_error(self):
        self.uber.service_plan_error = FakeUbersmithError(
            999, 'some error'
        )

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "uber.service_plan_get", "plan_id": "100"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 999,
                "error_message": "some error",
                "status": False
            }
        )

    def test_service_plan_list_returns_all_plans(self):
        self.data_store.service_plans_list = {
            "1": {"code": "42"},
            "2": {"code": "99"}
        }

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "uber.service_plan_list"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"1": {"code": "42"}, "2": {"code": "99"}},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_service_plan_list_returns_plans_matching_code(self):
        self.data_store.service_plans_list = {
            "1": {"plan_id": "1", "code": "42"},
            "2": {"plan_id": "1", "code": "99"}
        }

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "uber.service_plan_list", 'code': '42'}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"1": {"code": "42", "plan_id": "1"}},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    @mock.patch("fake_ubersmith.api.methods.client.a_random_id")
    def test_check_login_succesfully_for_client(self, random_id_mock):
        random_id_mock.return_value = 1
        with self.app.test_client() as c:
            self._assert_success(c.post('api/2.0/', data={"method": "client.add",
                                                          "first": "name",
                                                          "last": "lastname",
                                                          "email": "email@here.invalid",
                                                          "uber_login": "login",
                                                          "uber_pass": "password"}),
                                 content="1")

            self._assert_success(
                c.post('api/2.0/',
                       data={
                           "method": "uber.check_login",
                           "login": "login",
                           "pass": "password"
                       }),
                content={
                    "id": "1",
                    "login": "login",
                    "client_id": "1",
                    "contact_id": 0,
                    "fullname": "name lastname",
                    "email": "email@here.invalid",
                    "last_login": None,
                    "password_timeout": "0",
                    "password_changed": "1549380089",
                    "type": "client"
                }
            )

    @mock.patch("fake_ubersmith.api.methods.client.a_random_id")
    def test_check_login_succesfully_for_client_bare_info(self, random_id_mock):
        random_id_mock.return_value = 1
        with self.app.test_client() as c:
            self._assert_success(c.post('api/2.0/', data={"method": "client.add",
                                                          "uber_login": "login",
                                                          "uber_pass": "password"}),
                                 content="1")

            self._assert_success(
                c.post('api/2.0/',
                       data={
                           "method": "uber.check_login",
                           "login": "login",
                           "pass": "password"
                       }),
                content={
                    "id": "1",
                    "login": "login",
                    "client_id": "1",
                    "contact_id": 0,
                    "fullname": "",
                    "email": "",
                    "last_login": None,
                    "password_timeout": "0",
                    "password_changed": "1549380089",
                    "type": "client"
                }
            )

    def test_check_login_failed(self):
        self.data_store.clients = [
            {
                'clientid': '1',
                'first': 'John',
                'last': 'Smith',
                'email': 'john.smith@invalid.com',
                'login': 'john',
                'uber_pass': 'smith',
            }
        ]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "uber.check_login",
                    "login": "john",
                    "pass": "doe"
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 3,
                "error_message": "Invalid login or password.",
                "status": False
            }
        )

    @mock.patch("fake_ubersmith.api.methods.client.a_random_id")
    def test_check_login_successfully_for_contact(self, random_id_mock):
        random_id_mock.return_value = 1
        with self.app.test_client() as c:
            self._assert_success(c.post('api/2.0/',
                                        data={
                                            "method": "client.contact_add",
                                            "client_id": "12345",
                                            "real_name": "my real name",
                                            "email": "wat@wat.invalid",
                                            "login": "line",
                                            "password": "doe"}),
                                 content="1")

            self._assert_success(
                c.post('api/2.0/',
                       data={
                           "method": "uber.check_login",
                           "login": "line",
                           "pass": "doe"
                       }),
                content={
                    "id": "12345-1",
                    "login": "line",
                    "client_id": "12345",
                    "contact_id": "1",
                    "fullname": "my real name",
                    "email": "wat@wat.invalid",
                    "last_login": None,
                    "password_timeout": "0",
                    "password_changed": "1549380089",
                    "type": "contact"
                }
            )

    @mock.patch("fake_ubersmith.api.methods.client.a_random_id")
    def test_check_login_successfully_for_contact_bare_info(self, random_id_mock):
        random_id_mock.return_value = 1
        with self.app.test_client() as c:
            self._assert_success(c.post('api/2.0/',
                                        data={
                                            "method": "client.contact_add",
                                            "client_id": "12345",
                                            "login": "line",
                                            "password": "doe"}),
                                 content="1")

            self._assert_success(
                c.post('api/2.0/',
                       data={
                           "method": "uber.check_login",
                           "login": "line",
                           "pass": "doe"
                       }),
                content={
                    "id": "12345-1",
                    "login": "line",
                    "client_id": "12345",
                    "contact_id": "1",
                    "fullname": "",
                    "email": "@",
                    "last_login": None,
                    "password_timeout": "0",
                    "password_changed": "1549380089",
                    "type": "contact"
                }
            )

    def test_get_admin_roles_when_passing_valid_user_id_and_role_id(self):
        role_id = "some_role_id"
        self.data_store.roles = {
            role_id: {
                'role_id': role_id,
                'name': 'A Admin Role',
                'descr': 'A Admin Role'
            }
        }
        self.data_store.user_mapping = {
            "some_user_id": {"roles": {role_id}}
        }

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "uber.acl_admin_role_get",
                    "role_id": role_id,
                    "userid": "some_user_id",
                }
            )

        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "status": True,
                "error_code": None,
                "error_message": "",
                "data": {
                    role_id: {
                        "role_id": role_id,
                        'name': 'A Admin Role',
                        'descr': 'A Admin Role'
                    }
                }
            }
        )

    def test_get_admin_roles_when_passing_bad_role_id(self):
        role_id = "some_role_id"
        self.data_store.roles = {
            role_id: {
                'name': 'Some event type',
                'descr': 'client',
                'acls': {
                    'admin.portal': {'read': '1'}
                }
            }
        }
        self.data_store.user_mapping = {
            "some_user_id": {"role_id": "some_role_id"}
        }

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "uber.acl_admin_role_get",
                    "role_id": "bogus_id_that_won't_match"
                }
            )

        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "error_code": 1,
                "error_message": "No User Roles found",
                "status": False,
                "data": ""
            }
        )

    def test_get_admin_roles_successfully_when_passing_valid_role_id(self):
        role_id = "some_role_id"
        self.data_store.roles = {
            role_id: {
                'name': 'A Admin Role',
                'descr': 'A Admin Role',
                'acls': {
                    'admin.portal': {'read': '1'}
                }
            }
        }

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "uber.acl_admin_role_get",
                    "role_id": role_id
                }
            )

        self.assertEqual(
            json.loads(resp.data.decode('utf-8')).get('data'),
            {
                'name': 'A Admin Role',
                'descr': 'A Admin Role',
                'acls': {
                    'admin.portal': {'read': '1'}
                }
            }
        )

    def test_get_admin_roles_fails_when_no_role_id_passed(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "uber.acl_admin_role_get",
                    "userid": "some_user_id"
                }
            )

        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "error_code": 1,
                "error_message": "role_id parameter not specified",
                "status": False,
                "data": ""
            }
        )

    def test_get_admin_roles_fails_when_no_role_could_be_found_for_user(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "uber.acl_admin_role_get",
                    "userid": "some_user_id",
                    "role_id": "some_role_id"
                }
            )

        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "error_code": 1,
                "error_message": "No User Roles found",
                "status": False,
                "data": ""
            }
        )

    def test_get_admin_roles_fails_when_user_not_found(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "uber.acl_admin_role_get",
                    "userid": "some_user_id",
                    "role_id": "some_role_id"
                }
            )

        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "error_code": 1,
                "error_message": "No User Roles found",
                "status": False,
                "data": ""
            }
        )

    def test_acl_resource_add(self):
        self.maxDiff = None
        with self.app.test_client() as c:
            self._assert_success(c.post('api/2.0/', data={"method": "uber.acl_resource_add",
                                                          "parent_resource_name": "",
                                                          "resource_name": "my.resource",
                                                          "label": "my label",
                                                          "actions": "create,read,update,delete"}),
                                 content="")

            self._assert_success(c.post('api/2.0/', data={"method": "uber.acl_resource_add",
                                                          "parent_resource_name": "my.resource",
                                                          "resource_name": "my.child1",
                                                          "label": "my label 2",
                                                          "actions": "read"}),
                                 content="")

            self._assert_success(c.post('api/2.0/', data={"method": "uber.acl_resource_add",
                                                          "parent_resource_name": "my.child1",
                                                          "resource_name": "my.child2",
                                                          "label": "my label 3"}),
                                 content="")

            self._assert_success(
                c.post('api/2.0/', data={"method": "uber.acl_resource_list"}),
                content={
                    "1": {
                        "resource_id": "1",
                        "name": "my.resource",
                        "parent_id": "0",
                        "lft": "0",
                        "rgt": "0",
                        "active": "1",
                        "label": "my label",
                        "actions": {
                            "1": "Create",
                            "2": "View",
                            "3": "Update",
                            "4": "Delete"
                        },
                        "children": {
                            "2": {
                                "resource_id": "2",
                                "name": "my.child1",
                                "parent_id": "1",
                                "lft": "0",
                                "rgt": "0",
                                "active": "1",
                                "label": "my label 2",
                                "actions": {
                                    "2": "View",
                                },
                                "children": {
                                    "3": {
                                        "resource_id": "3",
                                        "name": "my.child2",
                                        "parent_id": "2",
                                        "lft": "0",
                                        "rgt": "0",
                                        "active": "1",
                                        "label": "my label 3",
                                        "actions": {
                                            "1": "Create",
                                            "2": "View",
                                            "3": "Update",
                                            "4": "Delete"
                                        },
                                        "children": []
                                    }
                                }
                            }
                        }
                    }
                })

    def test_acl_resource_add_error(self):
        with self.app.test_client() as c:
            self._assert_error(c.post('api/2.0/', data={"method": "uber.acl_resource_add",
                                                        "parent_resource_name": "baaaaaaah",
                                                        "resource_name": "my.resource"}),
                               code=1,
                               message="Resource [baaaaaaah] not found",
                               content="")
