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

from sushy import exceptions

from rsd_lib.resources.v2_1.fabric import port


class PortTestCase(testtools.TestCase):

    def setUp(self):
        super(PortTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/fabrics_port.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.port_inst = port.Port(
            self.conn, '/redfish/v1/Fabrics/PCIe/Switches/1/Ports/Up1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.port_inst._parse_attributes()
        self.assertEqual("Up1", self.port_inst.identity)
        self.assertEqual("PCIe Upstream Port 1", self.port_inst.name)
        self.assertEqual("PCIe Upstream Port 1", self.port_inst.description)
        self.assertEqual("Enabled", self.port_inst.status.state)
        self.assertEqual("OK", self.port_inst.status.health)
        self.assertEqual("1", self.port_inst.port_id)
        self.assertEqual("PCIe", self.port_inst.port_protocol)
        self.assertEqual("UpstreamPort", self.port_inst.port_type)
        self.assertEqual(32, self.port_inst.current_speed_gbps)
        self.assertEqual(4, self.port_inst.width)
        self.assertEqual(64, self.port_inst.max_speed_gbps)
        self.assertEqual("/redfish/v1/Fabrics/PCIe/Switches/1/Ports/Up1"
                         "/Actions/PCIePort.Reset",
                         self.port_inst.actions.reset.target_uri)
        self.assertEqual(["ForceOff", "ForceRestart", "ForceOn"],
                         self.port_inst.actions.reset.allowed_values)
        self.assertEqual(('/redfish/v1/Fabrics/PCIe/Endpoints/'
                          'HostRootComplex1',),
                         self.port_inst.links.associated_endpoints)
        self.assertEqual("#Intel.Oem.Port",
                         self.port_inst.oem.intel_rackScale.odata_type)
        self.assertEqual(['XYZ1234567890'],
                         self.port_inst.oem.intel_rackScale.pcie_connection_id)

    def test__parse_attributes_missing_reset_target(self):
        self.port_inst.json['Actions']['#Port.Reset'].pop(
            'target')
        self.assertRaisesRegex(
            exceptions.MissingAttributeError,
            'attribute Actions/#Port.Reset/target',
            self.port_inst._parse_attributes)

    def test_get__reset_action_element(self):
        value = self.port_inst._get_reset_action_element()
        self.assertEqual("/redfish/v1/Fabrics/PCIe/Switches/1/Ports/Up1/"
                         "Actions/PCIePort.Reset",
                         value.target_uri)
        self.assertEqual(["ForceOff", "ForceRestart", "ForceOn"],
                         value.allowed_values)

    def test__get_reset_action_element_missing_reset_action(self):
        self.port_inst.actions.reset = None
        self.assertRaisesRegex(
            exceptions.MissingActionError, 'action #Port.Reset',
            self.port_inst._get_reset_action_element)

    def test_get_allowed_reset_port_values(self):
        values = self.port_inst.get_allowed_reset_port_values()
        expected = ["ForceOff", "ForceRestart", "ForceOn"]
        self.assertEqual(expected, values)
        self.assertIsInstance(values, list)

    def test_reset_port(self):
        self.port_inst.reset_port('ForceOn')
        self.port_inst._conn.post.assert_called_once_with(
            '/redfish/v1/Fabrics/PCIe/Switches/1/Ports/Up1/Actions/'
            'PCIePort.Reset',
            data={'ResetType': 'ForceOn'})

    def test_reset_port_invalid_value(self):
        self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            '"value" value "GracefulRestart" is invalid.',
            self.port_inst.reset_port, 'GracefulRestart')


class PortCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(PortCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'fabrics_port_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.port_col = port.PortCollection(
            self.conn, '/redfish/v1/Fabrics/PCIe/Switches/1/Ports',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.port_col._parse_attributes()
        self.assertEqual("PCIe Port Collection", self.port_col.name)
        self.assertEqual("1.0.2", self.port_col.redfish_version)
        self.assertEqual(('/redfish/v1/Fabrics/PCIe/Switches/1/Ports/Up1',
                          '/redfish/v1/Fabrics/PCIe/Switches/1/Ports/Up2',
                          '/redfish/v1/Fabrics/PCIe/Switches/1/Ports/Down1',
                          '/redfish/v1/Fabrics/PCIe/Switches/1/Ports/Down2'),
                         self.port_col.members_identities)

    @mock.patch.object(port, 'Port', autospec=True)
    def test_get_member(self, mock_port):
        self.port_col.get_member(
            '/redfish/v1/Fabrics/PCIe/Switches/1/Ports/Up1')
        mock_port.assert_called_once_with(
            self.port_col._conn,
            '/redfish/v1/Fabrics/PCIe/Switches/1/Ports/Up1',
            redfish_version=self.port_col.redfish_version)

    @mock.patch.object(port, 'Port', autospec=True)
    def test_get_members(self, mock_port):
        members = self.port_col.get_members()
        mock_port.assert_called_with(
            self.port_col._conn, '/redfish/v1/Fabrics/PCIe/Switches/1/'
                                 'Ports/Down2',
            redfish_version='1.0.2')
        self.assertIsInstance(members, list)
        self.assertEqual(mock_port.call_count, 4)
        self.assertEqual(4, len(members))
