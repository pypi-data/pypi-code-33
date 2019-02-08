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

from sushy import exceptions

from rsd_lib.resources.v2_2.telemetry import metric_report
from rsd_lib.resources.v2_2.telemetry import metric_report_definition


class MetricReportTestCase(testtools.TestCase):

    def setUp(self):
        super(MetricReportTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
                'rsd_lib/tests/unit/json_samples/v2_2/metric_report.json',
                'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.metric_report_inst = metric_report.MetricReport(
            self.conn,
            '/redfish/v1/TelemetryService/MetricReports/TransmitCPU1Metrics',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.metric_report_inst._parse_attributes()
        self.assertEqual("TransmitCPU1Metrics",
                         self.metric_report_inst.identity)
        self.assertEqual("CPU1 Metric Report", self.metric_report_inst.name)
        self.assertEqual("description-as-string",
                         self.metric_report_inst.description)
        # metric_values section
        self.assertEqual(
            None, self.metric_report_inst.metric_values[0].metric_id)
        self.assertEqual(
            "29", self.metric_report_inst.metric_values[0].metric_value)
        self.assertEqual(
            "2016-07-25T11:27:59.895513984+02:00",
            self.metric_report_inst.metric_values[0].time_stamp)
        self.assertEqual(
            "/redfish/v1/Systems/System1/Processors/CPU1/Metrics#/"
            "BandwidthPercent",
            self.metric_report_inst.metric_values[0].metric_property)
        self.assertEqual(
            "/redfish/v1/TelemetryService/MetricDefinitions/CPUBandwidth",
            self.metric_report_inst.metric_values[0].metric_definition)

        self.assertEqual(
            None, self.metric_report_inst.metric_values[1].metric_id)
        self.assertEqual(
            "FRB1 BIST Failure",
            self.metric_report_inst.metric_values[1].metric_value)
        self.assertEqual(
            "2016-07-25T11:27:59.795513984+02:00",
            self.metric_report_inst.metric_values[1].time_stamp)
        self.assertEqual(
            "/redfish/v1/Systems/System1/Processors/CPU1/Metrics#/CPUHealth",
            self.metric_report_inst.metric_values[1].metric_property)
        self.assertEqual(
            "/redfish/v1/TelemetryService/MetricDefinitions/CPUHealth",
            self.metric_report_inst.metric_values[1].metric_definition)

        self.assertEqual(
            None, self.metric_report_inst.metric_values[2].metric_id)
        self.assertEqual(
            "43", self.metric_report_inst.metric_values[2].metric_value)
        self.assertEqual(
            "2016-07-25T11:27:59.595513984+02:00",
            self.metric_report_inst.metric_values[2].time_stamp)
        self.assertEqual(
            "/redfish/v1/Systems/System1/Processors/CPU1/Metrics#/"
            "TemperatureCelsius",
            self.metric_report_inst.metric_values[2].metric_property)
        self.assertEqual(
            "/redfish/v1/TelemetryService/MetricDefinitions/CPUTemperature",
            self.metric_report_inst.metric_values[2].metric_definition)

    def test__get_metric_report_definition_path_path(self):
        self.assertEqual(
            '/redfish/v1/TelemetryService/MetricReportDefinitions/CPU1Metrics',
            self.metric_report_inst._get_metric_report_definition_path())

    def test__get_metric_report_definition_path_missing_attr(self):
        self.metric_report_inst._json.pop('MetricReportDefinition')
        with self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'attribute MetricReportDefinition'):
            self.metric_report_inst._get_metric_report_definition_path()

    def test_metric_report_definition(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report_definition.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_report_definition = \
            self.metric_report_inst.metric_report_definition
        # | THEN |
        self.assertIsInstance(
            actual_report_definition,
            metric_report_definition.MetricReportDefinition)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_report_definition,
                      self.metric_report_inst.metric_report_definition)
        self.conn.get.return_value.json.assert_not_called()

    def test_metric_report_definitions_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report_definition.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.metric_report_inst.metric_report_definition,
            metric_report_definition.MetricReportDefinition)

        # On refreshing the telemetry service instance...
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.metric_report_inst.invalidate()
        self.metric_report_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report_definition.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.metric_report_inst.metric_report_definition,
            metric_report_definition.MetricReportDefinition)


class MetricReportCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(MetricReportCollectionTestCase, self).setUp()
        self.conn = mock.Mock()

        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.metric_report_col = metric_report.MetricReportCollection(
            self.conn, '/redfish/v1/TelemetryService/MetricReports',
            redfish_version='1.1.0')

    def test_parse_attributes(self):
        self.metric_report_col._parse_attributes()
        self.assertEqual("MetricReports", self.metric_report_col.name)

    @mock.patch.object(metric_report, 'MetricReport', autospec=True)
    def test_get_member(self, mock_metric_report):
        self.metric_report_col.get_member(
            '/redfish/v1/TelemetryService/MetricReports/TransmitCPU1Metrics')

        mock_metric_report.assert_called_once_with(
            self.metric_report_col._conn,
            '/redfish/v1/TelemetryService/MetricReports/TransmitCPU1Metrics',
            redfish_version=self.metric_report_col.redfish_version
        )

    @mock.patch.object(metric_report, 'MetricReport', autospec=True)
    def test_get_members(self, mock_metric_report):
        members = self.metric_report_col.get_members()
        self.assertEqual(mock_metric_report.call_count, 1)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
