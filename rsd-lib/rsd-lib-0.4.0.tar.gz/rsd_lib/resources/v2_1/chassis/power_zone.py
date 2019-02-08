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


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class RackLocationField(base.CompositeField):
    rack_units = base.Field('RackUnits')
    """Indicates the rack unit type"""

    xlocation = base.Field('XLocation', adapter=rsd_lib_utils.num_or_none)
    """The horizontal location within uLocation, from left to right
       (1.. MAXIMUM) 0 indicate not available
    """

    ulocation = base.Field('ULocation', adapter=rsd_lib_utils.num_or_none)
    """The index of the top-most U of the component, from top to bottom
       (1.. MAXIMUM) 0 indicate not available
    """

    uheight = base.Field('UHeight', adapter=rsd_lib_utils.num_or_none)
    """The height of managed zone, e.g. 8 for 8U, 16 for 16U"""


class PowerSuppliesField(base.ListField):
    name = base.Field('Name')
    """The Power Supply name"""

    power_capacity_watts = base.Field(
        'PowerCapacityWatts', adapter=rsd_lib_utils.num_or_none)
    """The maximum capacity of this Power Supply"""

    last_power_output_watts = base.Field(
        'LastPowerOutputWatts', adapter=rsd_lib_utils.num_or_none)
    """The average power output of this Power Supply"""

    manufacturer = base.Field('Manufacturer')
    """The manufacturer of this Power Supply"""

    model_number = base.Field('ModelNumber')
    """The model number for this Power Supply"""

    firmware_revision = base.Field('FirmwareRevision')
    """The firmware version for this Power Supply"""

    serial_number = base.Field('SerialNumber')
    """The serial number for this Power Supply"""

    part_number = base.Field('PartNumber')
    """The part number for this Power Supply"""

    status = StatusField('Status')
    """The Power supply status"""

    rack_location = RackLocationField('RackLocation')
    """The PowerZone physical location"""


class PowerZone(base.ResourceBase):
    identity = base.Field('Id', required=True)
    """The PowerZone identity string"""

    name = base.Field('Name')
    """The PowerZone name"""

    description = base.Field('Description')
    """The PowerZone description"""

    status = StatusField('Status')
    """The PowerZone status"""

    rack_location = RackLocationField('RackLocation')
    """The PowerZone physical location"""

    max_psus_supported = base.Field(
        'MaxPSUsSupported', adapter=rsd_lib_utils.num_or_none)
    """The maximum number of Power Supply Units supported by PowerZone"""

    presence = base.Field('Presence')
    """Indicates the aggregated Power Supply Unit presence information
       Aggregated Power Supply Unit presence format: Length of string indicate
       total slot of Power Supply Units in PowerZone.

       For each byte the string:
       "1" means present
       "0" means not present
    """

    number_of_psus_present = base.Field(
        'NumberOfPSUsPresent', adapter=rsd_lib_utils.num_or_none)
    """Indicates the number of existing Power Supply Units in PowerZone"""

    power_consumed_watts = base.Field(
        'PowerConsumedWatts', adapter=rsd_lib_utils.num_or_none)
    """The total power consumption of PowerZone, sum of trays'
       power consumption
    """

    power_output_watts = base.Field(
        'PowerOutputWatts', adapter=rsd_lib_utils.num_or_none)
    """The total power production of PowerZone, sum of PSUs' output"""

    power_capacity_watts = base.Field(
        'PowerCapacityWatts', adapter=rsd_lib_utils.num_or_none)
    """The maximum power capacity supported by PowerZone"""

    power_supplies = PowerSuppliesField('PowerSupplies')
    """Details of the power supplies associated with this system or device"""


class PowerZoneCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return PowerZone

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a PowerZone Collection

        :param connector: A Connector instance
        :param path: The canonical path to the power zone collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(PowerZoneCollection, self).__init__(connector,
                                                  path,
                                                  redfish_version)
