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

from rsd_lib.resources.v2_1.ethernet_switch import static_mac
from rsd_lib.resources.v2_1.ethernet_switch import vlan
from rsd_lib import utils as rsd_lib_utils

LOG = logging.getLogger(__name__)


class StatusField(base.CompositeField):
    state = base.Field('State')
    """The port state"""

    health = base.Field('Health')
    """The port health"""

    health_rollup = base.Field('HealthRollup')
    """The port health rollup"""


class NeighborInfoField(base.CompositeField):
    switch_id = base.Field('SwitchId')
    port_id = base.Field('PortId')
    cable_id = base.Field('CableId')


class IPv4AddressesField(base.ListField):
    address = base.Field('Address')
    """The port ipv4 address"""

    subnet_mask = base.Field('SubnetMask')
    """The port ipv4 address subnet mask"""

    address_origin = base.Field('AddressOrigin')
    """The port ipv4 address origin"""

    gateway = base.Field('Gateway')
    """The port ipv4 address gateway"""


class IPv6AddressesField(base.ListField):
    address = base.Field('Address')
    """The port ipv6 address"""

    prefix_length = base.Field(
        'PrefixLength', adapter=rsd_lib_utils.num_or_none)
    """The port ipv6 address prefix length"""

    address_origin = base.Field('AddressOrigin')
    """The port ipv6 address origin"""

    address_state = base.Field('AddressState')
    """The port ipv6 address gateway"""


class LinksField(base.CompositeField):
    primary_vlan = base.Field('PrimaryVLAN',
                              adapter=rsd_lib_utils.get_resource_identity)
    switch = base.Field('Switch', adapter=rsd_lib_utils.get_resource_identity)
    member_of_port = base.Field('MemberOfPort',
                                adapter=rsd_lib_utils.get_resource_identity)
    port_members = base.Field('PortMembers')
    active_acls = base.Field('ActiveACLs',
                             adapter=utils.get_members_identities)


class Port(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The port identity string"""

    name = base.Field('Name')
    """The port name"""

    description = base.Field('Description')
    """The port description"""

    port_id = base.Field('PortId')
    """The port id"""

    status = StatusField('Status')
    """The port status"""

    link_type = base.Field('LinkType')
    """The port link type"""

    operational_state = base.Field('OperationalState')
    """The port operational state"""

    administrative_state = base.Field('AdministrativeState')
    """The port administrative state"""

    link_speed_mbps = base.Field(
        'LinkSpeedMbps', adapter=rsd_lib_utils.num_or_none)
    """The port link speed(mbps)"""

    neighbor_info = NeighborInfoField('NeighborInfo')
    """The port neighbor info"""

    neighbor_mac = base.Field('NeighborMAC')
    """The port neighbor mac"""

    frame_size = base.Field(
        'FrameSize', adapter=rsd_lib_utils.num_or_none)
    """The port frame size"""

    autosense = base.Field('Autosense', adapter=bool)
    """The boolean indicate the autosense is enabled or not"""

    full_duplex = base.Field('FullDuplex', adapter=bool)
    """The boolean indicate the full duplex is enabled or not"""

    mac_address = base.Field('MACAddress')
    """The port mac address"""

    ipv4_addresses = IPv4AddressesField('IPv4Addresses')
    """The port ipv4 link info"""

    ipv6_addresses = IPv6AddressesField('IPv6Addresses')
    """The port ipv6 link info"""

    port_class = base.Field('PortClass')
    """The port class"""

    port_mode = base.Field('PortMode')
    """The port mode"""

    port_type = base.Field('PortType')
    """The port type"""

    links = LinksField('Links')
    """The port links"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing an Port

        :param connector: A Connector instance
        :param identity: The identity of the Port resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(Port, self).__init__(connector, identity, redfish_version)

    def _get_static_mac_collection_path(self):
        """Helper function to find the StaticMACCollection path"""
        return utils.get_sub_resource_path_by(self, 'StaticMACs')

    @property
    @utils.cache_it
    def static_macs(self):
        """Property to provide reference to `StaticMACollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return static_mac.StaticMACCollection(
            self._conn, self._get_static_mac_collection_path(),
            redfish_version=self.redfish_version)

    def _get_vlan_collection_path(self):
        """Helper function to find the VLANCollection path"""
        return utils.get_sub_resource_path_by(self, 'VLANs')

    @property
    @utils.cache_it
    def vlans(self):
        """Property to provide reference to `VLANCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return vlan.VLANCollection(
            self._conn, self._get_vlan_collection_path(),
            redfish_version=self.redfish_version)


class PortCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return Port

    def __init__(self, connector, path, redfish_version=None):
        """A class representing an Port

        :param connector: A Connector instance
        :param path: The canonical path to the Port collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(PortCollection, self).__init__(connector, path, redfish_version)
