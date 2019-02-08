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

from sushy.tests.unit import base

from rsd_lib.resources.v2_1.manager import manager
from rsd_lib.resources.v2_1.manager import network_protocol
from rsd_lib.resources.v2_1.system import ethernet_interface


class TestManager(base.TestCase):

    def setUp(self):
        super(TestManager, self).setUp()
        self.conn = mock.Mock()

        with open('rsd_lib/tests/unit/json_samples/v2_1/manager.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.manager_inst = manager.Manager(self.conn,
                                            '/redfish/v1/Manager/PSME',
                                            redfish_version='1.0.2')

    def test_parse_attributes(self):
        self.manager_inst._parse_attributes()
        self.assertEqual('1.0.2', self.manager_inst.redfish_version)
        self.assertEqual('1', self.manager_inst.identity)
        self.assertEqual('Manager', self.manager_inst.name)
        self.assertEqual('BMC', self.manager_inst.description)
        self.assertEqual('92384634-2938-2342-8820-489239905423',
                         self.manager_inst.service_entry_point_uuid)
        self.assertEqual('00000000-0000-0000-0000-000000000000',
                         self.manager_inst.uuid)
        self.assertEqual('Joo Janta 200', self.manager_inst.model)
        self.assertEqual('Enabled', self.manager_inst.status.state)
        self.assertEqual('OK', self.manager_inst.status.health)
        self.assertEqual('OK', self.manager_inst.status.health_rollup)
        self.assertEqual(True,
                         self.manager_inst.graphical_console.service_enabled)
        self.assertEqual(
            2,
            self.manager_inst.graphical_console.max_concurrent_sessions)
        self.assertEqual(
            ['KVMIP'],
            self.manager_inst.graphical_console.connect_types_supported)
        self.assertEqual(
            True,
            self.manager_inst.serial_console.service_enabled)
        self.assertEqual(
            1,
            self.manager_inst.serial_console.max_concurrent_sessions)
        self.assertEqual(
            ['Telnet', 'SSH', 'IPMI'],
            self.manager_inst.serial_console.connect_types_supported)
        self.assertEqual(
            True,
            self.manager_inst.command_shell.service_enabled)
        self.assertEqual(
            4,
            self.manager_inst.command_shell.max_concurrent_sessions)
        self.assertEqual(
            ['Telnet', 'SSH'],
            self.manager_inst.command_shell.connect_types_supported)
        self.assertEqual('1.00', self.manager_inst.firmware_version)
        self.assertEqual((), self.manager_inst.links.manager_for_servers)
        self.assertEqual(
            ('/redfish/v1/Chassis/FabricModule1',),
            self.manager_inst.links.manager_for_chassis)
        self.assertEqual('On', self.manager_inst.power_state)

    def test__get_network_protocol_path(self):
        expected = '/redfish/v1/Managers/PSME/NetworkProtocol'
        result = self.manager_inst._get_network_protocol_path()
        self.assertEqual(expected, result)

    def test_network_protocol(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'network_protocol.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_network_protocol = self.manager_inst.network_protocol
        # | THEN |
        self.assertIsInstance(actual_network_protocol,
                              network_protocol.NetworkProtocol)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_network_protocol,
                      self.manager_inst.network_protocol)
        self.conn.get.return_value.json.assert_not_called()

    def test_network_protocol_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'network_protocol.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.manager_inst.network_protocol,
                              network_protocol.NetworkProtocol)

        # On refreshing the manager instance...
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'manager.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.manager_inst.invalidate()
        self.manager_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'network_protocol.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.manager_inst.network_protocol,
                              network_protocol.NetworkProtocol)

    def test__get_ethernet_interfaces_path(self):
        expected = '/redfish/v1/Managers/PSME/EthernetInterfaces'
        result = self.manager_inst._get_ethernet_interfaces_path()
        self.assertEqual(expected, result)

    def test_ethernet_interfaces(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'manager_ethernet_interface.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_ethernet_interfaces = self.manager_inst.ethernet_interfaces
        # | THEN |
        self.assertIsInstance(actual_ethernet_interfaces,
                              ethernet_interface.EthernetInterfaceCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_ethernet_interfaces,
                      self.manager_inst.ethernet_interfaces)
        self.conn.get.return_value.json.assert_not_called()

    def test_ethernet_interfaces_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'manager_ethernet_interface_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.manager_inst.ethernet_interfaces,
                              ethernet_interface.EthernetInterfaceCollection)

        # On refreshing the manager instance...
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'manager.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.manager_inst.invalidate()
        self.manager_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'manager_ethernet_interface_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.manager_inst.ethernet_interfaces,
                              ethernet_interface.EthernetInterfaceCollection)


class TestManagerCollection(base.TestCase):

    def setUp(self):
        super(TestManagerCollection, self).setUp()
        self.conn = mock.Mock()

        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'manager_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.manager_col = manager.ManagerCollection(self.conn,
                                                     'redfish/v1/Managers',
                                                     redfish_version='1.0.2')

    def test_parse_attributes(self):
        self.manager_col._parse_attributes()
        self.assertEqual('1.0.2', self.manager_col.redfish_version)
        self.assertEqual('Manager Collection', self.manager_col.name)
        self.assertEqual(('/redfish/v1/Managers/RMC',
                          '/redfish/v1/Managers/MBPC1',
                          '/redfish/v1/Managers/MBPC2',),
                         self.manager_col.members_identities)

    @mock.patch.object(manager, 'Manager', autospec=True)
    def test_get_member(self, mock_manager):
        self.manager_col.get_member('/redfish/v1/Managers/RMC')

        mock_manager.assert_called_once_with(
            self.manager_col._conn,
            '/redfish/v1/Managers/RMC',
            redfish_version=self.manager_col.redfish_version
        )

    @mock.patch.object(manager, 'Manager', autospec=True)
    def test_get_members(self, mock_manager):
        members = self.manager_col.get_members()
        self.assertEqual(mock_manager.call_count, 3)
        self.assertIsInstance(members, list)
        self.assertEqual(3, len(members))
