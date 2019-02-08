# Copyright (c) 2018 Intel, Corp.
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
import jsonschema
import mock
import testtools

from rsd_lib.resources.v2_2.node import node
from rsd_lib.tests.unit.fakes import request_fakes


class NodeCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(NodeCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/node_collection.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
            self.conn.post.return_value = request_fakes.fake_request_post(
                None, headers={"Location": "https://localhost:8443/"
                                           "redfish/v1/Nodes/1"})

        self.node_col = node.NodeCollection(
            self.conn, '/redfish/v1/Nodes', redfish_version='1.0.2')

    def test_compose_node(self):
        reqs = {
            'Name': 'test',
            'Description': 'this is a test node',
            'Processors': [{
                'TotalCores': 4,
                'ProcessorType': 'FPGA',
                'Oem': {
                    'Brand': 'Platinum',
                    'Capabilities': ['sse']
                }
            }],
            'Memory': [{
                'CapacityMiB': 8000
            }],
            'Security': {
                'TpmPresent': True,
                'TpmInterfaceType': 'TPM2_0',
                'TxtEnabled': True
            },
            'TotalSystemCoreCount': 8,
            'TotalSystemMemoryMiB': 16000
        }
        result = self.node_col.compose_node(
            name='test', description='this is a test node',
            processor_req=[{
                'TotalCores': 4,
                'ProcessorType': 'FPGA',
                'Oem': {
                    'Brand': 'Platinum',
                    'Capabilities': ['sse']
                }
            }],
            memory_req=[{'CapacityMiB': 8000}],
            security_req={
                'TpmPresent': True,
                'TpmInterfaceType': 'TPM2_0',
                'TxtEnabled': True
            },
            total_system_core_req=8,
            total_system_memory_req=16000)
        self.node_col._conn.post.assert_called_once_with(
            '/redfish/v1/Nodes/Actions/Allocate', data=reqs)
        self.assertEqual(result, '/redfish/v1/Nodes/1')

    def test_compose_node_with_invalid_reqs(self):
        # Wrong processor type
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid' is not one of \['CPU', 'FPGA', 'GPU', 'DSP', "
             "'Accelerator', 'OEM'\]")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                processor_req=[{
                    'TotalCores': 4,
                    'ProcessorType': 'invalid'}])

        # Wrong processor Oem Brand
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid' is not one of \['E3', 'E5'")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                processor_req=[{
                    'TotalCores': 4,
                    'Oem': {
                        'Brand': 'invalid',
                        'Capabilities': ['sse']
                    }
                }])

        # Wrong processor Oem Capabilities
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'sse' is not of type 'array'")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                processor_req=[{
                    'TotalCores': 4,
                    'Oem': {
                        'Brand': 'E3',
                        'Capabilities': 'sse'
                    }
                }])

        # Wrong processor Oem Capabilities
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("0 is not of type 'string'")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                processor_req=[{
                    'TotalCores': 4,
                    'Oem': {
                        'Brand': 'E3',
                        'Capabilities': [0]
                    }
                }])

        # Wrong security parameter "TpmPresent"
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            "'invalid' is not of type 'boolean'"):
            self.node_col.compose_node(
                name='test', description='this is a test node',
                security_req={
                    'TpmPresent': 'invalid',
                    'TpmInterfaceType': 'TPM2_0',
                    'TxtEnabled': True
                })

        # Wrong security parameter "TpmInterfaceType"
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            "True is not of type 'string'"):
            self.node_col.compose_node(
                name='test', description='this is a test node',
                security_req={
                    'TpmPresent': False,
                    'TpmInterfaceType': True,
                    'TxtEnabled': True
                })

        # Wrong security parameter "TxtEnabled"
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            "'invalid' is not of type 'boolean'"):
            self.node_col.compose_node(
                name='test', description='this is a test node',
                security_req={
                    'TpmPresent': True,
                    'TpmInterfaceType': 'TPM2_0',
                    'TxtEnabled': 'invalid'
                })

        # Wrong additional security parameter
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("Additional properties are not allowed \('invalid-key' was "
             "unexpected\)")):
            self.node_col.compose_node(
                name='test', description='this is a test node',
                security_req={
                    'TpmPresent': True,
                    'TpmInterfaceType': 'TPM2_0',
                    'TxtEnabled': False,
                    'invalid-key': 'invalid-value'
                })
