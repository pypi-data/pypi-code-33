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

from sushy.resources import base
from sushy import utils

from rsd_lib.resources.v2_1.ethernet_switch import vlan
from rsd_lib import utils as rsd_lib_utils


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class IPv4AddressesField(base.ListField):
    address = base.Field("Address")
    """The IPv4Addresses address"""

    subnet_mask = base.Field("SubnetMask")
    """The IPv4Addresses subnetmask"""

    address_origin = base.Field("AddressOrigin")
    """The IPv4Addresses addressorigin"""

    gateway = base.Field("Gateway")
    """The IPv4Addresses gateway"""


class IPv6AddressesField(base.ListField):
    address = base.Field("Address")
    """The IPv4Addresses address"""

    prefix_length = base.Field("PrefixLength",
                               adapter=rsd_lib_utils.num_or_none)
    """The prefix length of IPv6 addresses"""

    address_origin = base.Field("AddressOrigin")
    """The IPv4Addresses address origin"""

    address_state = base.Field("AddressState")
    """The address state of IPv6 addresses"""


class IPv6StaticAddressesField(base.ListField):
    address = base.Field("Address")
    """The IPv6 static addresses"""

    prefix_length = base.Field("PrefixLength")
    """The IPv6 prefix length"""


class IPv6AddressPolicyTableField(base.ListField):
    prefix = base.Field("Prefix")
    """The IPv6 Address Policy Table prefix"""

    precedence = base.Field("Precedence", adapter=rsd_lib_utils.num_or_none)
    """The IPv6 Address Policy Table precedence"""

    label = base.Field("Label", adapter=rsd_lib_utils.num_or_none)
    """The IPv6 Address Policy Table label"""


class IntelRackScaleField(base.CompositeField):
    neighbor_port = base.Field("NeighborPort",
                               adapter=rsd_lib_utils.get_resource_identity)
    """The neighbor port of Rack ScaleIntel"""


class OemField(base.CompositeField):
    intel_rackScale = IntelRackScaleField("Intel_RackScale")
    """The Oem Intel_RackScale"""


class LinksField(base.CompositeField):
    oem = OemField("Oem")
    """"The oem of Links"""


class VLANField(base.CompositeField):
    vlan_enable = base.Field("VLANEnable", adapter=bool)
    """Whether the vlan is enable"""

    vlan_id = base.Field("VLANId", adapter=rsd_lib_utils.num_or_none)
    """The vlan id"""


class EthernetInterface(base.ResourceBase):
    identity = base.Field('Id', required=True)
    """The EthernetInterface identity string"""

    name = base.Field('Name')
    """The EthernetInterface identity string"""

    description = base.Field('Description')
    """The EthernetInterface description"""

    status = StatusField('Status')
    """The EthernetInterface Status"""

    interface_enabled = base.Field("InterfaceEnabled", adapter=bool)
    """Whether the interface is enabled"""

    permanent_mac_address = base.Field("PermanentMACAddress")
    """The EthernetInterface PermanentMACAddress"""

    mac_address = base.Field("MACAddress")
    """The EthernetInterface MACAddress"""

    speed_mbps = base.Field("SpeedMbps", adapter=rsd_lib_utils.num_or_none)
    """The EthernetInterface SpeedMbps"""

    auto_neg = base.Field("AutoNeg", adapter=bool)
    """Whether the EthernetInterface is AutoNeg"""

    full_duplex = base.Field("FullDuplex", adapter=bool)
    """Whether the EthernetInterface is FullDuplex"""

    mtu_size = base.Field("MTUSize", adapter=rsd_lib_utils.num_or_none)
    """The EthernetInterface MTUSize"""

    host_name = base.Field("HostName")
    """The EthernetInterface hostname"""

    fqdn = base.Field("FQDN")
    """The EthernetInterface FQDN"""

    ipv6_default_gateway = base.Field("IPv6DefaultGateway")
    """The EthernetInterface IPv6DefaultGateway"""

    max_ipv6_static_addresses = base.Field("MaxIPv6StaticAddresses",
                                           adapter=rsd_lib_utils.num_or_none)
    """The EthernetInterface MaxIPv6StaticAddresses"""

    name_servers = base.Field("NameServers")
    """The EthernetInterface nameservers"""

    ipv4_addresses = IPv4AddressesField("IPv4Addresses")
    """The EthernetInterface IPv4 addresses"""

    ipv6_addresses = IPv6AddressesField("IPv6Addresses")
    """The EthernetInterface IPv4 addresses"""

    ipv6_static_addresses = IPv6StaticAddressesField("IPv6StaticAddresses")
    """The EthernetInterface IPv6 Static Addresses"""

    ipv6_address_policy_table = IPv6AddressPolicyTableField(
        "IPv6AddressPolicyTable")
    """The EthernetInterface IPv6 Address Policy Table"""

    vlan = VLANField("VLAN")
    """The EthernetInterface VLAN"""

    links = LinksField("Links")
    """The EthernetInterface links"""

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


class EthernetInterfaceCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return EthernetInterface

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a EthernetInterface Collection

        :param connector: A Connector instance
        :param path: The canonical path to the EthernetInterface collection
            resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """

        super(EthernetInterfaceCollection, self).__init__(connector,
                                                          path,
                                                          redfish_version)
