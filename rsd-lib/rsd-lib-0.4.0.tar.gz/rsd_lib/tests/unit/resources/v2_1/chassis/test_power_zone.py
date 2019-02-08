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

from rsd_lib.resources.v2_1.chassis import power_zone


class PowerZoneTestCase(testtools.TestCase):

    def setUp(self):
        super(PowerZoneTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'power_zone.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.power_zone_inst = power_zone.PowerZone(
            self.conn, '/redfish/v1/Chassis/Rack1/PowerZones/1',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.power_zone_inst._parse_attributes()
        self.assertEqual('1', self.power_zone_inst.identity)
        self.assertEqual('power zone 1', self.power_zone_inst.name)
        self.assertEqual('power zone 1 description',
                         self.power_zone_inst.description)
        self.assertEqual('Enabled', self.power_zone_inst.status.state)
        self.assertEqual('OK', self.power_zone_inst.status.health)
        self.assertEqual('OK', self.power_zone_inst.status.health_rollup)
        self.assertEqual('OU', self.power_zone_inst.rack_location.rack_units)
        self.assertEqual(0, self.power_zone_inst.rack_location.xlocation)
        self.assertEqual(1, self.power_zone_inst.rack_location.ulocation)
        self.assertEqual(8, self.power_zone_inst.rack_location.uheight)
        self.assertEqual(6, self.power_zone_inst.max_psus_supported)
        self.assertEqual('111111', self.power_zone_inst.presence)
        self.assertEqual(6, self.power_zone_inst.number_of_psus_present)
        self.assertEqual(2000, self.power_zone_inst.power_consumed_watts)
        self.assertEqual(2000, self.power_zone_inst.power_output_watts)
        self.assertEqual(3000, self.power_zone_inst.power_capacity_watts)
        self.assertEqual(
            'Power supply 1', self.power_zone_inst.power_supplies[0].name)
        self.assertEqual(
            300, self.power_zone_inst.power_supplies[0].power_capacity_watts)
        self.assertEqual(
            48, self.power_zone_inst.power_supplies[0].last_power_output_watts)
        self.assertEqual(
            '', self.power_zone_inst.power_supplies[0].manufacturer)
        self.assertEqual(
            '', self.power_zone_inst.power_supplies[0].model_number)
        self.assertEqual(
            '', self.power_zone_inst.power_supplies[0].firmware_revision)
        self.assertEqual(
            '', self.power_zone_inst.power_supplies[0].serial_number)
        self.assertEqual(
            '', self.power_zone_inst.power_supplies[0].part_number)
        self.assertEqual(
            'Enabled', self.power_zone_inst.power_supplies[0].status.state)
        self.assertEqual(
            'OK', self.power_zone_inst.power_supplies[0].status.health)
        self.assertEqual(
            'OK', self.power_zone_inst.power_supplies[0].status.health_rollup)
        self.assertEqual(
            'OU',
            self.power_zone_inst.power_supplies[0].rack_location.rack_units)
        self.assertEqual(
            0, self.power_zone_inst.power_supplies[0].rack_location.xlocation)
        self.assertEqual(
            1, self.power_zone_inst.power_supplies[0].rack_location.ulocation)
        self.assertEqual(
            8, self.power_zone_inst.power_supplies[0].rack_location.uheight)


class PowerZoneCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(PowerZoneCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'power_zone_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
            self.power_zone_col = power_zone.\
                PowerZoneCollection(
                    self.conn, '/redfish/v1/Chassis/Rack1/PowerZones',
                    redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.power_zone_col._parse_attributes()
        self.assertEqual('1.1.0', self.power_zone_col.redfish_version)
        self.assertEqual(('/redfish/v1/Chassis/Rack1/PowerZones/Power1',),
                         self.power_zone_col.members_identities)

    @mock.patch.object(power_zone, 'PowerZone', autospec=True)
    def test_get_member(self, mock_power_zone):
        self.power_zone_col.get_member(
            '/redfish/v1/Chassis/Rack1/PowerZones/Power1')
        mock_power_zone.assert_called_once_with(
            self.power_zone_col._conn,
            '/redfish/v1/Chassis/Rack1/PowerZones/Power1',
            redfish_version=self.power_zone_col.redfish_version)

    @mock.patch.object(power_zone, 'PowerZone', autospec=True)
    def test_get_members(self, mock_power_zone):
        members = self.power_zone_col.get_members()
        calls = [
            mock.call(self.power_zone_col._conn,
                      '/redfish/v1/Chassis/Rack1/PowerZones/Power1',
                      redfish_version=self.power_zone_col.
                      redfish_version)
        ]
        mock_power_zone.assert_has_calls(calls)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
