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

import mock
from sushy import exceptions
import testtools

from rsd_lib import utils as rsd_lib_utils


class UtilsTestCase(testtools.TestCase):

    def test_get_resource_identity(self):
        self.assertIsNone(rsd_lib_utils.get_resource_identity(None))
        self.assertIsNone(rsd_lib_utils.get_resource_identity({}))
        self.assertEqual(
            '/redfish/v1/Systems/437XR1138R2/BIOS',
            rsd_lib_utils.get_resource_identity({
                "@odata.id": "/redfish/v1/Systems/437XR1138R2/BIOS"}))

    def test_num_or_none(self):
        self.assertIsNone(rsd_lib_utils.num_or_none(None))
        self.assertEqual(0, rsd_lib_utils.num_or_none('0'))
        self.assertEqual(1, rsd_lib_utils.num_or_none('1'))
        self.assertEqual(10, rsd_lib_utils.num_or_none('10.0'))
        self.assertEqual(12.5, rsd_lib_utils.num_or_none('12.5'))
        self.assertEqual(0, rsd_lib_utils.num_or_none(0))
        self.assertEqual(1, rsd_lib_utils.num_or_none(1))
        self.assertEqual(10, rsd_lib_utils.num_or_none(10.0))
        self.assertEqual(12.5, rsd_lib_utils.num_or_none(12.5))

    def test_get_sub_resource_path_list_by(self):
        sample = {
            "Links": {
                "PCIeDevices": [
                    {"@data.id": "/redfish/v1/Chassis/1/PCIeDevices/Device1"},
                    {"@data.id": "/redfish/v1/Chassis/1/PCIeDevices/Device2"}
                ]
            }
        }

        mock_resource = mock.Mock()
        mock_resource.json = sample

        self.assertRaises(
            ValueError,
            rsd_lib_utils.get_sub_resource_path_list_by,
            mock_resource,
            None)

        self.assertEqual(
            sorted([
                '/redfish/v1/Chassis/1/PCIeDevices/Device1',
                '/redfish/v1/Chassis/1/PCIeDevices/Device2'
            ]),
            sorted(rsd_lib_utils.get_sub_resource_path_list_by(
                mock_resource, ["Links", "PCIeDevices"]))
        )

        mock_resource.json = {'Links': {}}
        self.assertRaises(
            exceptions.MissingAttributeError,
            rsd_lib_utils.get_sub_resource_path_list_by,
            mock_resource,
            'Links'
        )
