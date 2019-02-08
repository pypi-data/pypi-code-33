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

from rsd_lib.resources.v2_1.system import network_device_function
from rsd_lib.resources.v2_1.system import network_interface


class NetworkInterface(testtools.TestCase):

    def setUp(self):
        super(NetworkInterface, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'network_interface.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.network_interface_inst = network_interface.NetworkInterface(
            self.conn, '/redfish/v1/Systems/System1/NetworkInterfaces/1/',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.network_interface_inst._parse_attributes()
        self.assertEqual('1.1.0', self.network_interface_inst.redfish_version)
        self.assertEqual('Network Device View',
                         self.network_interface_inst.name)
        self.assertEqual('1', self.network_interface_inst.identity)
        self.assertEqual('Network Device View',
                         self.network_interface_inst.description)
        self.assertEqual('Enabled', self.network_interface_inst.status.state)
        self.assertEqual('OK', self.network_interface_inst.status.health)
        self.assertEqual(
            'OK', self.network_interface_inst.status.health_rollup)
        self.assertEqual({}, self.network_interface_inst.links)

    def test__get_network_device_functions_path(self):
        expected = '/redfish/v1/Systems/System1/NetworkInterfaces/1/'\
                   'NetworkDeviceFunctions'
        result = self.network_interface_inst.\
            _get_network_device_functions_path()
        self.assertEqual(expected, result)

    def test_network_device_functions(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'network_device_function_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_network_device_functions = self.network_interface_inst.\
            network_device_functions
        # | THEN |
        self.assertIsInstance(
            actual_network_device_functions,
            network_device_function.NetworkDeviceFunctionCollection)
        self.conn.get.return_value.json.assert_called_once_with()
        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_network_device_functions,
                      self.network_interface_inst.network_device_functions)
        self.conn.get.return_value.json.assert_not_called()

    def test_network_device_functions_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'network_device_function_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.network_interface_inst.network_device_functions,
            network_device_function.NetworkDeviceFunctionCollection)

        # On refreshing the network_interface instance...
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'network_interface.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.network_interface_inst.invalidate()
        self.network_interface_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'network_device_function_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.network_interface_inst.network_device_functions,
            network_device_function.NetworkDeviceFunctionCollection)


class NetworkInterfaceCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(NetworkInterfaceCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'network_interface_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.network_interface_col = network_interface.\
            NetworkInterfaceCollection(
                self.conn,
                '/redfish/v1/Systems/System1/NetworkInterfaces/1',
                redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.network_interface_col._parse_attributes()
        self.assertEqual(
            '1.1.0', self.network_interface_col.redfish_version)
        self.assertEqual(
            ('/redfish/v1/Systems/System1/NetworkInterfaces/1',),
            self.network_interface_col.members_identities)

    @mock.patch.object(network_interface, 'NetworkInterface', autospec=True)
    def test_get_member(self, mock_network_interface):
        self.network_interface_col.get_member(
            '/redfish/v1/Systems/System1/NetworkInterfaces/1')
        mock_network_interface.assert_called_once_with(
            self.network_interface_col._conn,
            '/redfish/v1/Systems/System1/NetworkInterfaces/1',
            redfish_version=self.network_interface_col.redfish_version)

    @mock.patch.object(network_interface, 'NetworkInterface', autospec=True)
    def test_get_members(self, mock_network_interface):
        members = self.network_interface_col.get_members()
        mock_network_interface.assert_called_once_with(
            self.network_interface_col._conn,
            '/redfish/v1/Systems/System1/NetworkInterfaces/1',
            redfish_version=self.network_interface_col.redfish_version)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
