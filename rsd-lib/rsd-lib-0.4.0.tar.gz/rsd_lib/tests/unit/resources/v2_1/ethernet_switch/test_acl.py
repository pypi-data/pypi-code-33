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

import json

import mock
import testtools

from sushy import exceptions

from rsd_lib.resources.v2_1.ethernet_switch import acl
from rsd_lib.resources.v2_1.ethernet_switch import acl_rule


class ACLTestCase(testtools.TestCase):

    def setUp(self):
        super(ACLTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
            'rsd_lib/tests/unit/json_samples/v2_1/ethernet_switch_acl.json',
                'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.acl_inst = acl.ACL(
            self.conn, '/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1',
            redfish_version='1.0.2'
        )

    def test__parse_attributes(self):
        self.acl_inst._parse_attributes()
        self.assertEqual('1.0.2', self.acl_inst.redfish_version)
        self.assertEqual('ACL1', self.acl_inst.identity)
        self.assertEqual('Ethernet Switch Access Control List',
                         self.acl_inst.name)
        self.assertEqual('Switch ACL', self.acl_inst.description)
        self.assertEqual({}, self.acl_inst.oem)

    def test__get_acl_rule_collection_path(self):
        self.assertEqual(
            '/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1/Rules',
            self.acl_inst._get_acl_rule_collection_path())

    def test__get_acl_rule_collection_path_missing_attr(self):
        self.acl_inst._json.pop('Rules')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError, 'attribute Rules',
            self.acl_inst._get_acl_rule_collection_path)

    def test_acl_rule(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_acl.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_acl_rules = self.acl_inst.rules
        # | THEN |
        self.assertIsInstance(actual_acl_rules,
                              acl_rule.ACLRuleCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_acl_rules,
                      self.acl_inst.rules)
        self.conn.get.return_value.json.assert_not_called()

    def test_acl_rule_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'acl_rule_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.acl_inst.rules,
                              acl_rule.ACLRuleCollection)

        # On refreshing the acl_rule instance...
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_acl.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.acl_inst.invalidate()
        self.acl_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'acl_rule_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.acl_inst.rules,
                              acl_rule.ACLRuleCollection)


class ACLCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(ACLCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'ethernet_switch_acl_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
            self.acl_col = acl.ACLCollection(
                self.conn, '/redfish/v1/EthernetSwitches/ACLs',
                redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.acl_col._parse_attributes()
        self.assertEqual('1.0.2', self.acl_col.redfish_version)
        self.assertEqual(
            'Ethernet Switch Access Control List Collection',
            self.acl_col.name)
        self.assertEqual(
            ('/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1',),
            self.acl_col.members_identities)

    @mock.patch.object(acl, 'ACL', autospec=True)
    def test_get_member(self, mock_acl):
        self.acl_col.get_member(
            '/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1')
        mock_acl.assert_called_once_with(
            self.acl_col._conn,
            '/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1',
            redfish_version=self.acl_col.redfish_version)

    @mock.patch.object(acl, 'ACL', autospec=True)
    def test_get_members(self, mock_acl):
        members = self.acl_col.get_members()
        mock_acl.assert_called_with(
            self.acl_col._conn,
            '/redfish/v1/EthernetSwitches/Switch1/ACLs/ACL1',
            redfish_version=self.acl_col.redfish_version)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
