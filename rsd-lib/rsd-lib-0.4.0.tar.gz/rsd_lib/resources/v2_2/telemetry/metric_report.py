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

from sushy.resources import base
from sushy import utils

from rsd_lib import utils as rsd_lib_utils


class MetricValuesField(base.ListField):
    metric_id = base.Field('MetricId')
    """The value shall be the MetricId of the source metric within the
       associated MetricDefinition
    """

    metric_value = base.Field('MetricValue')
    """The value of the metric represented as a string. Its  data type is
       specified in including MetricResult.MetricDefinition.
    """

    time_stamp = base.Field('TimeStamp')
    """The value shall be an ISO 8601 date time for when the metric value was
       computed. Note that this may be different from the time when this
       instance is created. If Volatile is true for a given metric value
       instance, the TimeStamp changes whenever a new measurement snapshot
       is taken. A management application may establish a time series of metric
       data by retrieving the instances of metric value and sorting them
       according to their TimeStamp.
    """

    metric_property = base.Field('MetricProperty')
    """The value shall be a URI of a property contained in the scope of the
       MetricScope
    """

    metric_definition = base.Field(
        'MetricDefinition', adapter=rsd_lib_utils.get_resource_identity)
    """The value shall be a URI to the metric definition of the property"""


class MetricReport(base.ResourceBase):
    identity = base.Field("Id")
    """The metric report identity"""

    name = base.Field("Name")
    """The metric report name"""

    description = base.Field("Description")
    """The metric report description"""

    metric_values = MetricValuesField("MetricValues")
    """The metric report definition"""

    def _get_metric_report_definition_path(self):
        """Helper function to find the metric report definition path"""
        return utils.get_sub_resource_path_by(self, 'MetricReportDefinition')

    @property
    @utils.cache_it
    def metric_report_definition(self):
        """Property to provide reference to `MetricReportDefinition`

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        # Avoid metric_report and metric_report_definition module mutually
        # import each other, move import to this function
        from rsd_lib.resources.v2_2.telemetry import metric_report_definition
        return metric_report_definition.MetricReportDefinition(
            self._conn, self._get_metric_report_definition_path(),
            redfish_version=self.redfish_version)


class MetricReportCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return MetricReport

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a MetricReportCollection

        :param connector: A Connector instance
        :param path: The canonical path to the Metric Report collection
            resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(MetricReportCollection, self).__init__(connector, path,
                                                     redfish_version)
