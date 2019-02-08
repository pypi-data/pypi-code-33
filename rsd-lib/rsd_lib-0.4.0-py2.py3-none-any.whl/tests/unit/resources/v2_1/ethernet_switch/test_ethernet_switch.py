# Copyright 2017 Intel, Inc.
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
from sushy import exceptions
import testtools

from rsd_lib.resources.v2_1.ethernet_switch import acl
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch
from rsd_lib.resources.v2_1.ethernet_switch import port


class EthernetSwtichTestCase(testtools.TestCase):

    def setUp(self):
        super(EthernetSwtichTestCase, self).setUp()
        self.conn = mock.Mock()

        with open('rsd_lib/tests/unit/json_samples/v2_1/ethernet_switch.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.ethernet_switch_inst = ethernet_switch.EthernetSwitch(
            self.conn,
            '/redfish/v1/EthernetSwitches/Switch1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.ethernet_switch_inst._parse_attributes()
        self.assertEqual('1.0.2', self.ethernet_switch_inst.redfish_version)
        self.assertEqual('Switch1', self.ethernet_switch_inst.identity)
        self.assertEqual('Switch1', self.ethernet_switch_inst.name)
        self.assertEqual('description-as-string',
                         self.ethernet_switch_inst.description)
        self.assertEqual('Quanta', self.ethernet_switch_inst.manufacturer)
        self.assertEqual('ly8_rangley', self.ethernet_switch_inst.model)
        self.assertEqual('02/21/2015 00:00:00',
                         self.ethernet_switch_inst.manufacturing_date)
        self.assertEqual('2M220100SL', self.ethernet_switch_inst.seria_number)
        self.assertEqual('1LY8UZZ0007', self.ethernet_switch_inst.part_number)
        self.assertEqual('ONIE', self.ethernet_switch_inst.firmware_name)
        self.assertEqual('1.1', self.ethernet_switch_inst.firmware_version)
        self.assertEqual('TOR', self.ethernet_switch_inst.role)
        self.assertEqual('Enabled', self.ethernet_switch_inst.status.state)
        self.assertEqual('OK', self.ethernet_switch_inst.status.health)
        self.assertEqual('/redfish/v1/Chassis/FabricModule1',
                         self.ethernet_switch_inst.links.chassis)
        self.assertEqual(('/redfish/v1/Managers/Manager1',),
                         self.ethernet_switch_inst.links.managed_by)

    def test__get_port_collection_path(self):
        expected = '/redfish/v1/EthernetSwitches/Switch1/Ports'
        result = self.ethernet_switch_inst._get_port_collection_path()
        self.assertEqual(expected, result)

    def test__get_port_collection_path_missing_attr(self):
        self.ethernet_switch_inst._json.pop('Ports')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Ports',
            self.ethernet_switch_inst._get_port_collection_path)

    def test_ports(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
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
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_port_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.ethernet_switch_inst.ports,
                              port.PortCollection)

        # On refreshing the port instance...
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.ethernet_switch_inst.invalidate()
        self.ethernet_switch_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_port_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.ethernet_switch_inst.ports,
                              port.PortCollection)

    def test__get_acl_collection_path(self):
        self.assertEqual('/redfish/v1/EthernetSwitches/Switch1/ACLs',
                         self.ethernet_switch_inst._get_acl_collection_path())

    def test__get_acl_collection_path_missing_attr(self):
        self.ethernet_switch_inst._json.pop('ACLs')
        with self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute ACLs'):
            self.ethernet_switch_inst._get_acl_collection_path()

    def test_acl(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_acl_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_acls_col = self.ethernet_switch_inst.acls
        # | THEN |
        self.assertIsInstance(actual_acls_col,
                              acl.ACLCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        self.assertIs(actual_acls_col,
                      self.ethernet_switch_inst.acls)
        self.conn.get.return_value.json.assert_not_called()

    def test_acls_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_acl_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.ethernet_switch_inst.acls,
                              acl.ACLCollection)

        # On refreshing...
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.ethernet_switch_inst.invalidate()
        self.ethernet_switch_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_acl_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.ethernet_switch_inst.acls,
                              acl.ACLCollection)


class EthernetSwitchCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(EthernetSwitchCollectionTestCase, self).setUp()
        self.conn = mock.Mock()

        with open('rsd_lib/tests/unit/json_samples/v2_1/'
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
