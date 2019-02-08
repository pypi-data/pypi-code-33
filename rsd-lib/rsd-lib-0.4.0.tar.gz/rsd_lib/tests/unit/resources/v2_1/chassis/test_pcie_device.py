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

from rsd_lib.resources.v2_1.chassis import pcie_device


class PCIeDeviceTestCase(testtools.TestCase):

    def setUp(self):
        super(PCIeDeviceTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'pcie_device.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.pcie_device_inst = pcie_device.PCIeDevice(
            self.conn, '/redfish/v1/Chassis/1/PCIeDevices/Device1',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.pcie_device_inst._parse_attributes()
        self.assertEqual('Device1', self.pcie_device_inst.identity)
        self.assertEqual('NVMe SSD Drive', self.pcie_device_inst.name)
        self.assertEqual('Simple NVMe Drive',
                         self.pcie_device_inst.description)
        self.assertEqual(
            'Enabled', self.pcie_device_inst.status.state)
        self.assertEqual('OK', self.pcie_device_inst.status.health)
        self.assertEqual(
            'OK', self.pcie_device_inst.status.health_rollup)
        self.assertEqual('Intel', self.pcie_device_inst.manufacturer)
        self.assertEqual('Model Name', self.pcie_device_inst.model)
        self.assertEqual('sku string', self.pcie_device_inst.sku)
        self.assertEqual('SN123456', self.pcie_device_inst.serial_number)
        self.assertEqual(
            'partnumber string', self.pcie_device_inst.part_number)
        self.assertEqual(
            'free form asset tag', self.pcie_device_inst.asset_tag)
        self.assertEqual('SingleFunction', self.pcie_device_inst.device_type)
        self.assertEqual('XYZ1234', self.pcie_device_inst.firmware_version)
        self.assertEqual(
            ('/redfish/v1/Chassis/1',), self.pcie_device_inst.links.chassis)
        self.assertEqual(
            ('/redfish/v1/Chassis/1/PCIeDevices/Device1/Functions/1',),
            self.pcie_device_inst.links.pcie_functions)

    def test_update(self):
        self.pcie_device_inst.update(asset_tag='Rack#1')
        self.pcie_device_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Chassis/1/PCIeDevices/Device1',
            data={"AssetTag": "Rack#1"})
