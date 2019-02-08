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


class ReceivedField(base.CompositeField):
    packets = base.Field('Packets', adapter=rsd_lib_utils.num_or_none)
    dropped_packets = base.Field('DroppedPackets',
                                 adapter=rsd_lib_utils.num_or_none)
    error_packets = base.Field('ErrorPackets',
                               adapter=rsd_lib_utils.num_or_none)
    broadcast_packets = base.Field('BroadcastPackets',
                                   adapter=rsd_lib_utils.num_or_none)
    multicast_packets = base.Field('MulticastPackets',
                                   adapter=rsd_lib_utils.num_or_none)
    errors = base.Field('Errors', adapter=rsd_lib_utils.num_or_none)
    received_bytes = base.Field('Bytes', adapter=rsd_lib_utils.num_or_none)


class TransmittedField(base.CompositeField):
    packets = base.Field('Packets', adapter=rsd_lib_utils.num_or_none)
    dropped_packets = base.Field('DroppedPackets',
                                 adapter=rsd_lib_utils.num_or_none)
    error_packets = base.Field('ErrorPackets',
                               adapter=rsd_lib_utils.num_or_none)
    broadcast_packets = base.Field('BroadcastPackets',
                                   adapter=rsd_lib_utils.num_or_none)
    multicast_packets = base.Field('MulticastPackets',
                                   adapter=rsd_lib_utils.num_or_none)
    errors = base.Field('Errors', adapter=rsd_lib_utils.num_or_none)
    transmitted_bytes = base.Field('Bytes', adapter=rsd_lib_utils.num_or_none)


class PortMetrics(base.ResourceBase):
    name = base.Field('Name')
    """The metrics name"""

    identity = base.Field('Id')
    """The metrics identity"""

    received = ReceivedField('Received')
    """The received packets status"""

    transmitted = TransmittedField('Transmitted')
    """The transmitted packets status"""

    collisions = base.Field('Collisions', adapter=rsd_lib_utils.num_or_none)
    """The collisions status"""
