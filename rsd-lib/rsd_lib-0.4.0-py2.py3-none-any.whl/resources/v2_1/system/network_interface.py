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

from rsd_lib.resources.v2_1.system import network_device_function


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class NetworkInterface(base.ResourceBase):

    name = base.Field('Name')
    """The NetworkDeviceFunction name"""

    identity = base.Field('Id', required=True)
    """The NetworkDeviceFunction identity string"""

    description = base.Field('Description')
    """The description of NetworkDeviceFunction"""

    status = StatusField('Status')
    """The NetworkDeviceFunction status"""

    links = base.Field('Links')
    """Links for this NetworkDeviceFunction"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a NetworkInterface

        :param connector: A Connector instance
        :param identity: The identity of the NetworkInterface
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(NetworkInterface, self).__init__(connector, identity,
                                               redfish_version)

    def _get_network_device_functions_path(self):
        """Helper function to find the NetworkDeviceFunctions path"""
        return utils.get_sub_resource_path_by(self, 'NetworkDeviceFunctions')

    @property
    @utils.cache_it
    def network_device_functions(self):
        """Property to provide reference to `NetworkDeviceFunctionCollection`

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return network_device_function.NetworkDeviceFunctionCollection(
            self._conn, self._get_network_device_functions_path(),
            redfish_version=self.redfish_version)


class NetworkInterfaceCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return NetworkInterface

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a NetworkInterfaceCollection

        :param connector: A Connector instance
        :param path: The canonical path to the NetworkInterface collection
                     resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(NetworkInterfaceCollection, self).__init__(connector, path,
                                                         redfish_version)
