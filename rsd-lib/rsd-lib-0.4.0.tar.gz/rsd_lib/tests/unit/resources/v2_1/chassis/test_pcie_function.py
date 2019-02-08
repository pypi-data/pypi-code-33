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

from rsd_lib.resources.v2_1.chassis import pcie_function


class PCIeFunctionTestCase(testtools.TestCase):

    def setUp(self):
        super(PCIeFunctionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'pcie_function.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.pcie_function_inst = pcie_function.PCIeFunction(
            self.conn, '/redfish/v1/Chassis/1/PCIeDevices/Device1/Functions/1',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.pcie_function_inst._parse_attributes()
        self.assertEqual('1', self.pcie_function_inst.identity)
        self.assertEqual('SSD', self.pcie_function_inst.name)
        self.assertEqual('SSD Drive',
                         self.pcie_function_inst.description)
        self.assertEqual(
            'Enabled', self.pcie_function_inst.status.state)
        self.assertEqual('OK', self.pcie_function_inst.status.health)
        self.assertEqual(
            'OK', self.pcie_function_inst.status.health_rollup)
        self.assertEqual(1, self.pcie_function_inst.function_id)
        self.assertEqual('Physical', self.pcie_function_inst.function_type)
        self.assertEqual(
            'MassStorageController', self.pcie_function_inst.device_class)
        self.assertEqual('0xABCD', self.pcie_function_inst.device_id)
        self.assertEqual('0x8086', self.pcie_function_inst.vendor_id)
        self.assertEqual('0x10802', self.pcie_function_inst.class_code)
        self.assertEqual('0x00', self.pcie_function_inst.revision_id)
        self.assertEqual('0xABCD', self.pcie_function_inst.subsystem_id)
        self.assertEqual('0xABCD', self.pcie_function_inst.subsystem_vendor_id)
        self.assertEqual(
            None, self.pcie_function_inst.links.ethernet_interfaces)
        self.assertEqual(
            ('/redfish/v1/Chassis/PCIeSwitch1/Drives/Disk.Bay.1',),
            self.pcie_function_inst.links.drives)
        self.assertEqual(
            None, self.pcie_function_inst.links.storage_controllers)
        self.assertEqual(
            '/redfish/v1/Chassis/1/PCIeDevices/Device1',
            self.pcie_function_inst.links.pcie_device)
