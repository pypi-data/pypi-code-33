# Copyright 2019 Intel, Inc.
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

import json
import mock
import testtools

from sushy import exceptions

from rsd_lib.resources.v2_1.event_service import event_service
from rsd_lib.resources.v2_1.event_service import event_subscription


class EventServiceTestCase(testtools.TestCase):
    def setUp(self):
        super(EventServiceTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/event_service.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.event_service_inst = event_service.EventService(
            self.conn, '/redfish/v1/EventService',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.event_service_inst._parse_attributes()
        self.assertEqual('EventService', self.event_service_inst.identity)
        self.assertEqual('Event Service', self.event_service_inst.name)
        self.assertEqual('Event Service', self.event_service_inst.description)
        self.assertEqual('Enabled', self.event_service_inst.status.state)
        self.assertEqual('OK', self.event_service_inst.status.health)
        self.assertEqual(None, self.event_service_inst.status.health_rollup)
        self.assertEqual(True, self.event_service_inst.service_enabled)
        self.assertEqual(3, self.event_service_inst.delivery_retry_attempts)
        self.assertEqual(
            60, self.event_service_inst.delivery_retry_interval_seconds)
        self.assertEqual(
            ["StatusChange", "ResourceUpdated", "ResourceAdded",
             "ResourceRemoved", "Alert"],
            self.event_service_inst.event_types_for_subscription)

    def test__get_subscriptions_collection_path(self):
        expected = '/redfish/v1/EventService/Subscriptions'
        result = self.event_service_inst._get_subscriptions_collection_path()
        self.assertEqual(expected, result)

    def test__get_subscriptions_collection_path_missing_attr(self):
        self.event_service_inst._json.pop('Subscriptions')
        with self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Subscriptions'):
            self.event_service_inst._get_subscriptions_collection_path()

    def test_subscriptions(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'event_subscription_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_subscriptions = self.event_service_inst.subscriptions
        # | THEN |
        self.assertIsInstance(actual_subscriptions,
                              event_subscription.EventSubscriptionCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_subscriptions,
                      self.event_service_inst.subscriptions)
        self.conn.get.return_value.json.assert_not_called()

    def test_event_subscriptions_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'event_subscription_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.event_service_inst.subscriptions,
                              event_subscription.EventSubscriptionCollection)

        # On refreshing the event_service instance...
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'event_service.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.event_service_inst.invalidate()
        self.event_service_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'event_subscription_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.event_service_inst.subscriptions,
                              event_subscription.EventSubscriptionCollection)
