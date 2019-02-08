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

import logging

from sushy.resources import base
from sushy import utils

from rsd_lib.resources.v2_3.storage_service import volume
from rsd_lib import utils as rsd_lib_utils


LOG = logging.getLogger(__name__)


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class CapacityField(base.CompositeField):
    allocated_bytes = base.Field(['Data', 'AllocatedBytes'],
                                 adapter=rsd_lib_utils.num_or_none)
    consumed_bytes = base.Field(['Data', 'ConsumedBytes'],
                                adapter=rsd_lib_utils.num_or_none)
    guaranteed_bytes = base.Field(['Data', 'GuaranteedBytes'],
                                  adapter=rsd_lib_utils.num_or_none)
    provisioned_bytes = base.Field(['Data', 'ProvisionedBytes'],
                                   adapter=rsd_lib_utils.num_or_none)


class CapacitySourcesField(base.ListField):
    providing_drives = base.Field('ProvidingDrives', default=(),
                                  adapter=utils.get_members_identities)
    provided_capacity = CapacityField('ProvidedCapacity')


class IdentifierField(base.CompositeField):
    durable_name = base.Field('DurableName')
    durable_name_format = base.Field('DurableNameFormat')


class StoragePool(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The storage pool  identity string"""

    description = base.Field('Description')
    """The storage pool  description string"""

    name = base.Field('Name')
    """The storage pool  name string"""

    status = StatusField('Status')
    """The storage pool  status"""

    capacity = CapacityField('Capacity')
    """The storage pool capacity info"""

    capacity_sources = CapacitySourcesField('CapacitySources')
    """The storage pool capacity source info"""

    identifier = IdentifierField('Identifier')
    """These identifiers list of this volume"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a LogicalDrive

        :param connector: A Connector instance
        :param identity: The identity of the LogicalDrive resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(StoragePool, self).__init__(connector, identity, redfish_version)

    def _get_allocated_volumes_path(self):
        """Helper function to find the AllocatedVolumes path"""
        return utils.get_sub_resource_path_by(self, 'AllocatedVolumes')

    @property
    @utils.cache_it
    def allocated_volumes(self):
        """Property to provide reference to `AllocatedVolumes` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return volume.VolumeCollection(
            self._conn, self._get_allocated_volumes_path(),
            redfish_version=self.redfish_version)

    def _get_allocated_pools_path(self):
        """Helper function to find the AllocatedPools path"""
        return utils.get_sub_resource_path_by(self, 'AllocatedPools')

    @property
    @utils.cache_it
    def allocated_pools(self):
        """Property to provide reference to `AllocatedPools` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return StoragePoolCollection(
            self._conn, self._get_allocated_pools_path(),
            redfish_version=self.redfish_version)


class StoragePoolCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return StoragePool

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a StoragePoolCollection

        :param connector: A Connector instance
        :param path: The canonical path to the StoragePool collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(StoragePoolCollection, self).__init__(connector, path,
                                                    redfish_version)
