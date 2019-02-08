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


class LinksField(base.CompositeField):
    ethernet_interfaces = base.Field(
        'EthernetInterfaces', adapter=utils.get_members_identities)
    """The value of this property shall reference a resource of type
       EthernetInterface that represents the network interfaces associated
       with this resource.
    """

    drives = base.Field('Drives', adapter=utils.get_members_identities)
    """The value of this property shall reference a resource of type Drive
       that represents the storage drives associated with this resource.
    """

    storage_controllers = base.Field(
        'StorageControllers', adapter=utils.get_members_identities)
    """The value of this property shall reference a resource of type
       StorageController that represents the storage controllers associated
       with this resource.
    """

    pcie_device = base.Field(
        'PCIeDevice', adapter=rsd_lib_utils.get_resource_identity)
    """The value of this property shall be a reference to the resource that
       this function is a part of and shall reference a resource of
       type PCIeDevice.
    """


class PCIeFunction(base.ResourceBase):
    identity = base.Field('Id', required=True)
    """The PCIe function identity string"""

    name = base.Field('Name')
    """The PCIe function name"""

    description = base.Field('Description')
    """The PCIe function description"""

    function_id = base.Field('FunctionId', adapter=rsd_lib_utils.num_or_none)
    """The the PCIe Function identifier"""

    function_type = base.Field('FunctionType')
    """The type of the PCIe Function"""

    device_class = base.Field('DeviceClass')
    """The class for this PCIe Function"""

    device_id = base.Field('DeviceId')
    """The Device ID of this PCIe function"""

    vendor_id = base.Field('VendorId')
    """The Vendor ID of this PCIe function"""

    class_code = base.Field('ClassCode')
    """The Class Code of this PCIe function"""

    revision_id = base.Field('RevisionId')
    """The Revision ID of this PCIe function"""

    subsystem_id = base.Field('SubsystemId')
    """The Subsystem ID of this PCIe function"""

    subsystem_vendor_id = base.Field('SubsystemVendorId')
    """The Subsystem Vendor ID of this PCIe function"""

    status = StatusField('Status')
    """The PCIe function status"""

    links = LinksField('Links')
    """The link section of PCIe function"""
