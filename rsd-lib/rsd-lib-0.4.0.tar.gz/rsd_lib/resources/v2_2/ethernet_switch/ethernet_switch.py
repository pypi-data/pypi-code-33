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

from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch \
    as v2_1_ethernet_switch
from rsd_lib.resources.v2_2.ethernet_switch import metrics
from rsd_lib.resources.v2_2.ethernet_switch import port

from sushy.resources import base
from sushy import utils


class EthernetSwitch(v2_1_ethernet_switch.EthernetSwitch):

    @property
    @utils.cache_it
    def ports(self):
        """Property to provide reference to `PortCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return port.PortCollection(
            self._conn, self._get_port_collection_path(),
            redfish_version=self.redfish_version)

    def _get_metrics_path(self):
        """Helper function to find the Metrics path"""
        return utils.get_sub_resource_path_by(self, 'Metrics')

    @property
    @utils.cache_it
    def metrics(self):
        """Property to provide reference to `Metrics` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return metrics.Metrics(
            self._conn, self._get_metrics_path(),
            redfish_version=self.redfish_version)


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
