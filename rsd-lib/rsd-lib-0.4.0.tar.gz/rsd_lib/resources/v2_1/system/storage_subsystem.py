# Copyright 2018 99cloud, Inc.
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


class IdentifiersField(base.ListField):
    durable_name = base.Field('DurableName')
    durable_name_format = base.Field('DurableNameFormat')


class StorageControllersField(base.ListField):
    member_id = base.Field('MemberId')
    status = StatusField('Status')
    manufacturer = base.Field('Manufacturer')
    model = base.Field('Model')
    sku = base.Field('SKU')
    serial_number = base.Field('SerialNumber')
    part_number = base.Field('PartNumber')
    asset_tag = base.Field('AssetTag')
    speed_gbps = base.Field('SpeedGbps', adapter=rsd_lib_utils.num_or_none)
    firmware_version = base.Field('FirmwareVersion')
    supported_controller_protocols = base.Field(
        'SupportedControllerProtocols')
    supported_device_protocols = base.Field(
        'SupportedDeviceProtocols')
    identifiers = IdentifiersField('Identifiers')


class StorageSubsystem(base.ResourceBase):

    name = base.Field('Name')
    """The storage subsystem name"""

    identity = base.Field('Id', required=True)
    """The storage subsystem identity string"""

    description = base.Field('Description')
    """The storage subsystem description"""

    status = StatusField('Status')
    """The storage subsystem status"""

    storage_controllers = StorageControllersField('StorageControllers')
    """The storage subsystem controllers"""

    drives = base.Field('Drives', adapter=utils.get_members_identities)
    """The storage subsystem drives"""

    volumes = base.Field('Volumes',
                         adapter=rsd_lib_utils.get_resource_identity)
    """The storage subsystem volumes"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a Storage Subsystem

        :param connector: A Connector instance
        :param identity: The identity of the storage subsystem
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(StorageSubsystem, self).__init__(connector,
                                               identity,
                                               redfish_version)


class StorageSubsystemCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return StorageSubsystem

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a StorageSubsystemCollection

        :param connector: A Connector instance
        :param path: The canonical path to the storage subsystem collection
            resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(StorageSubsystemCollection, self).__init__(connector,
                                                         path,
                                                         redfish_version)
