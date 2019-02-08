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

from jsonschema import validate
import logging
from sushy.resources import base

from rsd_lib.resources.v2_1.ethernet_switch import schemas as \
    ethernet_switch_schemas
from rsd_lib import utils as rsd_lib_utils

LOG = logging.getLogger(__name__)


class VLAN(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The vlan network interface identity"""

    name = base.Field('Name')
    """The vlan network interface name"""

    description = base.Field('Description')
    """The vlan network interface description"""

    vlan_enable = base.Field('VLANEnable', adapter=bool)
    """The boolean indicate this vlan network interface is enabled or not"""

    vlan_id = base.Field('VLANId', adapter=rsd_lib_utils.num_or_none)
    """The vlan network interface id"""

    oem = base.Field('Oem')
    """The vlan network interface oem info"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing an VLAN network interface

        :param connector: A Connector instance
        :param identity: The identity of the VLAN network interface  resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(VLAN, self).__init__(connector, identity, redfish_version)


class VLANCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return VLAN

    def __init__(self, connector, path, redfish_version=None):
        """A class representing an VLAN network interface collection

        :param connector: A Connector instance
        :param path: The canonical path to the VLAN network interface
            collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(VLANCollection, self).__init__(connector, path, redfish_version)

    def add_vlan(self, vlan_network_interface_req):
        """Add a vlan to port

        :param vlan_network_interface_req: JSON for vlan network interface
        :returns: The location of the vlan network interface
        """
        target_uri = self._path
        validate(vlan_network_interface_req,
                 ethernet_switch_schemas.vlan_network_interface_req_schema)
        resp = self._conn.post(target_uri, data=vlan_network_interface_req)
        LOG.info("VLAN add at %s", resp.headers['Location'])
        vlan_network_interface_url = resp.headers['Location']
        return vlan_network_interface_url[vlan_network_interface_url.
                                          find(self._path):]
