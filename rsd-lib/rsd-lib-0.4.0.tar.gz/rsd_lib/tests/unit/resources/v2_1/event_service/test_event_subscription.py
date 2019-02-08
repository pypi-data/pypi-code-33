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
import jsonschema
import mock
import testtools

from rsd_lib.resources.v2_1.event_service import event_subscription
from rsd_lib.tests.unit.fakes import request_fakes


class EventSubscriptionTestCase(testtools.TestCase):
    def setUp(self):
        super(EventSubscriptionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
                'rsd_lib/tests/unit/json_samples/v2_1/event_subscription.json',
                'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.event_subscription_inst = event_subscription.EventSubscription(
            self.conn, '/redfish/v1/EventService/Subscriptions/1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.event_subscription_inst._parse_attributes()
        self.assertEqual('1', self.event_subscription_inst.identity)
        self.assertEqual('EventSubscription 1',
                         self.event_subscription_inst.name)
        self.assertEqual('EventSubscription',
                         self.event_subscription_inst.description)
        self.assertEqual('http://192.168.1.1/Destination1',
                         self.event_subscription_inst.destination)
        self.assertEqual(['ResourceAdded', 'ResourceRemoved'],
                         self.event_subscription_inst.event_types)
        self.assertEqual("My Event", self.event_subscription_inst.context)
        self.assertEqual("Redfish", self.event_subscription_inst.protocol)

    def test_delete(self):
        self.event_subscription_inst.delete()
        self.event_subscription_inst._conn.delete.assert_called_once()


class EventSubscriptionCollectionTestCase(testtools.TestCase):
    def setUp(self):
        super(EventSubscriptionCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
                'rsd_lib/tests/unit/json_samples/v2_1/'
                'event_subscription_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.conn.post.return_value = request_fakes.fake_request_post(
            None, headers={"Location": "https://localhost:8443/redfish/v1/"
                                       "EventService/Subscriptions/2"})

        self.event_subscription_col = event_subscription. \
            EventSubscriptionCollection(self.conn,
                                        '/redfish/v1/EventService/'
                                        'Subscriptions',
                                        redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.event_subscription_col._parse_attributes()
        self.assertEqual('1.0.2', self.event_subscription_col.redfish_version)
        self.assertEqual('Event Subscriptions Collection',
                         self.event_subscription_col.name)
        self.assertEqual(('/redfish/v1/EventService/Subscriptions/1',),
                         self.event_subscription_col.members_identities)

    @mock.patch.object(event_subscription, 'EventSubscription', autospec=True)
    def test_get_member(self, mock_event_subscription):
        self.event_subscription_col.get_member(
            '/redfish/v1/EventService/Subscriptions/1')
        mock_event_subscription.assert_called_once_with(
            self.event_subscription_col._conn,
            '/redfish/v1/EventService/Subscriptions/1',
            redfish_version=self.event_subscription_col.redfish_version)

    @mock.patch.object(event_subscription, 'EventSubscription', autospec=True)
    def test_get_members(self, mock_event_subscription):
        members = self.event_subscription_col.get_members()
        mock_event_subscription.assert_called_once_with(
            self.event_subscription_col._conn,
            '/redfish/v1/EventService/Subscriptions/1',
            redfish_version=self.event_subscription_col.redfish_version)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))

    def test_create_subscription_reqs(self):
        reqs = {
            'Name': 'EventSubscription 1',
            'Destination': 'EventSubscription',
            'EventTypes': [
                'ResourceAdded',
                'ResourceRemoved'
            ],
            'Context': 'My Event',
            'Protocol': 'Redfish',
            'OriginResources': [{
                '@odata.id': '/redfish/v1/Systems/1'
            }]
        }

        result = self.event_subscription_col.create_event_subscription(reqs)
        self.event_subscription_col._conn.post.assert_called_once_with(
            '/redfish/v1/EventService/Subscriptions',
            data=reqs)
        self.assertEqual(result,
                         '/redfish/v1/EventService/Subscriptions/2')

    def test_create_subscription_invalid_reqs(self):
        reqs = {
            'Name': 'EventSubscription 1',
            'Destination': 'EventSubscription',
            'EventTypes': [
                'ResourceAdded',
                'ResourceRemoved'
            ],
            'Context': 'My Event',
            'Protocol': 'Redfish',
            'OriginResources': [{
                '@odata.id': '/redfish/v1/Systems/1'
            }]
        }

        # Wrong format
        event_subscription_req = reqs.copy()
        event_subscription_req.update({'Context': True})
        self.assertRaises(
            jsonschema.exceptions.ValidationError,
            self.event_subscription_col.create_event_subscription,
            event_subscription_req)

        # Wrong additional fields
        event_subscription_req = reqs.copy()
        event_subscription_req['Additional'] = 'AdditionalField'
        self.assertRaises(
            jsonschema.exceptions.ValidationError,
            self.event_subscription_col.create_event_subscription,
            event_subscription_req)
