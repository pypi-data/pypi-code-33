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

from rsd_lib.resources import v2_2
from rsd_lib.resources.v2_3.ethernet_switch import ethernet_switch
from rsd_lib.resources.v2_3.fabric import fabric
from rsd_lib.resources.v2_3.manager import manager
from rsd_lib.resources.v2_3.node import node
from rsd_lib.resources.v2_3.storage_service import storage_service
from rsd_lib.resources.v2_3.system import system


class RSDLibV2_3(v2_2.RSDLibV2_2):

    _ethernet_switches_path = base.Field(
        ['Oem', 'Intel_RackScale', 'EthernetSwitches', '@odata.id'])
    """EthernetSwitchCollecton path"""

    _storage_service_path = base.Field(['StorageServices', '@odata.id'])
    """StorageServiceCollection path"""

    def get_system(self, identity):
        """Given the identity return a System object

        :param identity: The identity of the System resource
        :returns: The System object
        """
        return system.System(self._conn, identity,
                             redfish_version=self.redfish_version)

    def get_system_collection(self):
        """Get the SystemCollection object

        :raises: MissingAttributeError, if the collection attribute is
            not found
        :returns: a SystemCollection object
        """
        return system.SystemCollection(self._conn, self._systems_path,
                                       redfish_version=self.redfish_version)

    def get_node_collection(self):
        """Get the NodeCollection object

        :raises: MissingAttributeError, if the collection attribute is
            not found
        :returns: a NodeCollection object
        """
        return node.NodeCollection(self._conn, self._nodes_path,
                                   redfish_version=self.redfish_version)

    def get_node(self, identity):
        """Given the identity return a Node object

        :param identity: The identity of the Node resource
        :returns: The Node object
        """
        return node.Node(self._conn, identity,
                         redfish_version=self.redfish_version)

    def get_manager_collection(self):
        """Get the ManagerCollection object

        :raises: MissingAttributeError, if the collection attribute is
            not found
        :returns: a ManagerCollection object
        """
        return manager.ManagerCollection(self._conn,
                                         self._managers_path,
                                         redfish_version=self.redfish_version)

    def get_manager(self, identity):
        """Given the identity return a Manager object

        :param identity: The identity of the Manager resource
        :returns: The Manager object
        """
        return manager.Manager(self._conn,
                               identity,
                               redfish_version=self.redfish_version)

    def get_storage_service_collection(self):
        """Get the StorageServiceCollection object

        :raises: MissingAttributeError, if the collection attribute is
            not found
        :returns: a StorageServiceCollection object
        """
        return storage_service.StorageServiceCollection(
            self._conn, self._storage_service_path,
            redfish_version=self.redfish_version)

    def get_storage_service(self, identity):
        """Given the identity return a StorageService object

        :param identity: The identity of the StorageService resource
        :returns: The StorageService object
        """
        return storage_service.StorageService(
            self._conn, identity,
            redfish_version=self.redfish_version)

    def get_fabric_collection(self):
        """Get the FabricCollection object

        :raises: MissingAttributeError, if the collection attribute is
            not found
        :returns: a FabricCollection object
        """
        return fabric.FabricCollection(self._conn,
                                       self._fabrics_path,
                                       redfish_version=self.redfish_version)

    def get_fabric(self, identity):
        """Given the identity return a Fabric object

        :param identity: The identity of the Fabric resource
        :returns: The Fabric object
        """
        return fabric.Fabric(self._conn,
                             identity,
                             redfish_version=self.redfish_version)

    def get_ethernet_switch_collection(self):
        """Get the EthernetSwitchCollection object

        :raises: MissingAttributeError, if the collection attribute is
            not found
        :returns: a EthernetSwitchCollection object
        """
        return ethernet_switch.EthernetSwitchCollection(
            self._conn,
            self._ethernet_switches_path,
            redfish_version=self.redfish_version
        )

    def get_ethernet_switch(self, identity):
        """Given the identity return a EthernetSwitch object

        :param identity: The identity of the EthernetSwitch resource
        :returns: The EthernetSwitch object
        """
        return ethernet_switch.EthernetSwitch(
            self._conn,
            identity,
            redfish_version=self.redfish_version)
