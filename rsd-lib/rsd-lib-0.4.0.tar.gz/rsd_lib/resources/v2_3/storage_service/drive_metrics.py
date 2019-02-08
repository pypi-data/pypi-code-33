# Copyright (c) 2019 Intel, Corp.
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


class LifeTimeField(base.CompositeField):
    unit_size_bytes = base.Field('UnitSizeBytes',
                                 adapter=rsd_lib_utils.num_or_none)
    """The size of a unit in bytes used by UnitsRead and UnitsWritten"""

    units_read = base.Field('UnitsRead')
    """The number of units of a read since reset """

    units_written = base.Field('UnitsWritten')
    """The number of units of a written since reset"""

    host_read_commands = base.Field('HostReadCommands')
    """The number of read commands completed by the disk controller"""

    host_write_commands = base.Field('HostWriteCommands')
    """The number of write commands completed by the disk controller"""

    power_cycles = base.Field('PowerCycles')
    """The number of power cycels of this drive"""

    power_on_hours = base.Field('PowerOnHours')
    """The number of power-on hours of this drive"""

    controller_busy_time_minutes = base.Field('ControllerBusyTimeMinutes')
    """The amount of time in minutes the driver controller is busy"""


class HealthDataField(base.CompositeField):
    available_spare_percentage = base.Field('AvailableSparePercentage')
    """The percentage of the remaining spare capacity available"""

    predicted_media_life_used_percent = base.Field(
        'PredictedMediaLifeUsedPercent')
    """The percentage of life remaining in the driver's media"""

    unsafe_shutdowns = base.Field('UnsafeShutdowns')
    """The number of unsafe shutdowns of this drive"""

    media_errors = base.Field('MediaErrors')
    """The number of media and data integrity errors of this drive"""


class DriveMetrics(base.ResourceBase):

    name = base.Field('Name')
    """Drive metrics name"""

    identity = base.Field('Id')
    """Drive metrics id"""

    description = base.Field('Description')
    """Drive metrics description"""

    life_time = LifeTimeField('LifeTime')
    """The life time metrics for this drive"""

    health_data = HealthDataField('HealthData')
    """The health data metrics for this drive"""

    temperature_kelvin = base.Field('TemperatureKelvin')
    """The temperature in Kelvin degrees of this drive"""
