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

from rsd_lib.resources.v2_3.fabric import endpoint
from rsd_lib.resources.v2_3.storage_service import drive
from rsd_lib.resources.v2_3.storage_service import storage_pool
from rsd_lib.resources.v2_3.storage_service import volume

LOG = logging.getLogger(__name__)


class StatusField(base.CompositeField):
    state = base.Field('State')
    health = base.Field('Health')
    health_rollup = base.Field('HealthRollup')


class StorageService(base.ResourceBase):

    description = base.Field('Description')
    """The storage service description"""

    identity = base.Field('Id', required=True)
    """The storage service identity string"""

    name = base.Field('Name')
    """The storage service name"""

    status = StatusField('Status')
    """The storage service status"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a StorageService

        :param connector: A Connector instance
        :param identity: The identity of the StorageService resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(StorageService, self).__init__(connector, identity,
                                             redfish_version)

    def _get_volume_collection_path(self):
        """Helper function to find the VolumeCollection path"""
        return utils.get_sub_resource_path_by(self, 'Volumes')

    @property
    @utils.cache_it
    def volumes(self):
        """Property to provide reference to `VolumeCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return volume.VolumeCollection(
            self._conn, self._get_volume_collection_path(),
            redfish_version=self.redfish_version)

    def _get_storage_pool_collection_path(self):
        """Helper function to find the StoragePoolCollection path"""
        return utils.get_sub_resource_path_by(self, 'StoragePools')

    @property
    @utils.cache_it
    def storage_pools(self):
        """Property to provide reference to `StoragePoolCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return storage_pool.StoragePoolCollection(
            self._conn, self._get_storage_pool_collection_path(),
            redfish_version=self.redfish_version)

    def _get_drive_collection_path(self):
        """Helper function to find the DriveCollection path"""
        return utils.get_sub_resource_path_by(self, 'Drives')

    @property
    @utils.cache_it
    def drives(self):
        """Property to provide reference to `DriveCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return drive.DriveCollection(
            self._conn, self._get_drive_collection_path(),
            redfish_version=self.redfish_version)

    def _get_endpoint_collection_path(self):
        """Helper function to find the EndpointCollection path"""
        return utils.get_sub_resource_path_by(self, 'Endpoints')

    @property
    @utils.cache_it
    def endpoints(self):
        """Property to provide reference to `EndpointCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return endpoint.EndpointCollection(
            self._conn, self._get_endpoint_collection_path(),
            redfish_version=self.redfish_version)


class StorageServiceCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return StorageService

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a StorageServiceCollection

        :param connector: A Connector instance
        :param path: The canonical path to the StorageService collection
            resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(StorageServiceCollection, self).__init__(connector, path,
                                                       redfish_version)
