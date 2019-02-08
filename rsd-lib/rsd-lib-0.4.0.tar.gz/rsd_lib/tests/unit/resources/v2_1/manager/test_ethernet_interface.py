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

from rsd_lib.resources.v2_1.ethernet_switch import vlan
from rsd_lib.resources.v2_1.system import ethernet_interface


class EthernetInterface(testtools.TestCase):
    def setUp(self):
        super(EthernetInterface, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'manager_ethernet_interface.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.ethernet_interface_inst = ethernet_interface.EthernetInterface(
            self.conn,
            '/redfish/v1/Managers/1/EthernetInterfaces/1',
            redfish_version='1.0.2')

    def test_parse_attributes(self):
        self.ethernet_interface_inst._parse_attributes()
        self.assertEqual("LAN1", self.ethernet_interface_inst.identity)
        self.assertEqual("Ethernet Interface",
                         self.ethernet_interface_inst.name)
        self.assertEqual("System NIC 1",
                         self.ethernet_interface_inst.description)
        self.assertEqual("Enabled",
                         self.ethernet_interface_inst.status.state)
        self.assertEqual("OK", self.ethernet_interface_inst.status.health)
        self.assertEqual(None,
                         self.ethernet_interface_inst.status.health_rollup)
        self.assertEqual(True,
                         self.ethernet_interface_inst.interface_enabled)
        self.assertEqual(
            "AA:BB:CC:DD:EE:FF",
            self.ethernet_interface_inst.permanent_mac_address)
        self.assertEqual(
            "AA:BB:CC:DD:EE:FF",
            self.ethernet_interface_inst.mac_address)
        self.assertEqual(100, self.ethernet_interface_inst.speed_mbps)
        self.assertEqual(True, self.ethernet_interface_inst.auto_neg)
        self.assertEqual(True, self.ethernet_interface_inst.full_duplex)
        self.assertEqual(1500, self.ethernet_interface_inst.mtu_size)
        self.assertEqual("web483", self.ethernet_interface_inst.host_name)
        self.assertEqual("web483.redfishspecification.org",
                         self.ethernet_interface_inst.fqdn)
        self.assertEqual("fe80::3ed9:2bff:fe34:600",
                         self.ethernet_interface_inst.ipv6_default_gateway)
        self.assertEqual(
            None, self.ethernet_interface_inst.max_ipv6_static_addresses)
        self.assertEqual((['names.redfishspecification.org']),
                         self.ethernet_interface_inst.name_servers)
        self.assertEqual(
            "192.168.0.10",
            self.ethernet_interface_inst.ipv4_addresses[0].address)
        self.assertEqual(
            "255.255.252.0",
            self.ethernet_interface_inst.ipv4_addresses[0].subnet_mask)
        self.assertEqual(
            "Static",
            self.ethernet_interface_inst.ipv4_addresses[0].address_origin)
        self.assertEqual(
            "192.168.0.1",
            self.ethernet_interface_inst.ipv4_addresses[0].gateway)
        self.assertEqual(
            "fe80::1ec1:deff:fe6f:1e24",
            self.ethernet_interface_inst.ipv6_addresses[0].address)
        self.assertEqual(
            64, self.ethernet_interface_inst.ipv6_addresses[0].prefix_length)
        self.assertEqual(
            "Static",
            self.ethernet_interface_inst.ipv6_addresses[0].address_origin)
        self.assertEqual(
            "Preferred",
            self.ethernet_interface_inst.ipv6_addresses[0].address_state)
        self.assertEqual(None, self.ethernet_interface_inst.vlan)
        self.assertEqual(
            [], self.ethernet_interface_inst.ipv6_static_addresses)
        self.assertEqual(
            None, self.ethernet_interface_inst.ipv6_address_policy_table)
        self.assertEqual(
            "/redfish/v1/EthernetSwitches/1/Ports/1",
            self.ethernet_interface_inst.links.oem.intel_rackScale.
            neighbor_port)

    def test__get_vlan_collection_path(self):
        actual_path = self.ethernet_interface_inst._get_vlan_collection_path()
        self.assertEqual('/redfish/v1/Managers/1/EthernetInterfaces/1/VLANs',
                         actual_path)

    def test__get_vlan_collection_path_without_vlans(self):
        self.ethernet_interface_inst._json.pop('VLANs')
        with self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute VLANs'):
            self.ethernet_interface_inst._get_vlan_collection_path()

    def test_vlans(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_port_vlan_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_vlans = self.ethernet_interface_inst.vlans
        # | THEN |
        self.assertIsInstance(actual_vlans,
                              vlan.VLANCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        self.assertIs(actual_vlans, self.ethernet_interface_inst.vlans)
        self.conn.get.return_value.json.assert_not_called()

    def test_vlans_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_port_vlan_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        actual_vlans = self.ethernet_interface_inst.vlans

        self.assertIsInstance(actual_vlans,
                              vlan.VLANCollection)

        # On refreshing...
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'manager_ethernet_interface.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(
                f.read())

        self.ethernet_interface_inst.invalidate()
        self.ethernet_interface_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_port_vlan_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(
                f.read())
        # | WHEN & THEN |
        self.assertIsInstance(actual_vlans,
                              vlan.VLANCollection)


class EthernetInterfaceCollectionTestCase(testtools.TestCase):
    def setUp(self):
        super(EthernetInterfaceCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'manager_ethernet_interface_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
            self.ethernet_interface_col = ethernet_interface. \
                EthernetInterfaceCollection(
                    self.conn, '/redfish/v1/Managers/1/EthernetInterfaces',
                    redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.ethernet_interface_col._parse_attributes()
        self.assertEqual('1.0.2', self.ethernet_interface_col.redfish_version)
        self.assertEqual(('/redfish/v1/Managers/1/EthernetInterfaces/1',),
                         self.ethernet_interface_col.members_identities)

    @mock.patch.object(ethernet_interface, 'EthernetInterface', autospec=True)
    def test_get_member(self, mock_ethernet_interface):
        self.ethernet_interface_col.get_member(
            '/redfish/v1/Managers/1/EthernetInterfaces/1')
        mock_ethernet_interface.assert_called_once_with(
            self.ethernet_interface_col._conn,
            '/redfish/v1/Managers/1/EthernetInterfaces/1',
            redfish_version=self.ethernet_interface_col.redfish_version
        )

    @mock.patch.object(ethernet_interface, 'EthernetInterface', autospec=True)
    def test_get_members(self, mock_ethernet_interface):
        members = self.ethernet_interface_col.get_members()
        calls = [
            mock.call(
                self.ethernet_interface_col._conn,
                '/redfish/v1/Managers/1/EthernetInterfaces/1',
                redfish_version=self.ethernet_interface_col.redfish_version)
        ]
        mock_ethernet_interface.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
