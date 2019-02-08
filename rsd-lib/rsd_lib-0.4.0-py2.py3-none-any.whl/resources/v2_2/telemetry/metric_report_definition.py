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

from jsonschema import validate
import logging

from sushy import exceptions
from sushy.resources import base
from sushy import utils

from rsd_lib.resources.v2_2.telemetry import metric
from rsd_lib.resources.v2_2.telemetry import metric_report
from rsd_lib.resources.v2_2.telemetry import metric_report_definition_schemas


LOG = logging.getLogger(__name__)


class ScheduleField(base.CompositeField):
    recurrence_interval = base.Field("RecurrenceInterval")
    """The schedule recurrence interval"""


class WildcardsField(base.ListField):
    name = base.Field("Name")
    """This property shall contain a name for a Wildcard for a key"""

    keys = base.Field("Keys")
    """If the value is an empty string, then the server shall substitute every
       current key. Each not empty key value shall be substituted for the
       wildcard
    """


class StatusField(base.CompositeField):
    state = base.Field("State")
    """The status state"""

    health = base.Field("Health")
    """The status health"""

    health_rollup = base.Field('HealthRollup')
    """The status health_rollup"""


class MetricReportDefinition(base.ResourceBase):
    identity = base.Field("Id")
    """The metric report definition identity"""

    name = base.Field('Name')
    """The metric report definition name"""

    description = base.Field('Description')
    """The metric report definition description"""

    schedule = ScheduleField("Schedule")
    """If present, A metric values collected starting at each scheduled
       interval and for the time specified by Duration. No more than
       Schedule.MaxOccurrences values shall be collected for this metric. If
       not present, the corresponding metric values shall be collected when the
       related metric report is retrieved.
    """

    metric_report_type = base.Field("MetricReportType")
    """The value shall specify the collection type for the corresponding
       metric values
    """

    collection_time_scope = base.Field("CollectionTimeScope")
    """The value shall specify the time scope for collecting the corresponding
       metric values
    """

    report_actions = base.Field("ReportActions")
    """The value of this property shall specify the action to perform when the
       metric report is generated. When a metric report is generated, place the
       metric information in the resource specified by the MetricReport
       property. The Volatile property will specify the behavior if
       MetricReport resource already exists.
    """

    volatile = base.Field("Volatile")
    """Entries in the resulting metric value properties are reused on each
       scheduled interval
    """

    wildcards = WildcardsField("Wildcards")
    """The property shall contain an array of wildcards and their replacements
       strings, which are to appliced to the MetricProperties array property
    """

    status = StatusField("Status")
    """The report definition status"""

    metric_properties = base.Field("MetricProperties")
    """The report definition metric properties"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a MetricReportDefinition

        :param connector: A Connector instance
        :param identity: The identity of the MetricReportDefinition resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(MetricReportDefinition, self).__init__(
            connector, identity, redfish_version)

    def _get_metrics_path(self):
        """Helper function to find the metrics path"""
        if 'Metrics' not in self.json:
            raise exceptions.MissingAttributeError(
                attribute='Metrics', resource=self.path)

        return utils.get_members_identities(self.json.get('Metrics'))

    @property
    @utils.cache_it
    def metrics(self):
        """Property to provide collection to `Metric`

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return [metric.Metric(
            self._conn, path, redfish_version=self.redfish_version)
            for path in self._get_metrics_path()]

    def _get_metric_report_path(self):
        """Helper function to find the metric report path"""
        return utils.get_sub_resource_path_by(self, 'MetricReport')

    @property
    @utils.cache_it
    def metric_report(self):
        """Property to provide reference to `MetricReport` instance

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return metric_report.MetricReport(
            self._conn, self._get_metric_report_path(),
            redfish_version=self.redfish_version)

    def delete(self):
        """Delete report definition"""
        self._conn.delete(self.path)


class MetricReportDefinitionCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return MetricReportDefinition

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a ReportDefinitionCollection

        :param connector: A Connector instance
        :param path: The canonical path to the ReportDefinition collection
            resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(MetricReportDefinitionCollection, self).__init__(
            connector, path, redfish_version)

    def create_metric_report_definition(self, metric_report_definition_req):
        """Create a new report definition

        :param metric_report_definition_req: JSON for event subscription
        :returns: The uri of the new event report definition
        """
        target_uri = self._path
        validate(metric_report_definition_req,
                 metric_report_definition_schemas.report_definition_req_schema)

        resp = self._conn.post(target_uri, data=metric_report_definition_req)

        report_definition_url = resp.headers['Location']
        LOG.info("report definition created at %s", report_definition_url)
        return report_definition_url[report_definition_url.find(self._path):]
