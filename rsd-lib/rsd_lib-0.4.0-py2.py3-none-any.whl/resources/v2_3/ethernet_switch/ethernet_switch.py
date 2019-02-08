# Copyright 2018 99cloud, Inc.
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

import logging

from rsd_lib.resources.v2_2.ethernet_switch import ethernet_switch\
    as v2_2_ethernet_switch
from sushy.resources import base

from rsd_lib import utils as rsd_lib_utils

LOG = logging.getLogger(__name__)


class ClassToPriorityMappingField(base.ListField):
    priority = base.Field('Priority', adapter=rsd_lib_utils.num_or_none)

    traffic_class = base.Field(
        'TrafficClass', adapter=rsd_lib_utils.num_or_none)


class PriorityFlowControlField(base.CompositeField):
    enabled = base.Field('Enabled', adapter=bool)

    lossless_priorities = base.Field('LosslessPriorities')


class PriorityToClassMappingField(base.ListField):
    priority = base.Field('Priority', adapter=rsd_lib_utils.num_or_none)

    traffic_class = base.Field(
        'TrafficClass', adapter=rsd_lib_utils.num_or_none)


class TrafficClassficationField(base.ListField):
    port = base.Field('Port', adapter=rsd_lib_utils.num_or_none)

    protocol = base.Field('Protocol')

    traffic_class = base.Field(
        'TrafficClass', adapter=rsd_lib_utils.num_or_none)


class TransmissionSelectionField(base.ListField):
    bandwidth_percent = base.Field(
        'BandwidthPercent', adapter=rsd_lib_utils.num_or_none)

    traffic_class = base.Field(
        'TrafficClass', adapter=rsd_lib_utils.num_or_none)


class EthernetSwitch(v2_2_ethernet_switch.EthernetSwitch):
    class_to_priority_mapping = ClassToPriorityMappingField(
        'ClassToPriorityMapping')
    """The ethernet switch class to priority mapping"""

    dcbx_enabled = base.Field('DCBXEnabled', adapter=bool)
    """The boolean indicate this dcbx is enabled or not"""

    ets_enabled = base.Field('ETSEnabled', adapter=bool)
    """The boolean indicate this etse is enabled or not"""

    lldp_enabled = base.Field('LLDPEnabled', adapter=bool)
    """The boolean indicate this lldp is enabled or not"""

    max_acl_number = base.Field('MaxACLNumber')
    """The ethernet switch max acl number"""

    metrics = base.Field('Metrics', default=(),
                         adapter=rsd_lib_utils.get_resource_identity)
    """The ethernet switch metrics"""

    priority_flow_control = PriorityFlowControlField('PriorityFlowControl')
    """The ethernet switch priority flow control"""

    priority_to_class_mapping = PriorityToClassMappingField(
        'PriorityToClassMapping')
    """The ethernet switch priority to class mapping"""

    traffic_classification = TrafficClassficationField('TrafficClassification')
    """The ethernet switch traffic classification"""

    transmission_selection = TransmissionSelectionField(
        'TransmissionSelection')
    """The ethernet switch transmission selection"""


class EthernetSwitchCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return EthernetSwitch

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a EthernetSwitch Collection

        :param connector: A Connector instance
        :param path: The canonical path to the EthernetSwitch collection
            resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(EthernetSwitchCollection, self).__init__(connector,
                                                       path,
                                                       redfish_version)
