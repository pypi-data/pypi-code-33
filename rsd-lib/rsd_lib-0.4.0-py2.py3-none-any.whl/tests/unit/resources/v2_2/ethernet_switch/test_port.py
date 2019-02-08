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
import testtools

from sushy import exceptions

from rsd_lib.resources.v2_2.ethernet_switch import port
from rsd_lib.resources.v2_2.ethernet_switch import port_metrics


class PortTestCase(testtools.TestCase):

    def setUp(self):
        super(PortTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_port.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.port_inst = port.Port(
            self.conn, '/redfish/v1/EthernetSwitches/Switch1/Ports/Port1',
            redfish_version='1.0.2')

    def test__get_metrics_path(self):
        self.assertEqual(
            '/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/Metrics',
            self.port_inst._get_metrics_path())

    def test__get_metrics_path_missing_ports_attr(self):
        self.port_inst._json.pop('Metrics')
        with self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Metrics'):
            self.port_inst._get_metrics_path()

    def test_metrics(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_port_metrics.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_metrics = self.port_inst.metrics
        # | THEN |
        self.assertIsInstance(actual_metrics,
                              port_metrics.PortMetrics)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_metrics,
                      self.port_inst.metrics)
        self.conn.get.return_value.json.assert_not_called()

    def test_metrics_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_port_metrics.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.port_inst.metrics,
                              port_metrics.PortMetrics)

        # On refreshing the port instance...
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_port.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.port_inst.invalidate()
        self.port_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_port_metrics.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.port_inst.metrics,
                              port_metrics.PortMetrics)


class PortCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(PortCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            'rsd_lib/tests/unit/json_samples/v2_2/'
                'ethernet_switch_port_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
            self.port_col = port.PortCollection(
                self.conn, '/redfish/v1/EthernetSwitches/Switch1/Ports',
                redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.port_col._parse_attributes()
        self.assertEqual('1.0.2', self.port_col.redfish_version)
        self.assertEqual(
            'Ethernet Switch Port Collection',
            self.port_col.name)
        self.assertEqual(
            ('/redfish/v1/EthernetSwitches/Switch1/Ports/Port1',),
            self.port_col.members_identities)

    @mock.patch.object(port, 'Port', autospec=True)
    def test_get_member(self, mock_port):
        self.port_col.get_member(
            '/redfish/v1/EthernetSwitches/Switch1/Ports/Port1')
        mock_port.assert_called_once_with(
            self.port_col._conn,
            '/redfish/v1/EthernetSwitches/Switch1/Ports/Port1',
            redfish_version=self.port_col.redfish_version)

    @mock.patch.object(port, 'Port', autospec=True)
    def test_get_members(self, mock_port):
        members = self.port_col.get_members()
        mock_port.assert_called_with(
            self.port_col._conn,
            '/redfish/v1/EthernetSwitches/Switch1/Ports/Port1',
            redfish_version=self.port_col.redfish_version)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
