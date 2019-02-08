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

import json
import jsonschema
import mock
import testtools

from sushy import exceptions

from rsd_lib.resources.v2_3.node import node
from rsd_lib.tests.unit.fakes import request_fakes


class NodeTestCase(testtools.TestCase):

    def setUp(self):
        super(NodeTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_3/node.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.node_inst = node.Node(
            self.conn, '/redfish/v1/Nodes/Node1',
            redfish_version='1.0.2')

    def test__get_attach_endpoint_action_element(self):
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        value = self.node_inst._get_attach_endpoint_action_element()
        self.assertEqual('/redfish/v1/Nodes/Node1/Actions/'
                         'ComposedNode.AttachResource',
                         value.target_uri)
        self.assertEqual('/redfish/v1/Nodes/Node1/Actions/'
                         'AttachResourceActionInfo',
                         value.action_info_path)
        expected = [
            {
                "name": "Resource",
                "required": True,
                "data_type": "Object",
                "object_data_type": "#Resource.Resource",
                "allowable_values": (
                    "/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1",
                )
            },
            {
                "name": "Protocol",
                "required": False,
                "data_type": "String",
                "object_data_type": None,
                "allowable_values": ["NVMeOverFabrics"]
            }
        ]
        self.assertEqual(expected, value.action_info.parameters)

    def test_get_allowed_attach_endpoints(self):
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        expected = self.node_inst.get_allowed_attach_endpoints()
        result = ("/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1",)
        self.assertEqual(expected, result)

    def test_attach_endpoint(self):
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.node_inst.attach_endpoint(
            resource='/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1',
            protocol='NVMeOverFabrics')
        self.node_inst._conn.post.assert_called_once_with(
            '/redfish/v1/Nodes/Node1/Actions/ComposedNode.AttachResource',
            data={'Resource': {'@odata.id': '/redfish/v1/StorageServices'
                                            '/1-sv-1/Volumes/1-sv-1-vl-1'},
                  'Protocol': 'NVMeOverFabrics'})

    def test_attach_endpoint_only_with_resource_uri(self):
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.node_inst.attach_endpoint(
            resource='/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1')
        self.node_inst._conn.post.assert_called_once_with(
            '/redfish/v1/Nodes/Node1/Actions/ComposedNode.AttachResource',
            data={'Resource': {'@odata.id': '/redfish/v1/StorageServices'
                                            '/1-sv-1/Volumes/1-sv-1-vl-1'}})

    def test_attach_endpoint_invalid_parameter(self):
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            '"resource" value.*{0}'.format(
                '/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1')):

            self.node_inst.attach_endpoint(resource='invalid-resource')

    def test__get_detach_endpoint_action_element(self):
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        value = self.node_inst._get_detach_endpoint_action_element()
        self.assertEqual('/redfish/v1/Nodes/Node1/Actions/'
                         'ComposedNode.DetachResource',
                         value.target_uri)
        self.assertEqual('/redfish/v1/Nodes/Node1/Actions/'
                         'DetachResourceActionInfo',
                         value.action_info_path)
        expected = [
            {
                "name": "Resource",
                "required": True,
                "data_type": "Object",
                "object_data_type": "#Resource.Resource",
                "allowable_values": (
                    "/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1",
                )
            },
            {
                "name": "Protocol",
                "required": False,
                "data_type": "String",
                "object_data_type": None,
                "allowable_values": ["NVMeOverFabrics"]
            }
        ]
        self.assertEqual(expected, value.action_info.parameters)

    def test_get_allowed_detach_endpoints(self):
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        expected = self.node_inst.get_allowed_detach_endpoints()
        result = ("/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1",)
        self.assertEqual(expected, result)

    def test_detach_endpoint(self):
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.node_inst.detach_endpoint(
            resource='/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1')
        self.node_inst._conn.post.assert_called_once_with(
            '/redfish/v1/Nodes/Node1/Actions/ComposedNode.DetachResource',
            data={'Resource': {'@odata.id': '/redfish/v1/StorageServices'
                                            '/1-sv-1/Volumes/1-sv-1-vl-1'}})

    def test_detach_endpoint_invalid_parameter(self):
        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        with self.assertRaisesRegex(
            exceptions.InvalidParameterValueError,
            '"resource" value.*{0}'.format(
                '/redfish/v1/StorageServices/1-sv-1/Volumes/1-sv-1-vl-1')):

            self.node_inst.detach_endpoint(resource='invalid-resource')

    def test_refresh(self):
        self.assertIsNone(self.node_inst._actions.attach_endpoint.action_info)
        self.assertIsNone(self.node_inst._actions.detach_endpoint.action_info)

        with open('rsd_lib/tests/unit/json_samples/v2_3/'
                  'attach_action_info.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.node_inst._get_attach_endpoint_action_element()
        self.node_inst._get_detach_endpoint_action_element()

        self.assertIsNotNone(
            self.node_inst._actions.attach_endpoint.action_info)
        self.assertIsNotNone(
            self.node_inst._actions.detach_endpoint.action_info)

        with open('rsd_lib/tests/unit/json_samples/v2_3/node.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.node_inst.refresh()

        self.assertIsNone(self.node_inst._actions.attach_endpoint.action_info)
        self.assertIsNone(self.node_inst._actions.detach_endpoint.action_info)


class NodeCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(NodeCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_3/node_collection.json',
                  'r') as f:
            self.conn.get.return_value = request_fakes.fake_request_get(
                json.loads(f.read()))
            self.conn.post.return_value = request_fakes.fake_request_post(
                None, headers={"Location": "https://localhost:8443/"
                                           "redfish/v1/Nodes/1"})
        self.node_col = node.NodeCollection(
            self.conn, '/redfish/v1/Nodes', redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.node_col._parse_attributes()
        self.assertEqual('1.0.2', self.node_col.redfish_version)
        self.assertEqual('Composed Node Collection', self.node_col.name)
        self.assertEqual(('/redfish/v1/Nodes/1',),
                         self.node_col.members_identities)

    @mock.patch.object(node, 'Node', autospec=True)
    def test_get_member(self, mock_node):
        self.node_col.get_member('/redfish/v1/Nodes/1')
        mock_node.assert_called_once_with(
            self.node_col._conn, '/redfish/v1/Nodes/1',
            redfish_version=self.node_col.redfish_version)

    @mock.patch.object(node, 'Node', autospec=True)
    def test_get_members(self, mock_node):
        members = self.node_col.get_members()
        mock_node.assert_called_once_with(
            self.node_col._conn, '/redfish/v1/Nodes/1',
            redfish_version=self.node_col.redfish_version)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))

    def test__get_compose_action_element(self):
        value = self.node_col._get_compose_action_element()
        self.assertEqual('/redfish/v1/Nodes/Actions/Allocate',
                         value.target_uri)

    def test_compose_node_no_reqs(self):
        result = self.node_col.compose_node()
        self.node_col._conn.post.assert_called_once_with(
            '/redfish/v1/Nodes/Actions/Allocate', data={})
        self.assertEqual(result, '/redfish/v1/Nodes/1')

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
            'RemoteDrives': [{
                'CapacityGiB': 80,
                'Protocol': 'NVMeOverFabrics',
                'Master': {
                    'Type': 'Snapshot',
                    'Resource': {
                        '@odata.id':
                            '/redfish/v1/StorageServices/NVMeoE1/Volumes/102'
                    }
                },
                'Resource': {
                    '@odata.id':
                        '/redfish/v1/StorageServices/NVMeoE1/Volumes/102'
                }
            }],
            'Security': {
                'TpmPresent': True,
                'TpmInterfaceType': 'TPM2_0',
                'TxtEnabled': True,
                'ClearTPMOnDelete': True
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
            remote_drive_req=[{
                'CapacityGiB': 80,
                'Protocol': 'NVMeOverFabrics',
                'Master': {
                    'Type': 'Snapshot',
                    'Resource': {
                        '@odata.id':
                            '/redfish/v1/StorageServices/NVMeoE1/Volumes/102'
                    }
                },
                'Resource': {
                    '@odata.id':
                        '/redfish/v1/StorageServices/NVMeoE1/Volumes/102'
                }
            }],
            security_req={
                'TpmPresent': True,
                'TpmInterfaceType': 'TPM2_0',
                'TxtEnabled': True,
                'ClearTPMOnDelete': True
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

        # Wrong remote drive CapacityGiB
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid' is not of type 'number'")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                remote_drive_req=[{
                    'CapacityGiB': 'invalid',
                    'Protocol': 'NVMeOverFabrics',
                    'Master': {
                        'Type': 'Snapshot',
                        'Resource': {
                            '@odata.id':
                                '/redfish/v1/StorageServices/NVMeoE1/Volumes/'
                                '102'
                        }
                    },
                    'Resource': {
                        '@odata.id':
                            '/redfish/v1/StorageServices/NVMeoE1/Volumes/102'
                        }
                }])

        # Wrong remote drive Protocol
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid' is not one of \['iSCSI', 'NVMeOverFabrics'\]")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                remote_drive_req=[{
                    'CapacityGiB': 80,
                    'Protocol': 'invalid',
                    'Master': {
                        'Type': 'Snapshot',
                        'Resource': {
                            '@odata.id':
                                '/redfish/v1/StorageServices/NVMeoE1/Volumes/'
                                '102'
                        }
                    },
                    'Resource': {
                        '@odata.id':
                            '/redfish/v1/StorageServices/NVMeoE1/Volumes/102'
                        }
                }])

        # Wrong remote drive Master Type
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            ("'invalid' is not one of \['Snapshot', 'Clone'\]")):

            self.node_col.compose_node(
                name='test', description='this is a test node',
                remote_drive_req=[{
                    'CapacityGiB': 80,
                    'Protocol': 'iSCSI',
                    'Master': {
                        'Type': 'invalid',
                        'Resource': {
                            '@odata.id':
                                '/redfish/v1/StorageServices/NVMeoE1/Volumes/'
                                '102'
                        }
                    },
                    'Resource': {
                        '@odata.id':
                            '/redfish/v1/StorageServices/NVMeoE1/Volumes/102'
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
                    'TxtEnabled': True,
                    'ClearTPMOnDelete': True
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
                    'TxtEnabled': True,
                    'ClearTPMOnDelete': True
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
                    'TxtEnabled': 'invalid',
                    'ClearTPMOnDelete': True
                })

        # Wrong security parameter "ClearTPMOnDelete"
        with self.assertRaisesRegex(
            jsonschema.exceptions.ValidationError,
            "'invalid' is not of type 'boolean'"):
            self.node_col.compose_node(
                name='test', description='this is a test node',
                security_req={
                    'TpmPresent': True,
                    'TpmInterfaceType': 'TPM2_0',
                    'TxtEnabled': True,
                    'ClearTPMOnDelete': 'invalid'
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
