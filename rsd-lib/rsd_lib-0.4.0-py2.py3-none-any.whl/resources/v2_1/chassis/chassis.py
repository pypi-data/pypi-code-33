# Copyright 2017 Intel, Inc.
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

from rsd_lib.resources.v2_1.chassis import pcie_device
from rsd_lib.resources.v2_1.chassis import power
from rsd_lib.resources.v2_1.chassis import power_zone
from rsd_lib.resources.v2_1.chassis import thermal
from rsd_lib.resources.v2_1.chassis import thermal_zone
from rsd_lib import utils as rsd_lib_utils


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class LinksField(base.CompositeField):
    contains = base.Field('Contains', adapter=utils.get_members_identities)
    """Any other chassis that this chassis has in it"""

    contained_by = base.Field('ContainedBy',
                              adapter=rsd_lib_utils.get_resource_identity)
    """The resource that represents the chassis that contains this chassis
       and shall be of type Chassis
    """

    computer_systems = base.Field('ComputerSystems',
                                  adapter=utils.get_members_identities)
    """The computer systems contained in this chassis"""

    managed_by = base.Field('ManagedBy', adapter=utils.get_members_identities)
    """The managers contained in this chassis"""

    managers_in_chassis = base.Field('ManagersInChassis',
                                     adapter=utils.get_members_identities)
    """The managers located in this chassis"""

    switches = base.Field(['Oem', 'Intel_RackScale', 'Switches'],
                          adapter=utils.get_members_identities)
    """The Ethernet switches contained in this chassis"""


class LocationField(base.CompositeField):
    identity = base.Field('Id')
    """The location ID of the chassis"""

    parent_id = base.Field('ParentId')
    """The location ID of parent chassis"""


class OemField(base.CompositeField):
    location = LocationField('Location')
    """Property that shows this chassis ID and its parent"""

    rmm_present = base.Field('RMMPresent', adapter=bool)
    """RMM presence in a rack"""

    rack_supports_disaggregated_power_cooling = base.Field(
        'RackSupportsDisaggregatedPowerCooling', adapter=bool)
    """Indicates if Rack support is disaggregated (shared) power and cooling
       capabilities
    """

    uuid = base.Field('UUID')
    """Chassis unique ID"""

    geo_tag = base.Field('GeoTag')
    """Provides info about the geographical location of this chassis"""


class Chassis(base.ResourceBase):
    identity = base.Field('Id', required=True)
    """The chassis identity string"""

    asset_tag = base.Field('AssetTag')
    """The chassis asset tag"""

    description = base.Field('Description')
    """The chassis description"""

    manufacturer = base.Field('Manufacturer')
    """The chassis manufacturer"""

    name = base.Field('Name')
    """The chassis name"""

    model = base.Field('Model')
    """The chassis Model"""

    indicator_led = base.Field('IndicatorLED')
    """The state of the indicator LED, used to identify the chassis"""

    part_number = base.Field('PartNumber')
    """The chassis part number"""

    serial_number = base.Field('SerialNumber')
    """The chassis serial number"""

    sku = base.Field('SKU')
    """The chassis stock-keeping unit"""

    status = StatusField('Status')
    """The chassis status"""

    chassis_type = base.Field('ChassisType')
    """The chassis type"""

    oem = OemField(['Oem', 'Intel_RackScale'])
    """The chassis oem object"""

    links = LinksField('Links')
    """The link section of chassis"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a Chassis

        :param connector: A Connector instance
        :param identity: The identity of the chassis resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(Chassis, self).__init__(connector, identity, redfish_version)

    def _get_power_zone_collection_path(self):
        """Helper function to find the PowerZoneCollection path"""
        return utils.get_sub_resource_path_by(self, 'PowerZones')

    @property
    @utils.cache_it
    def power_zones(self):
        """Property to provide reference to `PowerZoneCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return power_zone.PowerZoneCollection(
            self._conn, self._get_power_zone_collection_path(),
            redfish_version=self.redfish_version)

    def _get_power_path(self):
        """Helper function to find the Power path"""
        return utils.get_sub_resource_path_by(self, 'Power')

    @property
    @utils.cache_it
    def power(self):
        """Property to provide reference to `Power` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return power.Power(
            self._conn, self._get_power_path(),
            redfish_version=self.redfish_version)

    def _get_thermal_zone_collection_path(self):
        """Helper function to find the ThermalZoneCollection path"""
        return utils.get_sub_resource_path_by(self, 'ThermalZones')

    @property
    @utils.cache_it
    def thermal_zones(self):
        """Property to provide reference to `ThermalZoneCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return thermal_zone.ThermalZoneCollection(
            self._conn, self._get_thermal_zone_collection_path(),
            redfish_version=self.redfish_version)

    def _get_thermal_path(self):
        """Helper function to find the Thermal path"""
        return utils.get_sub_resource_path_by(self, 'Thermal')

    @property
    @utils.cache_it
    def thermal(self):
        """Property to provide reference to `Thermal` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return thermal.Thermal(
            self._conn, self._get_thermal_path(),
            redfish_version=self.redfish_version)

    def update(self, asset_tag=None, location_id=None):
        """Update AssetTag and Location->Id properties

        :param asset_tag: The user assigned asset tag for this chassis
        :param location_id: The user assigned location id for this chassis.
                            It can be changed only for a Rack Chassis
        """

        data = {}

        if asset_tag is not None:
            data['AssetTag'] = asset_tag

        if location_id is not None:
            data['Oem'] = {
                "Intel_RackScale": {
                    "Location": {
                        "Id": location_id
                    }
                }
            }

        self._conn.patch(self.path, data=data)

    @property
    @utils.cache_it
    def pcie_devices(self):
        """Property to provide reference to a list of `PCIeDevice` instances

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        pcie_device_paths = rsd_lib_utils.get_sub_resource_path_list_by(
            self, ['Links', 'PCIeDevices'])
        return [
            pcie_device.PCIeDevice(
                self._conn, path, redfish_version=self.redfish_version
            ) for path in pcie_device_paths]


class ChassisCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Chassis

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a Chassis Collection

        :param connector: A Connector instance
        :param path: The canonical path to the chassis collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ChassisCollection, self).__init__(connector,
                                                path,
                                                redfish_version)
