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

from sushy import exceptions

from rsd_lib.resources.v2_2.telemetry import metric_definition
from rsd_lib.resources.v2_2.telemetry import metric_report
from rsd_lib.resources.v2_2.telemetry import metric_report_definition
from rsd_lib.resources.v2_2.telemetry import telemetry
from rsd_lib.resources.v2_2.telemetry import trigger


class TelemetryTestCase(testtools.TestCase):

    def setUp(self):
        super(TelemetryTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'telemetry_service.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.telemetry_inst = telemetry.Telemetry(
            self.conn, '/redfish/v1/TelemetryService',
            redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.telemetry_inst._parse_attributes()
        self.assertEqual('1.1.0', self.telemetry_inst.redfish_version)
        self.assertEqual('Enabled', self.telemetry_inst.status.state)
        self.assertEqual('OK', self.telemetry_inst.status.health)
        self.assertEqual(None, self.telemetry_inst.status.health_rollup)
        self.assertEqual(None, self.telemetry_inst.max_reports)
        self.assertEqual(None, self.telemetry_inst.min_collection_interval)
        self.assertEqual(
            None, self.telemetry_inst.supported_collection_functions)

    def test__get_metric_definitions_path(self):
        self.assertEqual('/redfish/v1/TelemetryService/MetricDefinitions',
                         self.telemetry_inst._get_metric_definitions_path())

    def test__get_metric_definitions_path_missing_attr(self):
        self.telemetry_inst._json.pop('MetricDefinitions')
        with self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute MetricDefinitions'):
            self.telemetry_inst._get_metric_definitions_path()

    def test_metric_definitions(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_definition_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_metric_definitions = self.telemetry_inst.metric_definitions
        # | THEN |
        self.assertIsInstance(actual_metric_definitions,
                              metric_definition.MetricDefinitionCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_metric_definitions,
                      self.telemetry_inst.metric_definitions)
        self.conn.get.return_value.json.assert_not_called()

    def test_metric_definitions_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_definition_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.telemetry_inst.metric_definitions,
                              metric_definition.MetricDefinitionCollection)

        # On refreshing the telemetry service instance...
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'telemetry_service.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.telemetry_inst.invalidate()
        self.telemetry_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_definition_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.telemetry_inst.metric_definitions,
                              metric_definition.MetricDefinitionCollection)

    def test__get_metric_report_definitions_path_path(self):
        self.assertEqual(
            '/redfish/v1/TelemetryService/MetricReportDefinitions',
            self.telemetry_inst._get_metric_report_definitions_path())

    def test__get_metric_report_definitions_path_missing_attr(self):
        self.telemetry_inst._json.pop('MetricReportDefinitions')
        with self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'attribute MetricReportDefinitions'):
            self.telemetry_inst._get_metric_report_definitions_path()

    def test_metric_report_definitions(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report_definition_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_report_definitions = \
            self.telemetry_inst.metric_report_definitions
        # | THEN |
        self.assertIsInstance(
            actual_report_definitions,
            metric_report_definition.MetricReportDefinitionCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_report_definitions,
                      self.telemetry_inst.metric_report_definitions)
        self.conn.get.return_value.json.assert_not_called()

    def test_metric_report_definitions_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report_definition_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_inst.metric_report_definitions,
            metric_report_definition.MetricReportDefinitionCollection)

        # On refreshing the telemetry service instance...
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'telemetry_service.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.telemetry_inst.invalidate()
        self.telemetry_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report_definition_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_inst.metric_report_definitions,
            metric_report_definition.MetricReportDefinitionCollection)

    def test__get_metric_reports_path_path(self):
        self.assertEqual(
            '/redfish/v1/TelemetryService/MetricReports',
            self.telemetry_inst._get_metric_reports_path())

    def test__get_metric_reports_path_missing_attr(self):
        self.telemetry_inst._json.pop('MetricReports')
        with self.assertRaisesRegex(exceptions.MissingAttributeError,
                                    'attribute MetricReports'):
            self.telemetry_inst._get_metric_reports_path()

    def test_metric_reports(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_metric_reports = self.telemetry_inst.metric_reports
        # | THEN |
        self.assertIsInstance(
            actual_metric_reports, metric_report.MetricReportCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_metric_reports,
                      self.telemetry_inst.metric_reports)
        self.conn.get.return_value.json.assert_not_called()

    def test_metric_reports_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_inst.metric_reports,
            metric_report.MetricReportCollection)

        # On refreshing the telemetry service instance...
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'telemetry_service.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.telemetry_inst.invalidate()
        self.telemetry_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'metric_report_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_inst.metric_reports,
            metric_report.MetricReportCollection)

    def test__get_triggers_path_path(self):
        self.assertEqual(
            '/redfish/v1/TelemetryService/Triggers',
            self.telemetry_inst._get_triggers_path())

    def test__get_triggers_path_missing_attr(self):
        self.telemetry_inst._json.pop('Triggers')
        with self.assertRaisesRegex(exceptions.MissingAttributeError,
                                    'attribute Triggers'):
            self.telemetry_inst._get_triggers_path()

    def test_triggers(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'trigger_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_triggers = self.telemetry_inst.triggers
        # | THEN |
        self.assertIsInstance(
            actual_triggers, trigger.TriggerCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_triggers,
                      self.telemetry_inst.triggers)
        self.conn.get.return_value.json.assert_not_called()

    def test_triggers_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'trigger_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_inst.triggers, trigger.TriggerCollection)

        # On refreshing the telemetry service instance...
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'telemetry_service.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.telemetry_inst.invalidate()
        self.telemetry_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_2/'
                  'trigger_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(
            self.telemetry_inst.triggers, trigger.TriggerCollection)
