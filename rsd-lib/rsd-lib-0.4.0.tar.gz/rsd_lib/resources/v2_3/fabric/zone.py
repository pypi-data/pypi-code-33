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

import logging

from rsd_lib.resources.v2_1.fabric import zone as v2_1_zone

LOG = logging.getLogger(__name__)


class Zone(v2_1_zone.Zone):

    def update(self, endpoints):
        """Add or remove Endpoints from a Zone

        User have to provide a full representation of Endpoints array. A
        partial update (single element update/append/detele) is not supported.
        :param endpoints: a full representation of Endpoints array
        """
        data = {"Links": {"Endpoints": []}}
        data['Links']['Endpoints'] = [
            {'@odata.id': endpoint} for endpoint in endpoints]

        self._conn.patch(self.path, data=data)

    def delete(self):
        """Delete this zone"""
        self._conn.delete(self.path)


class ZoneCollection(v2_1_zone.ZoneCollection):

    @property
    def _resource_type(self):
        return Zone

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a Zone Collection

        :param connector: A Connector instance
        :param path: The canonical path to the Zone collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ZoneCollection, self).__init__(connector, path,
                                             redfish_version)

    def create_zone(self, endpoints):
        """Create a new Zone

        :param endpoints: a full representation of Endpoints array
        :returns: The uri of the new zone
        """
        data = {"Links": {"Endpoints": []}}
        data['Links']['Endpoints'] = [
            {'@odata.id': endpoint} for endpoint in endpoints]

        resp = self._conn.post(self.path, data=data)
        LOG.info("Zone created at %s", resp.headers['Location'])
        zone_uri = resp.headers['Location']
        return zone_uri[zone_uri.find(self._path):]
