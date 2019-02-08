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

from rsd_lib import utils as rsd_lib_utils


class DiscreteTriggerConditionField(base.ListField):
    name = base.Field("Name")
    """This property shall contain a name for the trigger"""

    trigger_value = base.Field("TriggerValue")
    """This property contains the value that sets a trigger"""

    previous_value = base.Field("PreviousValue")
    """If present, this property shall contain a previous value that shall be
       used in evaluating the behavior of setting the trigger.
    """


class NumericTriggerConditionField(base.ListField):
    name = base.Field("Name")
    """This property shall contain a name for the trigger"""

    value = base.Field("Value", adapter=rsd_lib_utils.num_or_none)
    """This property shall contain the value of the trigger"""

    direction_of_crossing = base.Field("DirectionOfCrossing")
    """If present, this property shall contain the direction of crossing. If
       not present, the direction is not relevant
    """


class TriggerConditionField(base.CompositeField):
    dwell_interval = base.Field("DwellInterval")
    """The value shall be an ISO 8601 conformant interval during which the
       triggering state shall persist before the trigger is invoked.
    """

    trigger_type = base.Field("TriggerType")
    """The value of this property shall specific the type of trigger"""

    discrete_trigger_conditions = DiscreteTriggerConditionField(
        "DiscreteTriggerConditions")
    """A Trigger condition based on TriggerDiscreteCondition"""

    filter_trigger_condition = base.Field("FilterTriggerCondition")
    """A Trigger condition based on FilterTriggerCondition"""

    numeric_trigger_conditions = NumericTriggerConditionField(
        "NumericTriggerConditions")
    """A Trigger condition based on NumericTriggerConditions"""


class StatusField(base.CompositeField):
    state = base.Field("State")
    """The status state"""

    health = base.Field("Health")
    """The status health"""


class Metric(base.ResourceBase):
    identity = base.Field("Id")
    """The metric identity"""

    name = base.Field('Name')
    """The metric name"""

    description = base.Field('Description')
    """The metric description"""

    metric_properties = base.Field("MetricProperties")
    """The report definition metric properties"""

    collection_function = base.Field('CollectionFunction')
    """If present, the value shall define the function to apply over the
       collection duration
    """

    collection_duration = base.Field('CollectionDuration')
    """This property shall not be present if  MetricDefinition.Timescope=Point
       or if MetricDefintion.Duration is present.  If present, the value shall
       be an ISO 8601 duration of the interval over which this metric value
       shall be computed.
    """

    trigger_condition = TriggerConditionField("TriggerCondition")
    """If present the values define conditions that shall be met before the
       event is triggered.  This trigger applies to all properties defined by
       the value of the MetricPropertyDeclaration property in the associated
       MetricDefinition and as constrained by the MetricScope property.
    """

    status = StatusField("Status")
    """The report definition status"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a Metric

        :param connector: A Connector instance
        :param identity: The identity of the Metric resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(Metric, self).__init__(connector, identity, redfish_version)
