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

from rsd_lib.resources.v2_2.telemetry import trigger
from rsd_lib.tests.unit.fakes import request_fakes


class TriggerTestCase(testtools.TestCase):

    def setUp(self):
        super(TriggerTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/numeric_trigger.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.trigger_inst = trigger.Trigger(
            self.conn,
            '/redfish/v1/TelemetryService/Triggers/ProcessorTemperature',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.trigger_inst._parse_attributes()
        self.assertEqual("ProcessorTemperature", self.trigger_inst.identity)
        self.assertEqual("Triggers for Processor Temperature Malfunction",
                         self.trigger_inst.name)
        self.assertEqual(None, self.trigger_inst.description)

        self.assertEqual('Enabled', self.trigger_inst.status.state)
        self.assertEqual('OK', self.trigger_inst.status.health)
        self.assertEqual(None, self.trigger_inst.status.health_rollup)

        self.assertEqual('Numeric', self.trigger_inst.metric_type)
        self.assertEqual(["Transmit"], self.trigger_inst.trigger_actions)
        self.assertEqual(None, self.trigger_inst.discrete_trigger_condition)
        self.assertEqual(None, self.trigger_inst.discrete_triggers)
        self.assertEqual(None, self.trigger_inst.wildcards)
        self.assertEqual(
            [
                "/redfish/v1/Systems/System1/Processors/CPU0/Metrics#/"
                "TemperatureCelsius",
                "/redfish/v1/Systems/System1/Processors/CPU1/Metrics#/"
                "TemperatureCelsius"
            ],
            self.trigger_inst.metric_properties)

        self.assertEqual(
            'UpperThresholdCritical',
            self.trigger_inst.numeric_triggers[0].name)
        self.assertEqual(90, self.trigger_inst.numeric_triggers[0].value)
        self.assertEqual(
            'Increasing',
            self.trigger_inst.numeric_triggers[0].direction_of_crossing)
        self.assertEqual(
            1, self.trigger_inst.numeric_triggers[0].dwell_tim_msec)
        self.assertEqual(
            'Critical', self.trigger_inst.numeric_triggers[0].severity)

        self.assertEqual(
            'UpperThresholdNonCritical',
            self.trigger_inst.numeric_triggers[1].name)
        self.assertEqual(75, self.trigger_inst.numeric_triggers[1].value)
        self.assertEqual(
            'Increasing',
            self.trigger_inst.numeric_triggers[1].direction_of_crossing)
        self.assertEqual(
            4, self.trigger_inst.numeric_triggers[1].dwell_tim_msec)
        self.assertEqual(
            'Warning', self.trigger_inst.numeric_triggers[1].severity)

        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'discrete_trigger.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.trigger_inst.refresh()

        self.assertEqual(
            "ProcessorMachineCheckError", self.trigger_inst.identity)
        self.assertEqual("Trigger for Processor Machine Check Error",
                         self.trigger_inst.name)
        self.assertEqual(
            "Triggers for System1 Processor Machine Check Error",
            self.trigger_inst.description)

        self.assertEqual('Enabled', self.trigger_inst.status.state)
        self.assertEqual('OK', self.trigger_inst.status.health)
        self.assertEqual(None, self.trigger_inst.status.health_rollup)

        self.assertEqual('Discrete', self.trigger_inst.metric_type)
        self.assertEqual(["Transmit"], self.trigger_inst.trigger_actions)
        self.assertEqual(
            'Specified', self.trigger_inst.discrete_trigger_condition)
        self.assertEqual(
            None, self.trigger_inst.numeric_triggers)
        self.assertEqual(None, self.trigger_inst.wildcards)
        self.assertEqual(
            [
                "/redfish/v1/Systems/System1/Processors/CPU0/Metrics#/"
                "CPUHealth",
                "/redfish/v1/Systems/System1/Processors/CPU1/Metrics#/"
                "CPUHealth"
            ],
            self.trigger_inst.metric_properties)

        self.assertEqual(None, self.trigger_inst.discrete_triggers[0].name)
        self.assertEqual(
            "Machine Check Exception",
            self.trigger_inst.discrete_triggers[0].value)
        self.assertEqual(
            1, self.trigger_inst.discrete_triggers[0].dwell_tim_msec)
        self.assertEqual(
            'Critical', self.trigger_inst.discrete_triggers[0].severity)

    def test_delete(self):
        self.trigger_inst.delete()
        self.trigger_inst._conn.delete.assert_called_once()


class TriggerCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(TriggerCollectionTestCase, self).setUp()
        self.conn = mock.Mock()

        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'trigger_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.conn.post.return_value = request_fakes.fake_request_post(
            None, headers={
                "Location": "https://localhost:8443/redfish/v1/"
                            "TelemetryService/Triggers/2"})

        self.trigger_col = trigger.TriggerCollection(
            self.conn, '/redfish/v1/TelemetryService/Triggers',
            redfish_version='1.1.0')

    def test_parse_attributes(self):
        self.trigger_col._parse_attributes()
        self.assertEqual("Triggers Collection", self.trigger_col.name)

    @mock.patch.object(trigger, 'Trigger', autospec=True)
    def test_get_member(self, mock_trigger):
        self.trigger_col.get_member(
            '/redfish/v1/TelemetryService/Triggers/ProcessorCatastrophicError')

        mock_trigger.assert_called_once_with(
            self.trigger_col._conn,
            '/redfish/v1/TelemetryService/Triggers/ProcessorCatastrophicError',
            redfish_version=self.trigger_col.redfish_version
        )

    @mock.patch.object(trigger, 'Trigger', autospec=True)
    def test_get_members(self, mock_trigger):
        members = self.trigger_col.get_members()

        calls = [
            mock.call(
                self.trigger_col._conn,
                '/redfish/v1/TelemetryService/Triggers/'
                'ProcessorCatastrophicError',
                redfish_version=self.trigger_col.redfish_version),
            mock.call(
                self.trigger_col._conn,
                '/redfish/v1/TelemetryService/Triggers/'
                'ProcessorInitializationError',
                redfish_version=self.trigger_col.redfish_version),
            mock.call(
                self.trigger_col._conn,
                '/redfish/v1/TelemetryService/Triggers/'
                'ProcessorMachineCheckError',
                redfish_version=self.trigger_col.redfish_version),
            mock.call(
                self.trigger_col._conn,
                '/redfish/v1/TelemetryService/Triggers/ProcessorPOSTFailure',
                redfish_version=self.trigger_col.redfish_version),
            mock.call(
                self.trigger_col._conn,
                '/redfish/v1/TelemetryService/Triggers/ProcessorTemperature',
                redfish_version=self.trigger_col.redfish_version),
            mock.call(
                self.trigger_col._conn,
                '/redfish/v1/TelemetryService/Triggers/ProcessorThermalTrip',
                redfish_version=self.trigger_col.redfish_version)
        ]
        mock_trigger.assert_has_calls(calls)
        self.assertEqual(mock_trigger.call_count, 6)
        self.assertIsInstance(members, list)
        self.assertEqual(6, len(members))

    def test_create_trigger(self):
        reqs = {
            "Name": "Trigger for Processor Machine Check Error",
            "Description": "Triggers for System1 Processor Machine Check "
                           "Error",
            "MetricType": "Discrete",
            "TriggerActions": [
                "Transmit"
            ],
            "DiscreteTriggerCondition": "Specified",
            "DiscreteTriggers": [
                {
                    "Value": "Machine Check Exception",
                    "DwellTimMsec": 1,
                    "Severity": "Critical"
                }
            ],
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            },
            "MetricProperties": [
                "/redfish/v1/Systems/System1/Processors/CPU0/Metrics#/"
                "CPUHealth",
                "/redfish/v1/Systems/System1/Processors/CPU1/Metrics#/"
                "CPUHealth"
            ]
        }

        result = self.trigger_col.create_trigger(
            name=reqs['Name'], description=reqs['Description'],
            metric_type=reqs['MetricType'],
            trigger_actions=reqs['TriggerActions'],
            discrete_trigger_condition=reqs['DiscreteTriggerCondition'],
            discrete_triggers=reqs['DiscreteTriggers'], status=reqs['Status'],
            metric_properties=reqs['MetricProperties'],)
        self.trigger_col._conn.post.assert_called_once_with(
            '/redfish/v1/TelemetryService/Triggers',
            data=reqs)
        self.assertEqual(
            result, '/redfish/v1/TelemetryService/Triggers/2')
