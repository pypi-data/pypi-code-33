# Copyright 2018 99cloud, Inc.
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

from rsd_lib.resources.v2_1.ethernet_switch import static_mac


class StaticMACTestCase(testtools.TestCase):

    def setUp(self):
        super(StaticMACTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_port_static_mac.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.static_mac_inst = static_mac.StaticMAC(
            self.conn,
            '/redfish/v1/EthernetSwitches/Switch1/Ports/StaticMACs/1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.static_mac_inst._parse_attributes()
        self.assertEqual('1.0.2', self.static_mac_inst.redfish_version)
        self.assertEqual('1', self.static_mac_inst.identity)
        self.assertEqual('StaticMAC', self.static_mac_inst.name)
        self.assertEqual('description-as-string',
                         self.static_mac_inst.description)
        self.assertEqual('00:11:22:33:44:55', self.static_mac_inst.mac_address)
        self.assertEqual(112, self.static_mac_inst.vlan_id)
        self.assertEqual({}, self.static_mac_inst.oem)


class StaticMACCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(StaticMACCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_port_static_mac_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
            self.static_mac_col = static_mac.StaticMACCollection(
                self.conn,
                '/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/StaticMACs',
                redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.static_mac_col._parse_attributes()
        self.assertEqual('1.1.0', self.static_mac_col.redfish_version)
        self.assertEqual(
            ('/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/StaticMACs/1',),
            self.static_mac_col.members_identities)

    @mock.patch.object(static_mac, 'StaticMAC', autospec=True)
    def test_get_member(self, mock_static_mac):
        self.static_mac_col.get_member(
            '/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/StaticMACs/1')
        mock_static_mac.assert_called_once_with(
            self.static_mac_col._conn,
            '/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/StaticMACs/1',
            redfish_version=self.static_mac_col.redfish_version)

    @mock.patch.object(static_mac, 'StaticMAC', autopspec=True)
    def test_get_members(self, mock_static_mac):
        members = self.static_mac_col.get_members()
        calls = [
            mock.call(self.static_mac_col._conn,
                      '/redfish/v1/EthernetSwitches/Switch1/Ports/Port1/'
                      'StaticMACs/1',
                      redfish_version=self.static_mac_col.redfish_version)
        ]
        mock_static_mac.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
