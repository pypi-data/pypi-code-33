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

from sushy.resources import base
from sushy import utils

from rsd_lib.resources.v2_2.telemetry import metric_definition
from rsd_lib.resources.v2_2.telemetry import metric_report
from rsd_lib.resources.v2_2.telemetry import metric_report_definition
from rsd_lib.resources.v2_2.telemetry import trigger
from rsd_lib import utils as rsd_lib_utils


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class Telemetry(base.ResourceBase):

    max_reports = base.Field('MaxReports', adapter=rsd_lib_utils.num_or_none)
    """If present, the value shall specify the maximum number of metric
       collectors that can be supported by this service
    """

    min_collection_interval = base.Field('MinCollectionInterval')
    """If present, the value shall be an ISO 8601 duration specifying the
       minimum time between collections
    """

    supported_collection_functions = base.Field('SupportedCollectionFunctions')
    """If present, the value shall define the function to apply over the
       collection duration
    """

    status = StatusField('Status')
    """The telemetry service status"""

    def _get_metric_definitions_path(self):
        """Helper function to find the metric definitions path"""
        return utils.get_sub_resource_path_by(self, 'MetricDefinitions')

    @property
    @utils.cache_it
    def metric_definitions(self):
        """Property to provide reference to `MetricDefinitions` instance

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return metric_definition.MetricDefinitionCollection(
            self._conn, self._get_metric_definitions_path(),
            redfish_version=self.redfish_version)

    def _get_metric_report_definitions_path(self):
        """Helper function to find the metric report definitions path"""
        return utils.get_sub_resource_path_by(self, 'MetricReportDefinitions')

    @property
    @utils.cache_it
    def metric_report_definitions(self):
        """Property to provide reference to `MetricReportDefinitionCollection`

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return metric_report_definition.MetricReportDefinitionCollection(
            self._conn, self._get_metric_definitions_path(),
            redfish_version=self.redfish_version)

    def _get_metric_reports_path(self):
        """Helper function to find the metric reports path"""
        return utils.get_sub_resource_path_by(self, 'MetricReports')

    @property
    @utils.cache_it
    def metric_reports(self):
        """Property to provide reference to `MetricReportCollection`

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return metric_report.MetricReportCollection(
            self._conn, self._get_metric_reports_path(),
            redfish_version=self.redfish_version)

    def _get_triggers_path(self):
        """Helper function to find the triggers path"""
        return utils.get_sub_resource_path_by(self, 'Triggers')

    @property
    @utils.cache_it
    def triggers(self):
        """Property to provide reference to `TriggerCollection`

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return trigger.TriggerCollection(
            self._conn, self._get_triggers_path(),
            redfish_version=self.redfish_version)
