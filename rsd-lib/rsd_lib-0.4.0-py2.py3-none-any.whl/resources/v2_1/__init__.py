# Copyright 2017 Intel, Inc.
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

from rsd_lib.resources.v2_1.chassis import chassis
from rsd_lib.resources.v2_1.ethernet_switch import ethernet_switch
from rsd_lib.resources.v2_1.event_service import event_service
from rsd_lib.resources.v2_1.fabric import fabric
from rsd_lib.resources.v2_1.manager import manager
from rsd_lib.resources.v2_1.node import node
from rsd_lib.resources.v2_1.registries import registries
from rsd_lib.resources.v2_1.storage_service import storage_service
from rsd_lib.resources.v2_1.system import system
from rsd_lib.resources.v2_1.task import task_service


class RSDLibV2_1(base.ResourceBase):
    _systems_path = base.Field(['Systems', '@odata.id'], required=True)
    """SystemCollection path"""

    _nodes_path = base.Field(['Nodes', '@odata.id'], required=True)
    """NodeCollection path"""

    _chassis_path = base.Field(['Chassis', '@odata.id'])
    """ChassisCollection path"""

    _storage_service_path = base.Field(['Services', '@odata.id'])
    """StorageServiceCollection path"""

    _fabrics_path = base.Field(['Fabrics', '@odata.id'])
    """FabricCollection path"""

    _managers_path = base.Field(['Managers', '@odata.id'])
    """ManagerCollection path"""

    _ethernet_switches_path = base.Field(['EthernetSwitches', '@odata.id'])
    """EthernetSwitchCollecton path"""

    _task_service_path = base.Field(['Tasks', '@odata.id'])
    """Task Service path"""

    _registries_path = base.Field(['Registries', '@odata.id'])
    """RegistriesCollection path"""

    _event_service_path = base.Field(['EventService', '@odata.id'])
    """Event Service path"""

    _redfish_version = base.Field(['RedfishVersion'])
    """Redfish version"""

    _rsd_api_version = base.Field(['Oem', 'Intel_RackScale', 'ApiVersion'])
    """RSD API version"""

    def __init__(self, connector, identity="/redfish/v1/",
                 redfish_version=None):
        """A class representing a ComposedNode

        :param connector: A Connector instance
        :param identity: The identity of the Node resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(RSDLibV2_1, self).__init__(connector, identity, redfish_version)

    def get_system_collection(self):
        """Get the SystemCollection object

        :raises: MissingAttributeError, if the collection attribute is
            not found
        :returns: a SystemCollection object
        """
        return system.SystemCollection(self._conn, self._systems_path,
                                       redfish_version=self.redfish_version)

    def get_system(self, identity):
        """Given the identity return a System object

        :param identity: The identity of the System resource
        :returns: The System object
        """
        return system.System(self._conn, identity,
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

    def get_chassis_collection(self):
        """Get the ChassisCollection object

        :raises: MissingAttributeError, if the collection attribute is
            not found
        :returns: a ChassisCollection object
        """
        return chassis.ChassisCollection(self._conn,
                                         self._chassis_path,
                                         redfish_version=self.redfish_version)

    def get_chassis(self, identity):
        """Given the identity return a Chassis object

        :param identity: The identity of the Chassis resource
        :returns: The Chassis object
        """
        return chassis.Chassis(self._conn,
                               identity,
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

    def get_task_service(self):
        """Get the TaskService object

        :returns: The TaskService object
        """
        return task_service.TaskService(self._conn,
                                        self._task_service_path,
                                        redfish_version=self.redfish_version)

    def get_registries_collection(self):
        """Get the RegistriesCollection object

        :raises: MissingAttributeError, if the collection attribute is
            not found
        :returns: a RegistriesCollection object
        """
        return registries.RegistriesCollection(
            self._conn,
            self._registries_path,
            redfish_version=self.redfish_version
        )

    def get_registries(self, identity):
        """Given the identity return a Registries object

        :param identity: The identity of the registries resource
        :returns: The Registries object
        """
        return registries.Registries(
            self._conn,
            identity,
            redfish_version=self.redfish_version)

    def get_event_service(self):
        """Return a EventService object

        :returns: The EventService object
        """
        return event_service.EventService(self._conn,
                                          self._event_service_path,
                                          redfish_version=self.redfish_version)
