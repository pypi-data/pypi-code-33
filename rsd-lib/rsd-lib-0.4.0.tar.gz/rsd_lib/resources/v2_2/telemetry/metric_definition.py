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

from rsd_lib import utils as rsd_lib_utils


class WildcardsField(base.ListField):
    name = base.Field("Name")
    """This property shall contain a name for a Wildcard for a key"""

    keys = base.Field("Keys")
    """If the value is an empty string, then the server shall substitute every
       current key. Each not empty key value shall be substituted for the
       wildcard
    """


class CalculationParameterField(base.ListField):
    source_metric = base.Field("SourceMetric")
    """The metric property used as the input into the calculation"""

    result_metric = base.Field("ResultMetric")
    """The metric property used to store the results of the calculation"""


class MetricDefinition(base.ResourceBase):

    name = base.Field('Name')
    """The CPUHealth metric definition name"""

    identity = base.Field('Id', required=True)
    """The CPUHealth metric definition identity string"""

    description = base.Field('Description')
    """The metric definition description"""

    sensor_type = base.Field('SensorType')
    """This property represents the type of sensor that this resource
       represents
    """

    metric_type = base.Field('MetricType')
    """Specifies the type of metric provided"""

    implementation = base.Field('Implementation')
    """The value of this property shall designate how the sensor is implemented
    """

    sensing_interval = base.Field('SensingInterval')
    """This property specifies the time interval between when a metric or
       sensor reading is updated
    """

    physical_context = base.Field('PhysicalContext')
    """Specifies the physical context of the sensor"""

    units = base.Field('Units')
    """Units of measure for this metric"""

    min_reading_range = base.Field(
        'MinReadingRange', adapter=rsd_lib_utils.num_or_none)
    """Minimum value for Reading"""

    max_reading_range = base.Field(
        'MaxReadingRange', adapter=rsd_lib_utils.num_or_none)
    """Maximum value for Reading"""

    discrete_values = base.Field('DiscreteValues')
    """This array property specifies possible values of a discrete metric"""

    precision = base.Field('Precision', adapter=rsd_lib_utils.num_or_none)
    """Number of significant digits in the Reading described by
       MetricProperties field
    """

    calibration = base.Field('Calibration', adapter=rsd_lib_utils.num_or_none)
    """Specifies the calibration offset added to the Reading to obtain an
       accurate value
    """

    isLinear = base.Field('IsLinear', adapter=bool)
    """Indicates linear or non-linear values"""

    calculable = base.Field('Calculable')
    """The value shall define the caculatability of this metric"""

    data_type = base.Field('DataType')
    """The data type of the corresponding metric values"""

    accuracy = base.Field('Accuracy', adapter=rsd_lib_utils.num_or_none)
    """Estimated percent error of measured vs. actual values"""

    time_stamp_accuracy = base.Field('TimeStampAccuracy')
    """Accuracy of the timestamp"""

    calculation_time_interval = base.Field('CalculationTimeInterval')
    """This property specifies the time interval over which a calculated
       metric algorithm is performed
    """

    calculation_algorithm = base.Field('CalculationAlgorithm')
    """This property specifies the calculation which is performed on a source
       metric to obtain the metric being defined
    """

    calculation_parameters = CalculationParameterField('CalculationParameters')
    """Specifies the resource properties (metric) which are characterized by
       this definition
    """

    wildcards = WildcardsField("Wildcards")
    """The property shall contain an array of wildcards and their replacements
       strings, which are to appliced to the MetricProperties array property
    """

    metric_properties = base.Field('MetricProperties')
    """A collection of URI for the properties on which this metric definition
       is defined
    """


class MetricDefinitionCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return MetricDefinition
