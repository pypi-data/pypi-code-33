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

from rsd_lib.resources.v2_2.ethernet_switch import port_metrics


class PortMetricsTestCase(testtools.TestCase):

    def setUp(self):
        super(PortMetricsTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'ethernet_switch_port_metrics.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.port_metrics_inst = port_metrics.PortMetrics(
            self.conn,
            '/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/Metrics',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.port_metrics_inst._parse_attributes()
        self.assertEqual('1.1.0', self.port_metrics_inst.redfish_version)
        self.assertEqual('Ethernet Switch Port Metrics',
                         self.port_metrics_inst.name)
        self.assertEqual('Metrics',
                         self.port_metrics_inst.identity)

        self.assertEqual(8, self.port_metrics_inst.received.packets)
        self.assertEqual(5, self.port_metrics_inst.received.dropped_packets)
        self.assertEqual(4, self.port_metrics_inst.received.error_packets)
        self.assertEqual(3, self.port_metrics_inst.received.broadcast_packets)
        self.assertEqual(2, self.port_metrics_inst.received.multicast_packets)
        self.assertEqual(0, self.port_metrics_inst.received.errors)
        self.assertEqual(64, self.port_metrics_inst.received.received_bytes)

        self.assertEqual(128, self.port_metrics_inst.transmitted.packets)
        self.assertEqual(
            1, self.port_metrics_inst.transmitted.dropped_packets)
        self.assertEqual(2, self.port_metrics_inst.transmitted.error_packets)
        self.assertEqual(
            3, self.port_metrics_inst.transmitted.broadcast_packets)
        self.assertEqual(
            4, self.port_metrics_inst.transmitted.multicast_packets)
        self.assertEqual(5, self.port_metrics_inst.transmitted.errors)
        self.assertEqual(
            512, self.port_metrics_inst.transmitted.transmitted_bytes)

        self.assertEqual(0, self.port_metrics_inst.collisions)
