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

from rsd_lib.resources.v2_1.chassis import power


class PowerTestCase(testtools.TestCase):

    def setUp(self):
        super(PowerTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'power.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.power_inst = power.Power(
            self.conn, '/redfish/v1/Chassis/Rack1/Power',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.power_inst._parse_attributes()
        self.assertEqual('Power', self.power_inst.identity)
        self.assertEqual('PowerName', self.power_inst.name)
        self.assertEqual('PowerSubsystem',
                         self.power_inst.description)
        # PowerControl section
        self.assertEqual(
            'System Power Control', self.power_inst.power_control[0].name)
        self.assertEqual('0', self.power_inst.power_control[0].member_id)
        self.assertEqual(
            8000, self.power_inst.power_control[0].power_consumed_watts)
        self.assertEqual(
            8500, self.power_inst.power_control[0].power_requested_watts)
        self.assertEqual(
            8500, self.power_inst.power_control[0].power_available_watts)
        self.assertEqual(
            10000, self.power_inst.power_control[0].power_capacity_watts)
        self.assertEqual(
            8500, self.power_inst.power_control[0].power_allocated_watts)
        self.assertEqual(
            'Enabled', self.power_inst.power_control[0].status.state)
        self.assertEqual('OK', self.power_inst.power_control[0].status.health)
        self.assertEqual(
            'OK', self.power_inst.power_control[0].status.health_rollup)
        self.assertEqual(
            30, self.power_inst.power_control[0].power_metrics.interval_in_min)
        self.assertEqual(
            7500,
            self.power_inst.power_control[0].power_metrics.min_consumed_watts)
        self.assertEqual(
            8200,
            self.power_inst.power_control[0].power_metrics.max_consumed_watts)
        self.assertEqual(
            8000,
            self.power_inst.power_control[0].power_metrics.
            average_consumed_watts)
        self.assertEqual(
            9000, self.power_inst.power_control[0].power_limit.limit_in_watts)
        self.assertEqual(
            'LogEventOnly',
            self.power_inst.power_control[0].power_limit.limit_exception)
        self.assertEqual(
            42, self.power_inst.power_control[0].power_limit.correction_in_ms)
        self.assertEqual(
            ('/redfish/v1/Chassis/Drawer1', '/redfish/v1/Systems/System1'),
            self.power_inst.power_control[0].related_item)
        # voltage sensors section
        self.assertEqual('VRM1 Voltage', self.power_inst.voltages[0].name)
        self.assertEqual('0', self.power_inst.voltages[0].member_id)
        self.assertEqual('Enabled', self.power_inst.voltages[0].status.state)
        self.assertEqual('OK', self.power_inst.voltages[0].status.health)
        self.assertEqual(
            None, self.power_inst.voltages[0].status.health_rollup)
        self.assertEqual(11, self.power_inst.voltages[0].sensor_number)
        self.assertEqual(12, self.power_inst.voltages[0].reading_volts)
        self.assertEqual(
            100.5, self.power_inst.voltages[0].upper_threshold_non_critical)
        self.assertEqual(
            13, self.power_inst.voltages[0].upper_threshold_critical)
        self.assertEqual(15, self.power_inst.voltages[0].upper_threshold_fatal)
        self.assertEqual(
            11.5, self.power_inst.voltages[0].lower_threshold_non_critical)
        self.assertEqual(
            11, self.power_inst.voltages[0].lower_threshold_critical)
        self.assertEqual(10, self.power_inst.voltages[0].lower_threshold_fatal)
        self.assertEqual(0, self.power_inst.voltages[0].min_reading_range)
        self.assertEqual(20, self.power_inst.voltages[0].max_reading_range)
        self.assertEqual(
            'VoltageRegulator', self.power_inst.voltages[0].physical_context)
        self.assertEqual(('/redfish/v1/Systems/System1',),
                         self.power_inst.voltages[0].related_item)
        # power supply section
        self.assertEqual(
            'Power Supply Bay 1', self.power_inst.power_supplies[0].name)
        self.assertEqual('0', self.power_inst.power_supplies[0].member_id)
        self.assertEqual(
            'Enabled', self.power_inst.power_supplies[0].status.state)
        self.assertEqual(
            'Warning', self.power_inst.power_supplies[0].status.health)
        self.assertEqual(
            None, self.power_inst.power_supplies[0].status.health_rollup)
        self.assertEqual(
            'DC', self.power_inst.power_supplies[0].power_supply_type)
        self.assertEqual(
            'DCNeg48V',
            self.power_inst.power_supplies[0].line_input_voltage_type)
        self.assertEqual(
            -48, self.power_inst.power_supplies[0].line_input_voltage)
        self.assertEqual(
            400, self.power_inst.power_supplies[0].power_capacity_watts)
        self.assertEqual(
            192, self.power_inst.power_supplies[0].last_power_output_watts)
        self.assertEqual('499253-B21', self.power_inst.power_supplies[0].model)
        self.assertEqual(
            'ManufacturerName', self.power_inst.power_supplies[0].manufacturer)
        self.assertEqual(
            '1.00', self.power_inst.power_supplies[0].firmware_version)
        self.assertEqual(
            '1z0000001', self.power_inst.power_supplies[0].serial_number)
        self.assertEqual(
            '1z0000001A3a', self.power_inst.power_supplies[0].part_number)
        self.assertEqual(
            '0000001A3a', self.power_inst.power_supplies[0].spare_part_number)
        self.assertEqual(
            ('/redfish/v1/Chassis/Rack1',),
            self.power_inst.power_supplies[0].related_item)
        self.assertEqual(
            ('/redfish/v1/Chassis/1/Power#/Redundancy/0',),
            self.power_inst.power_supplies[0].redundancy)
        self.assertEqual(
            'Off', self.power_inst.power_supplies[0].indicator_led)
        self.assertEqual(
            'DC', self.power_inst.power_supplies[0].input_ranges[0].input_type)
        self.assertEqual(
            -47,
            self.power_inst.power_supplies[0].input_ranges[0].minimum_voltage)
        self.assertEqual(
            -49,
            self.power_inst.power_supplies[0].input_ranges[0].maximum_voltage)
        self.assertEqual(
            50,
            self.power_inst.power_supplies[0].input_ranges[0].
            minimum_frequency_hz)
        self.assertEqual(
            60,
            self.power_inst.power_supplies[0].input_ranges[0].
            maximum_frequency_hz)
        self.assertEqual(
            400,
            self.power_inst.power_supplies[0].input_ranges[0].output_wattage)
        # redundancy device section
        self.assertEqual(
            'PowerSupply Redundancy Group 1',
            self.power_inst.redundancy[0].name)
        self.assertEqual('0', self.power_inst.redundancy[0].member_id)
        self.assertEqual('Offline', self.power_inst.redundancy[0].status.state)
        self.assertEqual('OK', self.power_inst.redundancy[0].status.health)
        self.assertEqual(
            None, self.power_inst.redundancy[0].status.health_rollup)
        self.assertEqual('Failover', self.power_inst.redundancy[0].mode)
        self.assertEqual(2, self.power_inst.redundancy[0].max_num_supported)
        self.assertEqual(1, self.power_inst.redundancy[0].min_num_needed)
        self.assertEqual(
            ('/redfish/v1/Chassis/1/Power#/PowerSupplies/0',),
            self.power_inst.redundancy[0].redundancy_set)
