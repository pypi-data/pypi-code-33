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

from sushy import exceptions

from rsd_lib.resources.v2_3.storage_service import volume


class Volume(volume.Volume):

    def resize(self, num_bytes):
        """Update volume properties

        :param num_bytes: size in bytes of new resized volume
        """
        if not isinstance(num_bytes, int):
            raise exceptions.InvalidParameterValueError(
                parameter='num_bytes', value=num_bytes,
                valid_values='integer')

        if self.capacity_bytes and num_bytes <= self.capacity_bytes:
            raise exceptions.InvalidParameterValueError(
                parameter='num_bytes', value=num_bytes,
                valid_values='> {0}'.format(self.capacity_bytes))

        data = {"Capacity": {"Data": {'AllocatedBytes': num_bytes}}}
        self._conn.patch(self.path, data=data)


class VolumeCollection(volume.VolumeCollection):

    @property
    def _resource_type(self):
        return Volume

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a VolumeCollection

        :param connector: A Connector instance
        :param path: The canonical path to the Volume collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(VolumeCollection, self).__init__(connector, path,
                                               redfish_version)
