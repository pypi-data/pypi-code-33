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


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class LinksField(base.CompositeField):
    chassis = base.Field('Chassis', adapter=utils.get_members_identities)
    """The value of this property shall reference a resource of type Chassis
       that represents the physical container associated with this resource.
    """

    pcie_functions = base.Field(
        'PCIeFunctions', adapter=utils.get_members_identities)
    """The value of this property shall be a reference to the resources that
       this device exposes and shall reference a resource of type PCIeFunction.
    """


class PCIeDevice(base.ResourceBase):
    identity = base.Field('Id', required=True)
    """The PCIe device identity string"""

    name = base.Field('Name')
    """The PCIe device name"""

    description = base.Field('Description')
    """The PCIe device description"""

    manufacturer = base.Field('Manufacturer')
    """The PCIe device manufacturer"""

    model = base.Field('Model')
    """The PCIe device Model"""

    sku = base.Field('SKU')
    """The PCIe device stock-keeping unit"""

    serial_number = base.Field('SerialNumber')
    """The PCIe device serial number"""

    part_number = base.Field('PartNumber')
    """The PCIe device part number"""

    asset_tag = base.Field('AssetTag')
    """The user assigned asset tag for this PCIe device"""

    device_type = base.Field('DeviceType')
    """The device type for this PCIe device"""

    firmware_version = base.Field('FirmwareVersion')
    """The version of firmware for this PCIe device"""

    status = StatusField('Status')
    """The PCIe device status"""

    links = LinksField('Links')
    """The link section of PCIe device"""

    def update(self, asset_tag=None):
        """Update AssetTag properties

        :param asset_tag: The user assigned asset tag for this PCIe device
        """

        data = {'AssetTag': asset_tag}

        self._conn.patch(self.path, data=data)
