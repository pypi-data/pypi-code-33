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

from sushy.resources import base
from sushy import utils

from rsd_lib.resources.v2_1.ethernet_switch import acl
from rsd_lib.resources.v2_1.ethernet_switch import port
from rsd_lib import utils as rsd_lib_utils

LOG = logging.getLogger(__name__)


class StatusField(base.CompositeField):
    state = base.Field('State')

    health = base.Field('Health')


class LinksField(base.CompositeField):
    chassis = base.Field('Chassis', default=(),
                         adapter=rsd_lib_utils.get_resource_identity)
    """Link to chassis of this ethernet switch"""

    managed_by = base.Field('ManagedBy', default=(),
                            adapter=utils.get_members_identities)
    """Link to manager of this  ethernet switch"""


class EthernetSwitch(base.ResourceBase):
    identity = base.Field('Id', required=True)
    """The ethernet switch identity string"""

    switch_id = base.Field('SwitchId')
    """The ethernet switch id"""

    name = base.Field('Name')
    """The ethernet switch name"""

    description = base.Field('Description')
    """The ethernet switch description"""

    manufacturer = base.Field('Manufacturer')
    """The ethernet switch manufacturer"""

    model = base.Field('Model')
    """The ethernet switch model"""

    manufacturing_date = base.Field('ManufacturingDate')
    """The ethernet switch manufacturing date"""

    seria_number = base.Field('SerialNumber')
    """The ethernet switch serial number"""

    part_number = base.Field('PartNumber')
    """The ethernet switch port number"""

    firmware_name = base.Field('FirmwareName')
    """The ethernet switch fireware name"""

    firmware_version = base.Field('FirmwareVersion')
    """The ethernet switch firmware version"""

    role = base.Field('Role')
    """The ethernet switch role"""

    status = StatusField('Status')
    """The ethernet switch status"""

    links = LinksField('Links')
    """The links to ethernet switch"""

    def __init__(self, conncetor, identity, redfish_version=None):
        """A class representing a EthernetSwitch

        :param connector: A Connector instance
        :param identity: The identity of the EthernetSwitch resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(EthernetSwitch, self).__init__(conncetor,
                                             identity,
                                             redfish_version)

    def _get_port_collection_path(self):
        """Helper function to find the PortCollection path"""
        return utils.get_sub_resource_path_by(self, 'Ports')

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

    def _get_acl_collection_path(self):
        """Helper function to find the ACLCollection path"""
        return utils.get_sub_resource_path_by(self, 'ACLs')

    @property
    @utils.cache_it
    def acls(self):
        """Property to provide reference to `ACLCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return acl.ACLCollection(
            self._conn, self._get_acl_collection_path(),
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
