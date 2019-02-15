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
from fake_ubersmith.api.methods.order import Order
from fake_ubersmith.api.ubersmith import FakeUbersmithError, UbersmithBase


class TestOrderModule(unittest.TestCase):
    def setUp(self):
        self.data_store = DataStore()
        self.order = Order(self.data_store)
        self.app = Flask(__name__)
        self.base_uber_api = UbersmithBase(self.data_store)

        self.order.hook_to(self.base_uber_api)
        self.base_uber_api.hook_to(self.app)

    def test_coupon_get_returns_successfully(self):
        self.data_store.coupons = [
            {"coupon": {"coupon_code": "1"}},
            {"coupon": {"coupon_code": "2"}}
        ]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "order.coupon_get", "coupon_code": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"coupon": {"coupon_code": "1"}},
                "error_message": "",
                "status": True,
                "error_code": None,

            }
        )

    def test_coupon_get_returns_error(self):
        self.data_store.coupons = [
            {"coupon": {"coupon_code": "100"}},
            {"coupon": {"coupon_code": "200"}}
        ]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "order.coupon_get", "coupon_code": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "status": False,
                "error_message": "could not get coupon info",
                "error_code": 1
            }
        )

    def test_create_order_succeeds(self):
        self.data_store.order = {
            "1": {"order_id": "100", "order_queue_id": "1"}
        }

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "order.create", "order_queue_id": "1"}
            )
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"order_id": "100", "order_queue_id": "1"},
                "status": True,
                "error_message": "",
                "error_code": None
            }
        )

    def test_create_order_errs(self):
        self.data_store.order = {
            "1": FakeUbersmithError(code=999, message='epic fail')
        }

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "order.create", "order_queue_id": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 999,
                "error_message": "epic fail",
                "status": False
            }
        )

    def test_order_respond_responds(self):
        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "order.respond"}
            )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": 8,
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_submit_order_is_successful(self):
        self.data_store.order_submit = {"100": {"order_id": "100"}}

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "order.submit", "order_id": "100"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"order_id": "100"},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_submit_order_errs(self):
        self.data_store.order_submit = {
            "100": FakeUbersmithError(code=999, message='epic fail')
        }

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "order.submit", "order_id": "100"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 999,
                "error_message": "epic fail",
                "status": False
            }
        )

    def test_cancel_order_is_successful(self):
        self.data_store.order_cancel = {"100": {"order_id": "100"}}

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "order.cancel", "order_id": "100"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"order_id": "100"},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_cancel_order_errs(self):
        self.data_store.order_cancel = {
            "100": FakeUbersmithError(code=999, message='epic fail')
        }

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "order.cancel", "order_id": "100"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 999,
                "error_message": "epic fail",
                "status": False
            }
        )
