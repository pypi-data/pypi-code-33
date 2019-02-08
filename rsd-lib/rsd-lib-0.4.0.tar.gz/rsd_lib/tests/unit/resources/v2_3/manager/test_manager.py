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

from rsd_lib.resources.v2_3.manager import manager
from rsd_lib.resources.v2_3.system import ethernet_interface


class TestManager(base.TestCase):

    def setUp(self):
        super(TestManager, self).setUp()
        self.conn = mock.Mock()

        with open('rsd_lib/tests/unit/json_samples/v2_3/manager.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.manager_inst = manager.Manager(self.conn,
                                            '/redfish/v1/Manager/PSME',
                                            redfish_version='1.0.2')

    def test__get_ethernet_interfaces_path(self):
        expected = '/redfish/v1/Managers/PSME/EthernetInterfaces'
        result = self.manager_inst._get_ethernet_interfaces_path()
        self.assertEqual(expected, result)

    def test_ethernet_interfaces(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'manager_ethernet_interface_collection.json', 'r') as f:
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
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'manager_ethernet_interface_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.manager_inst.ethernet_interfaces,
                              ethernet_interface.EthernetInterfaceCollection)

        # On refreshing the manager instance...
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'manager.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.manager_inst.invalidate()
        self.manager_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'manager_ethernet_interface_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.manager_inst.ethernet_interfaces,
                              ethernet_interface.EthernetInterfaceCollection)


class TestManagerCollection(base.TestCase):

    def setUp(self):
        super(TestManagerCollection, self).setUp()
        self.conn = mock.Mock()

        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'manager_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.manager_col = manager.ManagerCollection(self.conn,
                                                     'redfish/v1/Managers',
                                                     redfish_version='1.0.2')

    def test_parse_attributes(self):
        self.manager_col._parse_attributes()
        self.assertEqual('1.0.2', self.manager_col.redfish_version)
        self.assertEqual('Manager Collection', self.manager_col.name)
        self.assertEqual(('/redfish/v1/Managers/BMC1',
                          '/redfish/v1/Managers/BMC2',
                          '/redfish/v1/Managers/PSME',),
                         self.manager_col.members_identities)

    @mock.patch.object(manager, 'Manager', autospec=True)
    def test_get_member(self, mock_manager):
        self.manager_col.get_member('/redfish/v1/Managers/BMC1')

        mock_manager.assert_called_once_with(
            self.manager_col._conn,
            '/redfish/v1/Managers/BMC1',
            redfish_version=self.manager_col.redfish_version
        )

    @mock.patch.object(manager, 'Manager', autospec=True)
    def test_get_members(self, mock_manager):
        members = self.manager_col.get_members()
        self.assertEqual(mock_manager.call_count, 3)
        self.assertIsInstance(members, list)
        self.assertEqual(3, len(members))
