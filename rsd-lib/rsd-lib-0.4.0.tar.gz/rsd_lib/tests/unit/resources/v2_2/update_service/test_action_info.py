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

from rsd_lib.resources.v2_2.update_service import action_info


class ActionInfoTestCase(testtools.TestCase):

    def setUp(self):
        super(ActionInfoTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'update_service_action_info.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.action_info_inst = action_info.ActionInfo(
            self.conn, '/redfish/v1/UpdateService/SimpleUpdateActionInfo',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.action_info_inst._parse_attributes()
        self.assertEqual({}, self.action_info_inst.oem)

    def test_parameters(self):
        # | WHEN |
        actual_parameters = self.action_info_inst.parameters
        # | THEN |
        expected = [
            {
                "name": "ImageURI",
                "required": True,
                "data_type": "String"
            },
            {
                "name": "TransferProtocol",
                "required": False,
                "data_type": "String",
                "allowable_values": [

                ]
            },
            {
                "name": "Targets",
                "required": False,
                "data_type": "StringArray",
                "allowable_values": [

                ]
            }
        ]
        self.assertEqual(expected, actual_parameters)

        # tests for same object on invoking subsequently
        self.assertIs(actual_parameters,
                      self.action_info_inst.parameters)

    def test_parameters_on_refresh(self):
        expected = [
            {
                "name": "ImageURI",
                "required": True,
                "data_type": "String"
            },
            {
                "name": "TransferProtocol",
                "required": False,
                "data_type": "String",
                "allowable_values": [

                ]
            },
            {
                "name": "Targets",
                "required": False,
                "data_type": "StringArray",
                "allowable_values": [

                ]
            }
        ]
        self.assertEqual(expected, self.action_info_inst.parameters)

        self.action_info_inst.invalidate()
        self.action_info_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'update_service_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertEqual(expected, self.action_info_inst.parameters)
