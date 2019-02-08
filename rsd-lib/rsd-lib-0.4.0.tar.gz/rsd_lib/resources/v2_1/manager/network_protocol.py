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

from rsd_lib import utils as rsd_lib_utils
from sushy.resources import base


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class ProtocolField(base.CompositeField):
    protocol_enables = base.Field('ProtocolEnabled')
    """Whether the protocol is enabled"""

    port = base.Field('Port', adapter=rsd_lib_utils.num_or_none)
    """The port of all protocol"""


class SSDPField(ProtocolField):
    notify_multicast_interval_seconds = base.Field(
        'NotifyMulticastIntervalSeconds',
        adapter=rsd_lib_utils.num_or_none)
    """The NotifyMulticast interval time"""

    notify_ttl = base.Field(
        'NotifyTTL',
        adapter=rsd_lib_utils.num_or_none)
    """The notify ttl"""

    notify_ipv6_scope = base.Field('NotifyIPv6Scope')
    """The NotifyIPv6Scope"""


class NetworkProtocol(base.ResourceBase):
    identify = base.Field('Id', required=True)
    """The NetworkProtocol identity string"""

    name = base.Field('Name')
    """The NetworkProtocol identity string"""

    description = base.Field('Description')
    """The NetworkProtocol description"""

    status = StatusField('Status')
    """The NetworkProtocol Status"""

    hostname = base.Field('HostName')
    """The NetworkProtocol Hostname"""

    fqdn = base.Field('FQDN')
    """The NetworkProtocol FQDN"""

    http = ProtocolField('HTTP')
    """The HTTP protocol"""

    https = ProtocolField('HTTPS')
    """The HTTPS protocol"""

    ipmi = ProtocolField('IPMI')
    """The IPMI protocol"""

    ssh = ProtocolField('SSH')
    """The SSH protocol"""

    snmp = ProtocolField('SNMP')
    """The SNMP protocol"""

    virtual_media = ProtocolField('VirtualMedia')
    """The VirtualMedia protocol"""

    ssdp = SSDPField('SSDP')
    """The SSDP protocol"""

    telnet = ProtocolField('Telnet')
    """The Telnet protocol"""

    kvm_ip = ProtocolField('KVMIP')
    """The KVMIP protocol"""
