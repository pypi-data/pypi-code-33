# Copyright 2018 Intel, Inc.
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

from rsd_lib.resources.v2_2.ethernet_switch import ethernet_switch
from rsd_lib.resources.v2_2.ethernet_switch import metrics
from rsd_lib.resources.v2_2.ethernet_switch import port

import testtools


class EthernetSwitchTestCase(testtools.TestCase):

    def setUp(self):
        super(EthernetSwitchTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.ethernet_switch_inst = ethernet_switch.EthernetSwitch(
            self.conn, '/redfish/v1/EthernetSwitches/Switch1/Ports/Port1',
            redfish_version='1.0.2')

    def test_ports(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_port_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_ports = self.ethernet_switch_inst.ports
        # | THEN |
        self.assertIsInstance(actual_ports,
                              port.PortCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_ports,
                      self.ethernet_switch_inst.ports)
        self.conn.get.return_value.json.assert_not_called()

    def test_ports_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_port_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.ethernet_switch_inst.ports,
                              port.PortCollection)

        # On refreshing the port instance...
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.ethernet_switch_inst.invalidate()
        self.ethernet_switch_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_port_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.ethernet_switch_inst.ports,
                              port.PortCollection)

    def test_metrics(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_metrics.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_metrics = self.ethernet_switch_inst.metrics
        # | THEN |
        self.assertIsInstance(actual_metrics,
                              metrics.Metrics)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_metrics,
                      self.ethernet_switch_inst.metrics)
        self.conn.get.return_value.json.assert_not_called()

    def test_metrics_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_metrics.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.ethernet_switch_inst.metrics,
                              metrics.Metrics)

        # On refreshing the metrics instance...
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.ethernet_switch_inst.invalidate()
        self.ethernet_switch_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_metrics.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.ethernet_switch_inst.metrics,
                              metrics.Metrics)


class EthernetSwitchCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(EthernetSwitchCollectionTestCase, self).setUp()
        self.conn = mock.Mock()

        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.ethernet_switch_col = ethernet_switch.EthernetSwitchCollection(
            self.conn,
            'redfish/v1/EthernetSwitches',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.ethernet_switch_col._parse_attributes()
        self.assertEqual('1.0.2', self.ethernet_switch_col.redfish_version)
        self.assertEqual('Ethernet Switches Collection',
                         self.ethernet_switch_col.name)
        self.assertEqual(('/redfish/v1/EthernetSwitches/Switch1',),
                         self.ethernet_switch_col.members_identities)

    @mock.patch.object(ethernet_switch, 'EthernetSwitch', autospec=True)
    def test_get_member(self, mock_ethernet_switch):
        self.ethernet_switch_col.get_member(
            '/redfish/v1/EthernetSwitches/Switch1')

        mock_ethernet_switch.assert_called_once_with(
            self.ethernet_switch_col._conn,
            '/redfish/v1/EthernetSwitches/Switch1',
            redfish_version=self.ethernet_switch_col.redfish_version
        )

    @mock.patch.object(ethernet_switch, 'EthernetSwitch', autospec=True)
    def test_get_members(self, mock_ethernet_switch):
        members = self.ethernet_switch_col.get_members()
        self.assertEqual(mock_ethernet_switch.call_count, 1)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
