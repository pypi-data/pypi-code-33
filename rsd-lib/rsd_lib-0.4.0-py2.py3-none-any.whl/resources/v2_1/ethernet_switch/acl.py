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

from rsd_lib.resources.v2_1.ethernet_switch import acl_rule


class ACL(base.ResourceBase):

    identity = base.Field('Id', required=True)
    """The acl identity string"""

    name = base.Field('Name')
    """The acl name"""

    description = base.Field('Description')
    """The acl description"""

    oem = base.Field('Oem')
    """The acl oem info"""

    links = base.Field('Links')
    """The acl links"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing an ACL

        :param connector: A Connector instance
        :param identity: The identity of the ACL resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ACL, self).__init__(connector, identity, redfish_version)

    def _get_acl_rule_collection_path(self):
        """Helper function to find the RuleCollection path"""
        return utils.get_sub_resource_path_by(self, 'Rules')

    @property
    @utils.cache_it
    def rules(self):
        """Property to provide reference to `RuleCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return acl_rule.ACLRuleCollection(
            self._conn, self._get_acl_rule_collection_path(),
            redfish_version=self.redfish_version)


class ACLCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return ACL

    def __init__(self, connector, path, redfish_version=None):
        """A class representing an ACL

        :param connector: A Connector instance
        :param path: The canonical path to the ACL collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ACLCollection, self).__init__(connector, path, redfish_version)
