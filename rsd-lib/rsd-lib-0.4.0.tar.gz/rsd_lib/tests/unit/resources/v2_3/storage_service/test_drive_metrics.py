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

from rsd_lib.resources.v2_3.storage_service import drive_metrics


class DriveMetricsTestCase(testtools.TestCase):

    def setUp(self):
        super(DriveMetricsTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_3/drive_metrics.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.drive_metrics_inst = drive_metrics.DriveMetrics(
            self.conn, '/redfish/v1/Chassis/1/Drives/1/Metrics',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.drive_metrics_inst._parse_attributes()
        self.assertEqual('Drive Metrics for Drive',
                         self.drive_metrics_inst.name)
        self.assertEqual('Metrics for Drive 1',
                         self.drive_metrics_inst.description)
        self.assertEqual('Metrics', self.drive_metrics_inst.identity)
        self.assertEqual(318, self.drive_metrics_inst.temperature_kelvin)

        life_time = self.drive_metrics_inst.life_time
        self.assertEqual(512000, life_time.unit_size_bytes)
        self.assertEqual(1640, life_time.units_read)
        self.assertEqual(2, life_time.units_written)
        self.assertEqual(12344, life_time.host_read_commands)
        self.assertEqual(2323, life_time.host_write_commands)
        self.assertEqual(244, life_time.power_cycles)
        self.assertEqual(34566566, life_time.power_on_hours)
        self.assertEqual(545465665656, life_time.controller_busy_time_minutes)

        health_data = self.drive_metrics_inst.health_data
        self.assertEqual(67, health_data.available_spare_percentage)
        self.assertEqual(120, health_data.predicted_media_life_used_percent)
        self.assertEqual(23, health_data.unsafe_shutdowns)
        self.assertEqual(10, health_data.media_errors)
