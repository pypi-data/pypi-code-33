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
import jsonschema
import mock
import testtools

from sushy import exceptions

from rsd_lib.resources.v2_2.telemetry import metric
from rsd_lib.resources.v2_2.telemetry import metric_report
from rsd_lib.resources.v2_2.telemetry import metric_report_definition
from rsd_lib.tests.unit.fakes import request_fakes


class ReportDefinitionTestCase(testtools.TestCase):

    def setUp(self):
        super(ReportDefinitionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
                'rsd_lib/tests/unit/json_samples/v2_2/'
                'metric_report_definition.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.metric_report_definition_inst = metric_report_definition.\
            MetricReportDefinition(
                self.conn,
                '/redfish/v1/TelemetryService/MetricReportDefinitions/'
                'CPU1Metrics',
                redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.metric_report_definition_inst._parse_attributes()
        self.assertEqual("CPUEventPublish",
                         self.metric_report_definition_inst.identity)
        self.assertEqual("CPU1 Metric Publisher",
                         self.metric_report_definition_inst.name)
        self.assertEqual(None,
                         self.metric_report_definition_inst.description)
        self.assertEqual(
            "PT1M",
            self.metric_report_definition_inst.schedule.recurrence_interval)
        self.assertEqual("Periodic",
                         self.metric_report_definition_inst.metric_report_type)
        self.assertEqual(
            "Interval",
            self.metric_report_definition_inst.collection_time_scope)
        self.assertEqual(['Transmit', 'Log'],
                         self.metric_report_definition_inst.report_actions)
        self.assertEqual(
            "Enabled", self.metric_report_definition_inst.status.state)
        self.assertEqual(
            "OK", self.metric_report_definition_inst.status.health)
        self.assertEqual(
            None, self.metric_report_definition_inst.status.health_rollup)
        self.assertEqual(None, self.metric_report_definition_inst.volatile)
        self.assertEqual(None, self.metric_report_definition_inst.wildcards)
        self.assertEqual(
            [
                "/redfish/v1/Systems/System1/Processors/CPU1/Metrics#"
                "/BandwidthPercent",
                "/redfish/v1/Systems/System1/Processors/CPU1/Metrics#"
                "/CPUHealth",
                "/redfish/v1/Systems/System1/Processors/CPU1/Metrics#"
                "/TemperatureCelsius"
            ],
            self.metric_report_definition_inst.metric_properties)

    def test__get_metrics_path(self):
        self.assertEqual(
            ("/redfish/v1/TelemetryService/FakeMetric",),
            self.metric_report_definition_inst._get_metrics_path())

    def test__get_metrics_path_missing_attr(self):
        self.metric_report_definition_inst._json.pop('Metrics')
        with self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Metrics'):
            self.metric_report_definition_inst._get_metrics_path()

    def test_metrics(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'processor_metrics.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_metrics = self.metric_report_definition_inst.metrics
        # | THEN |
        self.assertIsInstance(actual_metrics, list)
        self.assertIsInstance(actual_metrics[0], metric.Metric)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_metrics,
                      self.metric_report_definition_inst.metrics)
        self.conn.get.return_value.json.assert_not_called()

    def test_metrics_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'processor_metrics.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.metric_report_definition_inst.metrics, list)
        self.assertIsInstance(
            self.metric_report_definition_inst.metrics[0], metric.Metric)

        # On refreshing the telemetry service instance...
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report_definition.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.metric_report_definition_inst.invalidate()
        self.metric_report_definition_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'processor_metrics.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.metric_report_definition_inst.metrics, list)
        self.assertIsInstance(
            self.metric_report_definition_inst.metrics[0], metric.Metric)

    def test__get_metric_report_path_path(self):
        self.assertEqual(
            '/redfish/v1/TelemetryService/MetricReports/TransmitCPU1Metrics',
            self.metric_report_definition_inst._get_metric_report_path())

    def test__get_metric_report_path_missing_attr(self):
        self.metric_report_definition_inst._json.pop('MetricReport')
        with self.assertRaisesRegex(exceptions.MissingAttributeError,
                                    'attribute MetricReport'):
            self.metric_report_definition_inst._get_metric_report_path()

    def test_metric_report(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_metric_report = self.metric_report_definition_inst.metric_report
        # | THEN |
        self.assertIsInstance(
            actual_metric_report, metric_report.MetricReport)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_metric_report,
                      self.metric_report_definition_inst.metric_report)
        self.conn.get.return_value.json.assert_not_called()

    def test_metric_report_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.metric_report_definition_inst.metric_report,
            metric_report.MetricReport)

        # On refreshing the telemetry service instance...
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'telemetry_service.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.metric_report_definition_inst.invalidate()
        self.metric_report_definition_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.metric_report_definition_inst.metric_report,
            metric_report.MetricReport)

    def test_delete(self):
        self.metric_report_definition_inst.delete()
        self.metric_report_definition_inst._conn.delete.assert_called_once()


class ReportDefinitionCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(ReportDefinitionCollectionTestCase, self).setUp()
        self.conn = mock.Mock()

        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report_definition_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.conn.post.return_value = request_fakes.fake_request_post(
            None, headers={
                "Location": "https://localhost:8443/redfish/v1/"
                            "TelemetryService/MetricReportDefinitions/1"})

        self.report_definition_col = metric_report_definition.\
            MetricReportDefinitionCollection(
                self.conn,
                '/redfish/v1/TelemetryService/MetricReportDefinitions',
                redfish_version='1.1.0')

    def test_parse_attributes(self):
        self.report_definition_col._parse_attributes()
        self.assertEqual("MetricReportDefinition Collection",
                         self.report_definition_col.name)

    @mock.patch.object(
        metric_report_definition, 'MetricReportDefinition', autospec=True)
    def test_get_member(self, mock_metric_report_definition):
        self.report_definition_col.get_member(
            '/redfish/v1/TelemetryService/MetricReportDefinitions/CPU1Metrics')

        mock_metric_report_definition.assert_called_once_with(
            self.report_definition_col._conn,
            '/redfish/v1/TelemetryService/MetricReportDefinitions/CPU1Metrics',
            redfish_version=self.report_definition_col.redfish_version
        )

    @mock.patch.object(
        metric_report_definition, 'MetricReportDefinition', autospec=True)
    def test_get_members(self, mock_metric_report_definition):
        members = self.report_definition_col.get_members()
        self.assertEqual(mock_metric_report_definition.call_count, 1)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))

    def test_create_report_definition_reqs(self):
        reqs = {
            'Name': 'CPU1 Metric Publisher',
            'Schedule': {
                'RecurrenceInterval': 'PT1M'
            },
            'MetricReportType': 'Periodic',
            'CollectionTimeScope': 'Interval',
            'ReportActions': [
                'Transmit',
                'Log'
            ],
            'MetricReport': {
                '@odata.id': '/redfish/v1/TelemetryService'
                             '/MetricReports/TransmitCPU1Metrics'
            },
            'Status': {
                'State': 'Enabled',
                'Health': 'OK'
            },
            'MetricProperties': [
                '/redfish/v1/Systems/System1/Processors/CPU1/Metrics'
                '#/BandwidthPercent',
                '/redfish/v1/Systems/System1/Processors/CPU1/Metrics'
                '#/CPUHealth',
                '/redfish/v1/Systems/System1/Processors/CPU1/Metrics'
                '#/TemperatureCelsius'
            ]
        }

        result = self.report_definition_col.create_metric_report_definition(
            reqs)
        self.report_definition_col._conn.post.assert_called_once_with(
            '/redfish/v1/TelemetryService/MetricReportDefinitions',
            data=reqs)
        self.assertEqual(
            result, '/redfish/v1/TelemetryService/MetricReportDefinitions/1')

    def test_create_report_definition_invalid_reqs(self):
        reqs = {
            'Name': 'CPU1 Metric Publisher',
            'Schedule': {
                'RecurrenceInterval': 'PT1M'
            },
            'MetricReportType': 'Periodic',
            'CollectionTimeScope': 'Interval',
            'ReportActions': [
                'Transmit',
                'Log'
            ],
            'MetricReport': {
                '@odata.id': '/redfish/v1/TelemetryService/MetricReports'
                             '/TransmitCPU1Metrics'
            },
            'Status': {
                'State': 'Enabled',
                'Health': 'OK'
            },
            'MetricProperties': [
                '/redfish/v1/Systems/System1/Processors/CPU1/Metrics'
                '#/BandwidthPercent',
                '/redfish/v1/Systems/System1/Processors/CPU1/Metrics'
                '#/CPUHealth',
                '/redfish/v1/Systems/System1/Processors/CPU1/Metrics'
                '#/TemperatureCelsius'
            ]
        }

        # Wrong format
        report_definition_req = reqs.copy()
        report_definition_req.update({'ReportActions': True})
        self.assertRaises(
            jsonschema.exceptions.ValidationError,
            self.report_definition_col.create_metric_report_definition,
            report_definition_req)

        # Wrong additional fields
        report_definition_req = reqs.copy()
        report_definition_req['Additional'] = 'AdditionalField'
        self.assertRaises(
            jsonschema.exceptions.ValidationError,
            self.report_definition_col.create_metric_report_definition,
            report_definition_req)
