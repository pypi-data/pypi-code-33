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
from sushy import utils

from rsd_lib import utils as rsd_lib_utils


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class TemperaturesField(base.ListField):
    name = base.Field('Name')
    """The temperature sensor name"""

    member_id = base.Field('MemberId')
    """The temperature sensor member identity"""

    status = StatusField('Status')
    """The temperature sensor status"""

    sensor_number = base.Field(
        'SensorNumber', adapter=rsd_lib_utils.num_or_none)
    """A numerical identifier to represent the temperature sensor"""

    reading_celsius = base.Field(
        'ReadingCelsius', adapter=rsd_lib_utils.num_or_none)
    """The current value of the Temperature sensor"""

    upper_threshold_non_critical = base.Field(
        'UpperThresholdNonCritical', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the CurrentReading is above
       the normal range but is not critical. Units shall use the same units
       as the related ReadingVolts property.
    """

    upper_threshold_critical = base.Field(
        'UpperThresholdCritical', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the CurrentReading is above
       the normal range but is not yet fatal. Units shall use the same units
       as the related ReadingVolts property.
    """

    upper_threshold_fatal = base.Field(
        'UpperThresholdFatal', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the CurrentReading is above
       the normal range and is fatal. Units shall use the same units as the
       related ReadingVolts property.
    """

    lower_threshold_non_critical = base.Field(
        'LowerThresholdNonCritical', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the CurrentReading is below
       the normal range but is not critical. Units shall use the same units
       as the related ReadingVolts property.
    """

    lower_threshold_critical = base.Field(
        'LowerThresholdCritical', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the CurrentReading is below
       the normal range but is not yet fatal. Units shall use the same units
       as the related ReadingVolts property.
    """

    lower_threshold_fatal = base.Field(
        'LowerThresholdFatal', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the CurrentReading is below
       the normal range and is fatal. Units shall use the same units as the
       related ReadingVolts property.
    """

    min_reading_range = base.Field(
        'MinReadingRange', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the lowest possible value
       for CurrentReading. Units shall use the same units as the related
       ReadingVolts property.
    """

    max_reading_range = base.Field(
        'MaxReadingRange', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the highest possible value
       for CurrentReading. Units shall use the same units as the related
       ReadingVolts property.
    """

    physical_context = base.Field('PhysicalContext')
    """Describes the area or device to which this temperature measurement
       applies
    """

    related_item = base.Field(
        'RelatedItem', adapter=utils.get_members_identities)
    """Describes the areas or devices to which this temperature measurement
       applies
    """


class FansField(base.ListField):
    name = base.Field('Name')
    """The fan sensor name"""

    member_id = base.Field('MemberId')
    """The fan sensor member identity"""

    status = StatusField('Status')
    """The fan sensor status"""

    sensor_number = base.Field(
        'SensorNumber', adapter=rsd_lib_utils.num_or_none)
    """A numerical identifier to represent the fan sensor"""

    reading = base.Field('Reading', adapter=rsd_lib_utils.num_or_none)
    """The current value of the fan sensor"""

    reading_units = base.Field('ReadingUnits')
    """The value of this property shall be the units in which the fan's
       reading and thresholds are measured.
    """

    upper_threshold_non_critical = base.Field(
        'UpperThresholdNonCritical', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the CurrentReading is above
       the normal range but is not critical. The units shall be the same units
       as the related Reading property.
    """

    upper_threshold_critical = base.Field(
        'UpperThresholdCritical', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the CurrentReading is above
       the normal range but is not yet fatal. Units shall use the same units
       as the related Reading property.
    """

    upper_threshold_fatal = base.Field(
        'UpperThresholdFatal', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the CurrentReading is above
       the normal range and is fatal. Units shall use the same units as the
       related Reading property.
    """

    lower_threshold_non_critical = base.Field(
        'LowerThresholdNonCritical', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the CurrentReading is below
       the normal range but is not critical. Units shall use the same units
       as the related Reading property.
    """

    lower_threshold_critical = base.Field(
        'LowerThresholdCritical', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the CurrentReading is below
       the normal range but is not yet fatal. Units shall use the same units
       as the related Reading property.
    """

    lower_threshold_fatal = base.Field(
        'LowerThresholdFatal', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the CurrentReading is below
       the normal range and is fatal. Units shall use the same units as the
       related Reading property.
    """

    min_reading_range = base.Field(
        'MinReadingRange', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the lowest possible value
       for CurrentReading. Units shall use the same units as the related
       Reading property.
    """

    max_reading_range = base.Field(
        'MaxReadingRange', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall indicate the highest possible value
       for CurrentReading. Units shall use the same units as the related
       Reading property.
    """

    physical_context = base.Field('PhysicalContext')
    """Describes the area or device to which this fan measurement
       applies
    """

    related_item = base.Field(
        'RelatedItem', adapter=utils.get_members_identities)
    """Describes the areas or devices to which this fan measurement
       applies
    """

    redundancy = base.Field(
        'Redundancy', adapter=utils.get_members_identities)
    """The values of the properties in this array shall be used to show
       redundancy for fans and other elements in this resource.  The use of
       IDs within these arrays shall reference the members of the redundancy
       groups.
    """


class RedundancyField(base.ListField):
    name = base.Field('Name')
    """The Redundant device name"""

    member_id = base.Field('MemberId')
    """The Redundant device identity"""

    status = StatusField('Status')
    """The Redundant device status"""

    mode = base.Field('Mode')
    """This is the redundancy mode of the group"""

    max_num_supported = base.Field(
        'MaxNumSupported', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall contain the maximum number of
       members allowed in the redundancy group.
    """

    min_num_needed = base.Field(
        'MinNumNeeded', adapter=rsd_lib_utils.num_or_none)
    """The value of this property shall contain the minimum number of members
       allowed in the redundancy group for the current redundancy mode to
       still be fault tolerant.
    """

    redundancy_set = base.Field(
        'RedundancySet', adapter=utils.get_members_identities)
    """The value of this property shall contain the ids of components that
       are part of this redundancy set. The id values may or may not be
       dereferenceable.
    """

    redundancy_enabled = base.Field(
        'RedundancyEnabled', adapter=bool)
    """The value of this property shall be a boolean indicating whether the
       redundancy is enabled.
    """


class Thermal(base.ResourceBase):
    identity = base.Field('Id', required=True)
    """The Power identity string"""

    name = base.Field('Name')
    """The Power name"""

    description = base.Field('Description')
    """The Power description"""

    temperatures = TemperaturesField('Temperatures')
    """The details of temperatures senor"""

    fans = FansField('Fans')
    """The details of fans"""

    redundancy = RedundancyField('Redundancy')
    """Redundancy information for the power subsystem of this system or
       device
    """
