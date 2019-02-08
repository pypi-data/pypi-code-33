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

from sushy.resources import base
from sushy import utils

from rsd_lib.resources.v2_1.manager import network_protocol
from rsd_lib.resources.v2_1.system import ethernet_interface
from rsd_lib import utils as rsd_lib_utils


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class GraphicalConsoleField(base.CompositeField):
    service_enabled = base.Field('ServiceEnabled')
    max_concurrent_sessions = base.Field('MaxConcurrentSessions',
                                         adapter=rsd_lib_utils.num_or_none)
    connect_types_supported = base.Field('ConnectTypesSupported')


class SerialConsoleField(base.CompositeField):
    service_enabled = base.Field('ServiceEnabled')
    max_concurrent_sessions = base.Field('MaxConcurrentSessions',
                                         adapter=rsd_lib_utils.num_or_none)
    connect_types_supported = base.Field('ConnectTypesSupported')


class CommandShellField(base.CompositeField):
    service_enabled = base.Field('ServiceEnabled')
    max_concurrent_sessions = base.Field('MaxConcurrentSessions',
                                         adapter=rsd_lib_utils.num_or_none)
    connect_types_supported = base.Field('ConnectTypesSupported')


class LinksField(base.CompositeField):
    manager_for_servers = base.Field('ManagerForServers', default=(),
                                     adapter=utils.get_members_identities)
    """Link to managed servers of this manager"""

    manager_for_chassis = base.Field('ManagerForChassis', default=(),
                                     adapter=utils.get_members_identities)
    """Link to managed chassis of this manager"""

    oem = base.Field('Oem')
    """The oem options values of links (dict)"""


class Manager(base.ResourceBase):
    identity = base.Field('Id', required=True)
    """The manager identity string"""

    name = base.Field('Name')
    """The manager name"""

    manager_type = base.Field('ManagerType')
    """The manager type"""

    description = base.Field('Description')
    """The manager description"""

    service_entry_point_uuid = base.Field('ServiceEntryPointUUID')
    """The manager service entry point uuid"""

    uuid = base.Field('UUID')
    """The manager uuid"""

    model = base.Field('Model')
    """The manager model"""

    status = StatusField("Status")
    """The manager status"""

    graphical_console = GraphicalConsoleField('GraphicalConsole')
    """The manager graphical console"""

    serial_console = SerialConsoleField('SerialConsole')
    """The manager serial console"""

    command_shell = CommandShellField('CommandShell')
    """The manager shell console"""

    firmware_version = base.Field('FirmwareVersion')
    """The manager firmware version"""

    links = LinksField('Links')
    """These links to related components of this manager"""

    oem = base.Field('Oem')
    """The manager oem options values (dict)"""

    power_state = base.Field('PowerState')
    """The manager power state"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a manager

        :param connector: A Connector instance
        :param identity: The identity of the chassis resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(Manager, self).__init__(connector, identity, redfish_version)

    def _get_network_protocol_path(self):
        """Helper function to find the network protocol path"""
        return utils.get_sub_resource_path_by(self, 'NetworkProtocol')

    def _get_ethernet_interfaces_path(self):
        """Helper function to find the Ethernet Interfaces path"""
        return utils.get_sub_resource_path_by(self, 'EthernetInterfaces')

    @property
    @utils.cache_it
    def network_protocol(self):
        """Property to provide reference to `network protocol` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return network_protocol.NetworkProtocol(
            self._conn, self._get_network_protocol_path(),
            redfish_version=self.redfish_version)

    @property
    @utils.cache_it
    def ethernet_interfaces(self):
        """Property to provide reference to `EthernetInterfaceCollection`

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return ethernet_interface.EthernetInterfaceCollection(
            self._conn, self._get_ethernet_interfaces_path(),
            redfish_version=self.redfish_version)


class ManagerCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Manager

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a Manager Collection

        :param connector: A Connector instance
        :param path: The canonical path to the manager collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ManagerCollection, self).__init__(connector,
                                                path,
                                                redfish_version)
