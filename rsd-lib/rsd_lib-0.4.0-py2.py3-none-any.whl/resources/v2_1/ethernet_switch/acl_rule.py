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

import logging

from jsonschema import validate
from sushy.resources import base
from sushy import utils

from rsd_lib.resources.v2_1.ethernet_switch import schemas as acl_rule_schema
from rsd_lib import utils as rsd_lib_utils

LOG = logging.getLogger(__name__)


class IPSourceField(base.CompositeField):
    ipv4_address = base.Field('IPv4Address')
    mask = base.Field('Mask')


class MACSourceField(base.CompositeField):
    address = base.Field('Address')
    mask = base.Field('Mask', adapter=rsd_lib_utils.num_or_none)


class VLANIdField(base.CompositeField):
    id = base.Field('Id', adapter=rsd_lib_utils.num_or_none)
    mask = base.Field('Mask', adapter=rsd_lib_utils.num_or_none)


class L4SourcePortField(base.CompositeField):
    port = base.Field('Port', adapter=rsd_lib_utils.num_or_none)
    mask = base.Field('Mask', adapter=rsd_lib_utils.num_or_none)


class ConditionField(base.CompositeField):
    ip_source = IPSourceField('IPSource')
    ip_destination = base.Field('IPDestination')
    mac_source = MACSourceField('MACSource')
    mac_destination = base.Field('MACDestination')
    vlan_id = VLANIdField('VLANId')
    l4_source_port = L4SourcePortField('L4SourcePort')
    l4_destination_port = base.Field('L4DestinationPort',
                                     adapter=rsd_lib_utils.num_or_none)
    l4_protocol = base.Field('L4Protocol')


class ACLRule(base.ResourceBase):

    identity = base.Field('Id')
    """The acl rule identity string"""

    name = base.Field('Name')
    """The acl rule name"""

    description = base.Field('Description')
    """The acl rule description"""

    rule_id = base.Field('RuleId', adapter=rsd_lib_utils.num_or_none)
    """The acl rule id"""

    action = base.Field('Action')
    """The acl rule action"""

    forward_mirror_interface = base.Field(
        'ForwardMirrorInterface',
        adapter=rsd_lib_utils.get_resource_identity)
    """The acl rule forward mirror interface"""

    mirror_port_region = base.Field('MirrorPortRegion',
                                    adapter=utils.get_members_identities)
    """The acl rule mirror port region"""

    mirror_type = base.Field('MirrorType')
    """The acl rule mirror type"""

    condition = ConditionField('Condition')
    """The acl rule condition field"""

    oem = base.Field('Oem')
    """The ac rule oem field"""

    links = base.Field('Links')
    """The acl rule links field"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing an ACL Rule

        :param connector: A connector instance
        :param identity: The identity of the ACL Rule resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ACLRule, self).__init__(connector, identity, redfish_version)


class ACLRuleCollection(base.ResourceCollectionBase):

    @property
    def _resource_type(self):
        return ACLRule

    def __init__(self, connector, path, redfish_version=None):
        """A class representing an ACL Rule Collection

        :param connector: A Connector instance
        :param path: The canonical path to the ACL Rule collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ACLRuleCollection, self).__init__(connector,
                                                path,
                                                redfish_version)

    def add_acl_rule(self, acl_rule_req):
        """Add a acl rule

        :param acl_rule: JSON for acl_rule
        :returns: The location of the acl rule
        """
        target_uri = self._path
        validate(acl_rule_req, acl_rule_schema.acl_rule_req_schema)
        resp = self._conn.post(target_uri, data=acl_rule_req)
        acl_rule_url = resp.headers['Location']
        LOG.info("ACL Rule add at %s", acl_rule_url)
        return acl_rule_url[acl_rule_url.find(self._path):]
