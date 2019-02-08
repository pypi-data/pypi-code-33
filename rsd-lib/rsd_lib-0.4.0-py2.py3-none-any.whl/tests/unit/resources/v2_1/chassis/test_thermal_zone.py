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

from rsd_lib.resources.v2_1.chassis import thermal_zone


class ThermalZoneTestCase(testtools.TestCase):

    def setUp(self):
        super(ThermalZoneTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'thermal_zone.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.thermal_zone_inst = thermal_zone.ThermalZone(
            self.conn, '/redfish/v1/Chassis/Rack1/ThermalZones/Thermal1',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.thermal_zone_inst._parse_attributes()
        self.assertEqual('1', self.thermal_zone_inst.identity)
        self.assertEqual('thermal zone 1', self.thermal_zone_inst.name)
        self.assertEqual('thermal zone 1 description',
                         self.thermal_zone_inst.description)
        self.assertEqual('Enabled', self.thermal_zone_inst.status.state)
        self.assertEqual('OK', self.thermal_zone_inst.status.health)
        self.assertEqual(None, self.thermal_zone_inst.status.health_rollup)
        self.assertEqual('OU', self.thermal_zone_inst.rack_location.rack_units)
        self.assertEqual(0, self.thermal_zone_inst.rack_location.xlocation)
        self.assertEqual(1, self.thermal_zone_inst.rack_location.ulocation)
        self.assertEqual(8, self.thermal_zone_inst.rack_location.uheight)
        self.assertEqual('111100', self.thermal_zone_inst.presence)
        self.assertEqual(50, self.thermal_zone_inst.desired_speed_pwm)
        self.assertEqual(3000, self.thermal_zone_inst.desired_speed_rpm)
        self.assertEqual(6, self.thermal_zone_inst.max_fans_supported)
        self.assertEqual(6, self.thermal_zone_inst.number_of_fans_present)
        self.assertEqual(80, self.thermal_zone_inst.volumetric_airflow)
        self.assertEqual(
            'Fan 1', self.thermal_zone_inst.fans[0].name)
        self.assertEqual(
            0, self.thermal_zone_inst.fans[0].reading_rpm)
        self.assertEqual(
            'Enabled', self.thermal_zone_inst.fans[0].status.state)
        self.assertEqual(
            'OK', self.thermal_zone_inst.fans[0].status.health)
        self.assertEqual(
            None, self.thermal_zone_inst.fans[0].status.health_rollup)
        self.assertEqual(
            'OU',
            self.thermal_zone_inst.fans[0].rack_location.rack_units)
        self.assertEqual(
            0, self.thermal_zone_inst.fans[0].rack_location.xlocation)
        self.assertEqual(
            1, self.thermal_zone_inst.fans[0].rack_location.ulocation)
        self.assertEqual(
            8, self.thermal_zone_inst.fans[0].rack_location.uheight)
        self.assertEqual(
            'Inlet Temperature', self.thermal_zone_inst.temperatures[0].name)
        self.assertEqual(
            'Enabled', self.thermal_zone_inst.temperatures[0].status.state)
        self.assertEqual(
            'OK', self.thermal_zone_inst.temperatures[0].status.health)
        self.assertEqual(
            None, self.thermal_zone_inst.temperatures[0].status.health_rollup)
        self.assertEqual(
            21, self.thermal_zone_inst.temperatures[0].reading_celsius)
        self.assertEqual(
            'Intake', self.thermal_zone_inst.temperatures[0].physical_context)
        self.assertEqual(
            'Outlet Temperature', self.thermal_zone_inst.temperatures[1].name)
        self.assertEqual(
            'Enabled', self.thermal_zone_inst.temperatures[1].status.state)
        self.assertEqual(
            'OK', self.thermal_zone_inst.temperatures[1].status.health)
        self.assertEqual(
            None, self.thermal_zone_inst.temperatures[1].status.health_rollup)
        self.assertEqual(
            35, self.thermal_zone_inst.temperatures[1].reading_celsius)
        self.assertEqual(
            'Exhaust', self.thermal_zone_inst.temperatures[1].physical_context)


class ThermalZoneCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(ThermalZoneCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'thermal_zone_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
            self.thermal_zone_col = thermal_zone.\
                ThermalZoneCollection(
                    self.conn, '/redfish/v1/Chassis/Rack1/ThermalZones',
                    redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.thermal_zone_col._parse_attributes()
        self.assertEqual('1.1.0', self.thermal_zone_col.redfish_version)
        self.assertEqual(('/redfish/v1/Chassis/Rack1/ThermalZones/Thermal1',),
                         self.thermal_zone_col.members_identities)

    @mock.patch.object(thermal_zone, 'ThermalZone', autospec=True)
    def test_get_member(self, mock_thermal_zone):
        self.thermal_zone_col.get_member(
            '/redfish/v1/Chassis/Rack1/ThermalZones/Thermal1')
        mock_thermal_zone.assert_called_once_with(
            self.thermal_zone_col._conn,
            '/redfish/v1/Chassis/Rack1/ThermalZones/Thermal1',
            redfish_version=self.thermal_zone_col.redfish_version)

    @mock.patch.object(thermal_zone, 'ThermalZone', autospec=True)
    def test_get_members(self, mock_thermal_zone):
        members = self.thermal_zone_col.get_members()
        calls = [
            mock.call(self.thermal_zone_col._conn,
                      '/redfish/v1/Chassis/Rack1/ThermalZones/Thermal1',
                      redfish_version=self.thermal_zone_col.
                      redfish_version)
        ]
        mock_thermal_zone.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
