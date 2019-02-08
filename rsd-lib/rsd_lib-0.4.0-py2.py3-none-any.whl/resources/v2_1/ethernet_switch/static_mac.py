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

from rsd_lib import utils as rsd_lib_utils


class StaticMAC(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The static mac identity string"""

    name = base.Field('Name')
    """The static mac name"""

    description = base.Field('Description')
    """The static mac description"""

    mac_address = base.Field('MACAddress')
    """The static mac address"""

    vlan_id = base.Field('VLANId', adapter=rsd_lib_utils.num_or_none)
    """The static mac vlan id"""

    oem = base.Field('Oem')
    """The static mac oem info"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing an StaticMAC

        :param connector: A Connector instance
        :param identity: The identity of the StaticMAC resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(StaticMAC, self).__init__(connector, identity, redfish_version)


class StaticMACCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return StaticMAC

    def __init__(self, connector, path, redfish_version=None):
        """A class representing an StaticMAC

        :param connector: A Connector instance
        :param identity: The identity of the StaticMAC Collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(StaticMACCollection, self).__init__(connector,
                                                  path,
                                                  redfish_version)
