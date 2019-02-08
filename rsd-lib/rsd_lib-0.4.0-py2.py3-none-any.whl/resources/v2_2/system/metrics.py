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


class Metrics(base.ResourceBase):
    name = base.Field('Name')
    """The metrics name"""

    description = base.Field('Description')
    """The metrics description"""

    identity = base.Field('Id')
    """The metrics identity"""

    processor_bandwidth_percent = base.Field('ProcessorBandwidthPercent',
                                             adapter=rsd_lib_utils.num_or_none)
    """The processor bandwidth percent"""

    memory_bandwidth_percent = base.Field('MemoryBandwidthPercent',
                                          adapter=rsd_lib_utils.num_or_none)
    """The memory bandwidth percent"""

    memory_throttled_cycles_percent = base.Field(
        'MemoryThrottledCyclesPercent', adapter=rsd_lib_utils.num_or_none)
    """The memory throttled cycles percent"""

    processor_power_watt = base.Field('ProcessorPowerWatt',
                                      adapter=rsd_lib_utils.num_or_none)
    """The processor power watt"""

    memory_power_watt = base.Field('MemoryPowerWatt',
                                   adapter=rsd_lib_utils.num_or_none)
    """The memory power watt"""

    io_bandwidth_gbps = base.Field('IOBandwidthGBps',
                                   adapter=rsd_lib_utils.num_or_none)
    """The io bandwidth GBps"""

    health = base.Field('Health')
    """The detail health information"""
