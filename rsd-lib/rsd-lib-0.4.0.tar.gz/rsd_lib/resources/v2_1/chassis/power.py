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


class PowerMetricsField(base.CompositeField):
    interval_in_min = base.Field(
        'IntervalInMin', adapter=rsd_lib_utils.num_or_none)
    """The time interval (or window) in which the PowerMetrics are
       measured over
    """

    min_consumed_watts = base.Field(
        'MinConsumedWatts', adapter=rsd_lib_utils.num_or_none)
    """The lowest power consumption level over the measurement window
       (the last IntervalInMin minutes)
    """

    max_consumed_watts = base.Field(
        'MaxConsumedWatts', adapter=rsd_lib_utils.num_or_none)
    """The highest power consumption level that has occured over the
       measurement window (the last IntervalInMin minutes)
    """

    average_consumed_watts = base.Field(
        'AverageConsumedWatts', adapter=rsd_lib_utils.num_or_none)
    """The average power level over the measurement window
       (the last IntervalInMin minutes)
    """


class PowerLimitField(base.CompositeField):
    limit_in_watts = base.Field(
        'LimitInWatts', adapter=rsd_lib_utils.num_or_none)
    """The Power limit in watts. Set to null to disable power capping"""

    limit_exception = base.Field('LimitException')
    """The action that is taken if the power cannot be maintained below
       the LimitInWatts
    """

    correction_in_ms = base.Field(
        'CorrectionInMs', adapter=rsd_lib_utils.num_or_none)
    """The time required for the limiting process to reduce power consumption
       to below the limit
    """


class PowerControlField(base.ListField):
    name = base.Field('Name')
    """The Power Control name"""

    member_id = base.Field('MemberId')
    """The Power Control member identity"""

    power_consumed_watts = base.Field(
        'PowerConsumedWatts', adapter=rsd_lib_utils.num_or_none)
    """The actual power being consumed by the chassis"""

    power_requested_watts = base.Field(
        'PowerRequestedWatts', adapter=rsd_lib_utils.num_or_none)
    """The potential power that the chassis resources are requesting which
       may be higher than the current level being consumed since requested
       power includes budget that the chassis resource wants for future use
    """

    power_available_watts = base.Field(
        'PowerAvailableWatts', adapter=rsd_lib_utils.num_or_none)
    """The amount of power not already budgeted and therefore available for
       additional allocation. (powerCapacity - powerAllocated).  This
       indicates how much reserve power capacity is left.
    """

    power_capacity_watts = base.Field(
        'PowerCapacityWatts', adapter=rsd_lib_utils.num_or_none)
    """The total amount of power available to the chassis for allocation.
       This may the power supply capacity, or power budget assigned to the
       chassis from an up-stream chassis.
    """

    power_allocated_watts = base.Field(
        'PowerAllocatedWatts', adapter=rsd_lib_utils.num_or_none)
    """The total amount of power that has been allocated (or budegeted) to
       chassis resources
    """

    status = StatusField('Status')
    """The Power Control status"""

    power_metrics = PowerMetricsField('PowerMetrics')
    """Power readings for this chassis"""

    power_limit = PowerLimitField('PowerLimit')
    """Power limit status and configuration information for this chassis"""

    related_item = base.Field(
        'RelatedItem', adapter=utils.get_members_identities)
    """The ID(s) of the resources associated with this Power Limit"""


class VoltageField(base.ListField):
    name = base.Field('Name')
    """The Voltage sensor name"""

    member_id = base.Field('MemberId')
    """The Voltage sensor member identity"""

    status = StatusField('Status')
    """The Voltage sensor status"""

    sensor_number = base.Field(
        'SensorNumber', adapter=rsd_lib_utils.num_or_none)
    """A numerical identifier to represent the voltage sensor"""

    reading_volts = base.Field(
        'ReadingVolts', adapter=rsd_lib_utils.num_or_none)
    """The current value of the voltage sensor"""

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
    """Describes the area or device to which this voltage measurement
       applies
    """

    related_item = base.Field(
        'RelatedItem', adapter=utils.get_members_identities)
    """Describes the areas or devices to which this voltage measurement
       applies
    """


class InputRangesField(base.ListField):
    input_type = base.Field('InputType')
    """This property shall contain the input type (AC or DC) of the
       associated range.
    """

    minimum_voltage = base.Field(
        'MinimumVoltage', adapter=rsd_lib_utils.num_or_none)
    """This property shall contain the value in Volts of the minimum line
       input voltage which the power supply is capable of consuming for
       this range.
    """

    maximum_voltage = base.Field(
        'MaximumVoltage', adapter=rsd_lib_utils.num_or_none)
    """This property shall contain the value in Volts of the maximum line
       input voltage which the power supply is capable of consuming for
       this range.
    """

    minimum_frequency_hz = base.Field(
        'MinimumFrequencyHz', adapter=rsd_lib_utils.num_or_none)
    """This property shall contain the value in Hertz of the minimum line
       input frequency which the power supply is capable of consuming for
       this range.
    """

    maximum_frequency_hz = base.Field(
        'MaximumFrequencyHz', adapter=rsd_lib_utils.num_or_none)
    """This property shall contain the value in Hertz of the maximum line
       input frequency which the power supply is capable of consuming for
       this range.
    """

    output_wattage = base.Field(
        'OutputWattage', adapter=rsd_lib_utils.num_or_none)
    """This property shall contiain the maximum amount of power, in Watts,
       that the associated power supply is rated to deliver while operating
       in this input range.
    """


class PowerSuppliesField(base.ListField):
    name = base.Field('Name')
    """The Power Supply name"""

    member_id = base.Field('MemberId')
    """The Power Supply member identity"""

    status = StatusField('Status')
    """The Power Supply status"""

    power_supply_type = base.Field('PowerSupplyType')
    """This property shall contain the input power type (AC or DC) of the
       associated power supply
    """

    line_input_voltage_type = base.Field('LineInputVoltageType')
    """This property shall contain the type of input line voltage supported
       by the associated power supply
    """

    line_input_voltage = base.Field(
        'LineInputVoltage', adapter=rsd_lib_utils.num_or_none)
    """This property shall contain the value in Volts of the line input
       voltage (measured or configured for) that the power supply has been
       configured to operate with or is currently receiving.
    """

    power_capacity_watts = base.Field(
        'PowerCapacityWatts', adapter=rsd_lib_utils.num_or_none)
    """This property shall contiain the maximum amount of power, in Watts,
       that the associated power supply is rated to deliver.
    """

    last_power_output_watts = base.Field(
        'LastPowerOutputWatts', adapter=rsd_lib_utils.num_or_none)
    """This property shall contain the average power output, measured in
       Watts, of the associated power supply.
    """

    model = base.Field('Model')
    """This property shall contain the model information as defined by the
       manufacturer for the associated power supply.
    """

    manufacturer = base.Field('Manufacturer')
    """The manufacturer for this Power Supply"""

    firmware_version = base.Field('FirmwareVersion')
    """This property shall contain the firwmare version as defined by the
       manufacturer for the associated power supply.
    """

    serial_number = base.Field('SerialNumber')
    """This property shall contain the serial number as defined by the
       manufacturer for the associated power supply.
    """

    part_number = base.Field('PartNumber')
    """This property shall contain the part number as defined by the
       manufacturer for the associated power supply.
    """

    spare_part_number = base.Field('SparePartNumber')
    """This property shall contain the spare or replacement part number as
       defined by the manufacturer for the associated power supply.
    """

    related_item = base.Field(
        'RelatedItem', adapter=utils.get_members_identities)
    """The ID(s) of the resources associated with this Power Limit"""

    redundancy = base.Field(
        'Redundancy', adapter=utils.get_members_identities)
    """The values of the properties in this array shall be used to show
       redundancy for power supplies and other elements in this resource.
       The use of IDs within these arrays shall reference the members of the
       redundancy groups.
    """

    input_ranges = InputRangesField('InputRanges')
    """This is the input ranges that the power supply can use"""

    indicator_led = base.Field('IndicatorLED')
    """The value of this property shall contain the indicator light state for
       the indicator light associated with this power supply.
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


class Power(base.ResourceBase):
    identity = base.Field('Id', required=True)
    """The Power identity string"""

    name = base.Field('Name')
    """The Power name"""

    description = base.Field('Description')
    """The Power description"""

    power_control = PowerControlField('PowerControl')
    """The details of power control function"""

    voltages = VoltageField('Voltages')
    """The details of voltage sensors"""

    power_supplies = PowerSuppliesField('PowerSupplies')
    """Details of the power supplies associated with this system or device"""

    redundancy = RedundancyField('Redundancy')
    """Redundancy information for the power subsystem of this system or
       device
    """
