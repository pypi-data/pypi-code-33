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

from sushy.resources import base

from rsd_lib.resources.v2_2.telemetry import trigger_schemas
from rsd_lib import utils as rsd_lib_utils


LOG = logging.getLogger(__name__)


class NumericTriggersField(base.ListField):
    name = base.Field('Name')
    """The name of trigger"""

    value = base.Field('Value', adapter=rsd_lib_utils.num_or_none)
    """This property contains the value of the trigger"""

    direction_of_crossing = base.Field('DirectionOfCrossing')
    """This property contains the value of the trigger"""

    dwell_tim_msec = base.Field(
        'DwellTimMsec', adapter=rsd_lib_utils.num_or_none)
    """This time the excursion persists before a trigger is determined"""

    severity = base.Field('Severity')
    """This property contains the value of the Severity property in the Event
       message
    """


class DiscreteTriggersField(base.ListField):
    name = base.Field('Name')
    """The name of trigger"""

    value = base.Field('Value')
    """This property contains the value of the trigger"""

    dwell_tim_msec = base.Field(
        'DwellTimMsec', adapter=rsd_lib_utils.num_or_none)
    """This time the excursion persists before a trigger is determined"""

    severity = base.Field('Severity')
    """This property contains the value of the Severity property in the Event
       message
    """


class WildcardsField(base.ListField):
    name = base.Field("Name")
    """This property shall contain a name for a Wildcard for a key"""

    keys = base.Field("Keys")
    """If the value is an empty string, then the server shall substitute every
       current key. Each not empty key value shall be substituted for the
       wildcard
    """


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class Trigger(base.ResourceBase):
    identity = base.Field("Id")
    """The trigger identity"""

    name = base.Field("Name")
    """The trigger name"""

    description = base.Field("Description")
    """The trigger description"""

    metric_type = base.Field("MetricType")
    """The type of trigger"""

    trigger_actions = base.Field("TriggerActions")
    """The metric report description"""

    numeric_triggers = NumericTriggersField("NumericTriggers")
    """List of numeric triggers"""

    discrete_trigger_condition = base.Field("DiscreteTriggerCondition")
    """The value shall indicate how the corresponding metric"""

    discrete_triggers = DiscreteTriggersField("DiscreteTriggers")
    """List of discrete triggers"""

    status = StatusField('Status')
    """The trigger status"""

    wildcards = WildcardsField("Wildcards")
    """The property shall contain an array of wildcards and their replacements
       strings, which are to appliced to the MetricProperties array property
    """

    metric_properties = base.Field("MetricProperties")
    """The report definition metric properties"""

    def delete(self):
        """Delete trigger"""
        self._conn.delete(self.path)


class TriggerCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return Trigger

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a TriggerCollection

        :param connector: A Connector instance
        :param path: The canonical path to the Trigger collection
            resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(TriggerCollection, self).__init__(
            connector, path, redfish_version)

    def create_trigger(self, name=None, description=None, metric_type=None,
                       trigger_actions=None, numeric_triggers=None,
                       discrete_trigger_condition=None, discrete_triggers=None,
                       status=None, wildcards=None, metric_properties=None):
        """Create a new trigger

        :param name: The trigger name
        :param description: The trigger description
        :param metric_type: The type of trigger
        :param trigger_actions: The metric report description
        :param numeric_triggers: List of numeric triggers
        :param discrete_trigger_condition: The value shall indicate how the
                                           corresponding metric
        :param discrete_triggers: List of discrete triggers
        :param status: The trigger status
        :param wildcards: Wildcards used to replace values in MetricProperties
                          array property
        :param metric_properties: The report definition metric properties
        :returns: The uri of the new trigger
        """
        target_uri = self._path

        # prepare the request data of creating new trigger
        data = {}
        if name is not None:
            data['Name'] = name
        if description is not None:
            data['Description'] = description

        if metric_type is not None:
            validate(metric_type,
                     trigger_schemas.metric_type_schema)
            data['MetricType'] = metric_type

        if trigger_actions is not None:
            validate(trigger_actions,
                     trigger_schemas.trigger_actions_schema)
            data['TriggerActions'] = trigger_actions

        if numeric_triggers is not None:
            validate(numeric_triggers,
                     trigger_schemas.numeric_triggers_schema)
            data['NumericTriggers'] = numeric_triggers

        if discrete_trigger_condition is not None:
            validate(discrete_trigger_condition,
                     trigger_schemas.discrete_trigger_condition_schema)
            data['DiscreteTriggerCondition'] = discrete_trigger_condition

        if discrete_triggers is not None:
            validate(discrete_triggers,
                     trigger_schemas.discrete_triggers_schema)
            data['DiscreteTriggers'] = discrete_triggers

        if status is not None:
            validate(status,
                     trigger_schemas.status_schema)
            data['Status'] = status

        if wildcards is not None:
            validate(wildcards,
                     trigger_schemas.wildcards_schema)
            data['Wildcards'] = wildcards

        if metric_properties is not None:
            validate(metric_properties,
                     trigger_schemas.metric_properties_schema)
            data['MetricProperties'] = metric_properties

        # Issue POST request to create new trigger
        resp = self._conn.post(target_uri, data=data)
        LOG.info("Node created at %s", resp.headers['Location'])
        node_url = resp.headers['Location']

        return node_url[node_url.find(self._path):]
