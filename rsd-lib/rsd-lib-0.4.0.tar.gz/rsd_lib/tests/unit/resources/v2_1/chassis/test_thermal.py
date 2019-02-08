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

from rsd_lib.resources.v2_1.chassis import thermal


class ThermalTestCase(testtools.TestCase):

    def setUp(self):
        super(ThermalTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'thermal.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.thermal_inst = thermal.Thermal(
            self.conn, '/redfish/v1/Chassis/Rack1/Thermal',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.thermal_inst._parse_attributes()
        self.assertEqual('Thermal', self.thermal_inst.identity)
        self.assertEqual('ThermalName', self.thermal_inst.name)
        self.assertEqual('Thermal Subsystem',
                         self.thermal_inst.description)
        # voltage sensors section
        self.assertEqual(
            'Drawer inlet Temp', self.thermal_inst.temperatures[0].name)
        self.assertEqual('0', self.thermal_inst.temperatures[0].member_id)
        self.assertEqual(
            'Enabled', self.thermal_inst.temperatures[0].status.state)
        self.assertEqual('OK', self.thermal_inst.temperatures[0].status.health)
        self.assertEqual(
            None, self.thermal_inst.temperatures[0].status.health_rollup)
        self.assertEqual(42, self.thermal_inst.temperatures[0].sensor_number)
        self.assertEqual(21, self.thermal_inst.temperatures[0].reading_celsius)
        self.assertEqual(
            42, self.thermal_inst.temperatures[0].upper_threshold_non_critical)
        self.assertEqual(
            42, self.thermal_inst.temperatures[0].upper_threshold_critical)
        self.assertEqual(
            42, self.thermal_inst.temperatures[0].upper_threshold_fatal)
        self.assertEqual(
            42, self.thermal_inst.temperatures[0].lower_threshold_non_critical)
        self.assertEqual(
            5, self.thermal_inst.temperatures[0].lower_threshold_critical)
        self.assertEqual(
            42, self.thermal_inst.temperatures[0].lower_threshold_fatal)
        self.assertEqual(
            0, self.thermal_inst.temperatures[0].min_reading_range)
        self.assertEqual(
            200, self.thermal_inst.temperatures[0].max_reading_range)
        self.assertEqual(
            'Intake', self.thermal_inst.temperatures[0].physical_context)
        self.assertEqual(('/redfish/v1/Chassis/Drawer1',),
                         self.thermal_inst.temperatures[0].related_item)
        # fans section
        self.assertEqual(
            'BaseBoard System Fan', self.thermal_inst.fans[0].name)
        self.assertEqual('0', self.thermal_inst.fans[0].member_id)
        self.assertEqual('Enabled', self.thermal_inst.fans[0].status.state)
        self.assertEqual('OK', self.thermal_inst.fans[0].status.health)
        self.assertEqual(
            None, self.thermal_inst.fans[0].status.health_rollup)
        self.assertEqual(2100, self.thermal_inst.fans[0].reading)
        self.assertEqual('RPM', self.thermal_inst.fans[0].reading_units)
        self.assertEqual(
            42, self.thermal_inst.fans[0].upper_threshold_non_critical)
        self.assertEqual(
            4200, self.thermal_inst.fans[0].upper_threshold_critical)
        self.assertEqual(42, self.thermal_inst.fans[0].upper_threshold_fatal)
        self.assertEqual(
            42, self.thermal_inst.fans[0].lower_threshold_non_critical)
        self.assertEqual(
            5, self.thermal_inst.fans[0].lower_threshold_critical)
        self.assertEqual(42, self.thermal_inst.fans[0].lower_threshold_fatal)
        self.assertEqual(0, self.thermal_inst.fans[0].min_reading_range)
        self.assertEqual(5000, self.thermal_inst.fans[0].max_reading_range)
        self.assertEqual(
            'Backplane', self.thermal_inst.fans[0].physical_context)
        self.assertEqual(('/redfish/v1/Chassis/Rack1',),
                         self.thermal_inst.fans[0].related_item)
        self.assertEqual(('/redfish/v1/Chassis/Rack1/Thermal#/Redundancy/0',),
                         self.thermal_inst.fans[0].redundancy)
        # redundancy device section
        self.assertEqual(
            'BaseBoard System Fans',
            self.thermal_inst.redundancy[0].name)
        self.assertEqual('0', self.thermal_inst.redundancy[0].member_id)
        self.assertEqual(
            'Disabled', self.thermal_inst.redundancy[0].status.state)
        self.assertEqual('OK', self.thermal_inst.redundancy[0].status.health)
        self.assertEqual(
            None, self.thermal_inst.redundancy[0].status.health_rollup)
        self.assertEqual('N+m', self.thermal_inst.redundancy[0].mode)
        self.assertEqual(2, self.thermal_inst.redundancy[0].max_num_supported)
        self.assertEqual(1, self.thermal_inst.redundancy[0].min_num_needed)
        self.assertEqual(
            ('/redfish/v1/Chassis/1/Thermal#/Fans/0',),
            self.thermal_inst.redundancy[0].redundancy_set)
        self.assertEqual(
            False, self.thermal_inst.redundancy[0].redundancy_enabled)
