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
from rsd_lib.resources.v2_2.update_service import update_service


class UpdateServiceTestCase(testtools.TestCase):

    def setUp(self):
        super(UpdateServiceTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/update_service.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.update_service_inst = update_service.UpdateService(
            self.conn, '/redfish/v1/UpdateService',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.update_service_inst._parse_attributes()
        self.assertEqual("UpdateService", self.update_service_inst.identity)
        self.assertEqual("Update service", self.update_service_inst.name)
        self.assertEqual("Disabled", self.update_service_inst.status.state)
        self.assertEqual(None, self.update_service_inst.status.health)
        self.assertEqual(None, self.update_service_inst.status.health_rollup)
        self.assertEqual(False, self.update_service_inst.service_enabled)
        self.assertEqual("/redfish/v1/UpdateService/Actions/SimpleUpdate",
                         self.update_service_inst.actions.simple_update.target)
        self.assertEqual({}, self.update_service_inst.actions.oem)
        self.assertEqual({}, self.update_service_inst.oem)
        self.assertEqual("/redfish/v1/$metadata#UpdateService/$entity",
                         self.update_service_inst.odata_context)

    def test__get_action_info_path(self):
        expected = '/redfish/v1/UpdateService/SimpleUpdateActionInfo'
        result = self.update_service_inst._get_action_info_path()
        self.assertEqual(expected, result)

    def test_action_info(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'update_service_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_action_info = self.update_service_inst.action_info
        # | THEN |
        self.assertIsInstance(actual_action_info,
                              action_info.ActionInfo)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_action_info,
                      self.update_service_inst.action_info)
        self.conn.get.return_value.json.assert_not_called()

    def test_action_info_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'update_service_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.update_service_inst.action_info,
                              action_info.ActionInfo)

        # On refreshing the update service instance...
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'update_service.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.update_service_inst.invalidate()
        self.update_service_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'update_service_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.update_service_inst.action_info,
                              action_info.ActionInfo)
