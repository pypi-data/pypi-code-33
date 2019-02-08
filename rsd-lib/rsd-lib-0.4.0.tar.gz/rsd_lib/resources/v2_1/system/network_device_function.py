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

from rsd_lib import utils as rsd_lib_utils


class EthernetField(base.CompositeField):
    macaddress = base.Field('MACAddress')
    """This is the currently configured MAC address of the (logical port)
       network device function
    """


class iSCSIBootField(base.CompositeField):
    ip_address_type = base.Field('IPAddressType')
    """The type of IP address (IPv6 or IPv4) being populated in the iSCSIBoot
       IP address fields
    """

    initiator_ip_address = base.Field('InitiatorIPAddress')
    """The IPv6 or IPv4 address of the iSCSI initiator"""

    initiator_name = base.Field('InitiatorName')
    """The value of this property shall be the iSCSI boot initiator name"""

    initiator_default_gateway = base.Field('InitiatorDefaultGateway')
    """The value of this property shall be the IPv6 or IPv4 iSCSI boot default
       gateway
    """

    initiator_netmask = base.Field('InitiatorNetmask')
    """The value of this property shall be the IPv6 or IPv4 netmask of the
       iSCSI boot initiator
    """

    target_info_via_dhcp = base.Field('TargetInfoViaDHCP', adapter=bool)
    """The value of this property shall be a boolean indicating whether the
       iSCSI boot target name, LUN, IP address, and netmask should be obtained
       from DHCP
    """

    primary_target_name = base.Field('PrimaryTargetName')
    """The value of this property shall be the name of the primary iSCSI boot
       target (iSCSI Qualified Name, IQN)
    """

    primary_target_ip_address = base.Field('PrimaryTargetIPAddress')
    """The value of this property shall be the IP address (IPv6 or IPv4) for
       the primary iSCSI boot target
    """

    primary_target_tcp_port = base.Field(
        'PrimaryTargetTCPPort', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall be the TCP port for the primary iSCSI
       boot target
    """

    primary_lun = base.Field('PrimaryLUN', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall be the logical unit number (LUN) for
       the primary iSCSI boot target
    """

    primary_vlan_enable = base.Field('PrimaryVLANEnable', adapter=bool)
    """The value of this property shall be used to indicate if PrimaryVLANId
       is enabled for the primary iSCSI boot target
    """

    primary_vlan_id = base.Field(
        'PrimaryVLANId', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall be the 802.1q VLAN ID to use for iSCSI
       boot from the primary target.  This VLAN ID is only used if
       PrimaryVLANEnable is true.
    """

    primary_dns = base.Field('PrimaryDNS')
    """The value of this property shall be the IPv6 or IPv4 address of the
       primary DNS server for the iSCSI boot initiator
    """

    secondary_target_name = base.Field('SecondaryTargetName')
    """The value of this property shall be the name of the secondary iSCSI
       boot target (iSCSI Qualified Name, IQN)
    """

    secondary_target_ip_address = base.Field('SecondaryTargetIPAddress')
    """The value of this property shall be the IP address (IPv6 or IPv4) for
       the secondary iSCSI boot target
    """

    secondary_target_tcp_port = base.Field(
        'SecondaryTargetTCPPort', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall be the TCP port for the secondary
       iSCSI boot target
    """

    secondary_lun = base.Field(
        'SecondaryLUN', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall be the logical unit number (LUN) for
       the secondary iSCSI boot target
    """

    secondary_vlan_enable = base.Field('SecondaryVLANEnable', adapter=bool)
    """The value of this property shall be used to indicate if this VLAN is
       enabled for the secondary iSCSI boot target
    """

    secondary_vlan_id = base.Field(
        'SecondaryVLANId', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall be the 802.1q VLAN ID to use for iSCSI
       boot from the secondary target.  This VLAN ID is only used if
       SecondaryVLANEnable is true.
    """

    secondary_dns = base.Field('SecondaryDNS')
    """The value of this property shall be the IPv6 or IPv4 address of the
       secondary DNS server for the iSCSI boot initiator
    """

    ip_mask_dns_via_dhcp = base.Field('IPMaskDNSViaDHCP', adapter=bool)
    """The value of this property shall be a boolean indicating whether the
       iSCSI boot initiator uses DHCP to obtain the iniator name, IP address,
       and netmask
    """

    router_advertisement_enabled = base.Field(
        'RouterAdvertisementEnabled', adapter=bool)
    """The value of this property shall be a boolean indicating whether IPv6
       router advertisement is enabled for the iSCSI boot target.  This
       setting shall only apply to IPv6 configurations.
    """

    authentication_method = base.Field('AuthenticationMethod')
    """The value of this property shall be the iSCSI boot authentication
       method for this network device function
    """

    chap_username = base.Field('CHAPUsername')
    """The value of this property shall be username for CHAP authentication"""

    chap_secret = base.Field('CHAPSecret')
    """The value of this property shall be the shared secret for CHAP
       authentication
    """

    mutual_chap_username = base.Field('MutualCHAPUsername')
    """The value of this property shall be the CHAP Username for 2-way CHAP
       authentication
    """

    mutual_chap_secret = base.Field('MutualCHAPSecret')
    """The value of this property shall be the CHAP Secret for 2-way CHAP
       authentication
    """


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class NetworkDeviceFunction(base.ResourceBase):

    name = base.Field('Name')
    """The NetworkDeviceFunction name"""

    identity = base.Field('Id', required=True)
    """The NetworkDeviceFunction identity string"""

    description = base.Field('Description')
    """The description of NetworkDeviceFunction"""

    device_enabled = base.Field('DeviceEnabled', adapter=bool)
    """Whether the network device function is enabled"""

    ethernet = EthernetField('Ethernet')
    """This object shall contain Ethernet capabilities for this network
       device function
    """

    iscsi_boot = iSCSIBootField('iSCSIBoot')
    """This object shall contain iSCSI boot capabilities, status, and
       configuration values for this network device function
    """

    status = StatusField('Status')
    """The NetworkDeviceFunction status"""

    links = base.Field('Links')
    """Links for this NetworkDeviceFunction"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a NetworkDeviceFunction

        :param connector: A Connector instance
        :param identity: The identity of the NetworkDeviceFunction
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(NetworkDeviceFunction, self).__init__(
            connector, identity, redfish_version)

    def update(self, ethernet=None, iscsi_boot=None):
        """Enable iSCSI boot of compute node

        :param ethernet: Ethernet capabilities for this network device function
        :param iscsi_boot: iSCSI boot capabilities, status, and configuration
                           values for this network device function
        """
        data = {}
        if ethernet is not None:
            data['Ethernet'] = ethernet
        if iscsi_boot is not None:
            data['iSCSIBoot'] = iscsi_boot

        self._conn.patch(self.path, data=data)


class NetworkDeviceFunctionCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return NetworkDeviceFunction

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a NetworkDeviceFunctionCollection

        :param connector: A Connector instance
        :param path: The canonical path to the NetworkDeviceFunction collection
                     resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(NetworkDeviceFunctionCollection, self).__init__(
            connector, path, redfish_version)
