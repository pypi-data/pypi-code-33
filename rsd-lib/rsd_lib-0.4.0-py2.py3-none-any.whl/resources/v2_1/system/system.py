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

from sushy.resources.system import system
from sushy import utils

from rsd_lib.resources.v2_1.system import ethernet_interface
from rsd_lib.resources.v2_1.system import memory
from rsd_lib.resources.v2_1.system import network_interface
from rsd_lib.resources.v2_1.system import storage_subsystem


class System(system.System):

    def _get_memory_collection_path(self):
        """Helper function to find the memory path"""
        return utils.get_sub_resource_path_by(self, 'Memory')

    @property
    @utils.cache_it
    def memory(self):
        """Property to provide reference to `Metrics` instance

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return memory.MemoryCollection(
            self._conn, self._get_memory_collection_path(),
            redfish_version=self.redfish_version)

    def _get_storage_subsystem_collection_path(self):
        """Helper function to find the storage subsystem path"""
        return utils.get_sub_resource_path_by(self, 'Storage')

    @property
    @utils.cache_it
    def storage_subsystem(self):
        """Property to provide reference to `StorageSubsystem` instance

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return storage_subsystem.StorageSubsystemCollection(
            self._conn, self._get_storage_subsystem_collection_path(),
            redfish_version=self.redfish_version)

    def _get_ethernet_interfaces_collection_path(self):
        """Helper function to find the ethernet interfaces path"""
        return utils.get_sub_resource_path_by(self, 'EthernetInterfaces')

    @property
    @utils.cache_it
    def ethernet_interfaces(self):
        """Property to provide reference to `EthernetInterfaceCollection`

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return ethernet_interface.EthernetInterfaceCollection(
            self._conn, self._get_ethernet_interfaces_collection_path(),
            redfish_version=self.redfish_version)

    def _get_network_interfaces_collection_path(self):
        """Helper function to find the network interfaces path"""
        return utils.get_sub_resource_path_by(self, 'NetworkInterfaces')

    @property
    @utils.cache_it
    def network_interfaces(self):
        """Property to provide reference to `NetworkInterfaceCollection`

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return network_interface.NetworkInterfaceCollection(
            self._conn, self._get_network_interfaces_collection_path(),
            redfish_version=self.redfish_version)


class SystemCollection(system.SystemCollection):

    @property
    def _resource_type(self):
        return System
