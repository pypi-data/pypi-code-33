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

from rsd_lib.resources.v2_2.fabric import port


class PortTestCase(testtools.TestCase):

    def setUp(self):
        super(PortTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_2/fabrics_port.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.port_inst = port.Port(
            self.conn, '/redfish/v1/Fabrics/PCIe/Switches/1/Ports/Up1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.port_inst._parse_attributes()
        self.assertEqual('/redfish/v1/Fabrics/PCIe/Switches/1/'
                         'Ports/Up1/Metrics',
                         self.port_inst.oem.intel_rackScale.metrics)
