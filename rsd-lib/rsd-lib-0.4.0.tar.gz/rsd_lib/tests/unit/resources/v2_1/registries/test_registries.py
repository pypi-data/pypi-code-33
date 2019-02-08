# Copyright 2019 Intel, Inc.
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

from rsd_lib.resources.v2_1.registries import registries


class RegistriesTestCase(testtools.TestCase):

    def setUp(self):
        super(RegistriesTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/registries.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.registries_inst = registries.Registries(
            self.conn, '/redfish/v1/Registries/Base',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.registries_inst._parse_attributes()
        self.assertEqual("Base", self.registries_inst.identity)
        self.assertEqual("Base Message Registry File",
                         self.registries_inst.name)
        self.assertEqual("Base Message Registry File locations",
                         self.registries_inst.description)
        self.assertEqual(['en'], self.registries_inst.languages)
        self.assertEqual("Base.1.0", self.registries_inst.registry)
        self.assertEqual("en", self.registries_inst.location[0].language)
        self.assertEqual(
            "https://www.dmtf.org/sites/default/files/standards"
            "/documents/DSP8011_1.0.0a.json",
            self.registries_inst.location[0].publication_uri)
        self.assertEqual({}, self.registries_inst.oem)


class RegistriesCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(RegistriesCollectionTestCase, self).setUp()
        self.conn = mock.Mock()

        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'registries_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.registries_col = registries.RegistriesCollection(
            self.conn,
            '/redfish/v1/Registries',
            redfish_version='1.0.2')

    def test_parse_attributes(self):
        self.registries_col._parse_attributes()
        self.assertEqual("Registry File Collection", self.registries_col.name)
        self.assertEqual(('/redfish/v1/Registries/Base',),
                         self.registries_col.members_identities)

    @mock.patch.object(registries, 'Registries', autospec=True)
    def test_get_member(self, mock_registries):
        self.registries_col.get_member('/redfish/v1/Registries/Base')

        mock_registries.assert_called_once_with(
            self.registries_col._conn,
            '/redfish/v1/Registries/Base',
            redfish_version=self.registries_col.redfish_version
        )

    @mock.patch.object(registries, 'Registries', autospec=True)
    def test_get_members(self, mock_registries):
        members = self.registries_col.get_members()
        self.assertEqual(mock_registries.call_count, 1)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
