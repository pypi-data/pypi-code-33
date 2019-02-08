# Copyright 2018 Intel, Inc.
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

from rsd_lib.resources.v2_1.system import network_device_function


class NetworkDeviceFunctionTestCase(testtools.TestCase):

    def setUp(self):
        super(NetworkDeviceFunctionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'network_device_function.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.network_device_function_inst = network_device_function.\
            NetworkDeviceFunction(
                self.conn,
                '/redfish/v1/Systems/System1/NetworkInterfaces/1/'
                'NetworkDeviceFunctions/1',
                redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.network_device_function_inst._parse_attributes()
        self.assertEqual(
            '1.1.0', self.network_device_function_inst.redfish_version)
        self.assertEqual('Network Device Function View',
                         self.network_device_function_inst.name)
        self.assertEqual('1', self.network_device_function_inst.identity)
        self.assertEqual('Network Device Function View',
                         self.network_device_function_inst.description)
        self.assertEqual(
            True, self.network_device_function_inst.device_enabled)
        self.assertEqual(
            'Enabled', self.network_device_function_inst.status.state)
        self.assertEqual('OK', self.network_device_function_inst.status.health)
        self.assertEqual(
            'OK', self.network_device_function_inst.status.health_rollup)
        self.assertEqual('00:0C:29:9A:98:ED',
                         self.network_device_function_inst.ethernet.macaddress)
        self.assertEqual({}, self.network_device_function_inst.links)
        # iSCSIBoot section
        self.assertEqual(
            'IPv4',
            self.network_device_function_inst.iscsi_boot.ip_address_type)
        self.assertEqual(
            '10.0.10.10',
            self.network_device_function_inst.iscsi_boot.initiator_ip_address)
        self.assertEqual(
            'iqn.2017-03.com.intel:workload-server',
            self.network_device_function_inst.iscsi_boot.initiator_name)
        self.assertEqual(
            '10.0.10.1',
            self.network_device_function_inst.iscsi_boot.
            initiator_default_gateway)
        self.assertEqual(
            '255.255.255.0',
            self.network_device_function_inst.iscsi_boot.initiator_netmask)
        self.assertEqual(
            False,
            self.network_device_function_inst.iscsi_boot.target_info_via_dhcp)
        self.assertEqual(
            'iqn.2017-03.com.intel:image-server',
            self.network_device_function_inst.iscsi_boot.primary_target_name)
        self.assertEqual(
            '10.0.10.254',
            self.network_device_function_inst.iscsi_boot.
            primary_target_ip_address)
        self.assertEqual(
            3260,
            self.network_device_function_inst.iscsi_boot.
            primary_target_tcp_port)
        self.assertEqual(
            1, self.network_device_function_inst.iscsi_boot.primary_lun)
        self.assertEqual(
            True,
            self.network_device_function_inst.iscsi_boot.primary_vlan_enable)
        self.assertEqual(
            4088,
            self.network_device_function_inst.iscsi_boot.primary_vlan_id)
        self.assertEqual(
            None,
            self.network_device_function_inst.iscsi_boot.primary_dns)
        self.assertEqual(
            None,
            self.network_device_function_inst.iscsi_boot.secondary_target_name)
        self.assertEqual(
            None,
            self.network_device_function_inst.iscsi_boot.
            secondary_target_ip_address)
        self.assertEqual(
            None,
            self.network_device_function_inst.iscsi_boot.
            secondary_target_tcp_port)
        self.assertEqual(
            None,
            self.network_device_function_inst.iscsi_boot.secondary_lun)
        self.assertEqual(
            False,
            self.network_device_function_inst.iscsi_boot.secondary_vlan_enable)
        self.assertEqual(
            None,
            self.network_device_function_inst.iscsi_boot.secondary_vlan_id)
        self.assertEqual(
            None,
            self.network_device_function_inst.iscsi_boot.secondary_dns)

        self.assertEqual(
            False,
            self.network_device_function_inst.iscsi_boot.ip_mask_dns_via_dhcp)
        self.assertEqual(
            False,
            self.network_device_function_inst.iscsi_boot.
            router_advertisement_enabled)
        self.assertEqual(
            'CHAP',
            self.network_device_function_inst.iscsi_boot.authentication_method)
        self.assertEqual(
            'user',
            self.network_device_function_inst.iscsi_boot.chap_username)
        self.assertEqual(
            None,
            self.network_device_function_inst.iscsi_boot.chap_secret)
        self.assertEqual(
            'mutualuser',
            self.network_device_function_inst.iscsi_boot.mutual_chap_username)
        self.assertEqual(
            None,
            self.network_device_function_inst.iscsi_boot.mutual_chap_secret)

    def test_update(self):
        self.network_device_function_inst.update(
            ethernet={"MACAddress": "00:0C:29:9A:98:ED"})
        self.network_device_function_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/System1/NetworkInterfaces/1/'
            'NetworkDeviceFunctions/1',
            data={"Ethernet": {"MACAddress": "00:0C:29:9A:98:ED"}})

        self.network_device_function_inst._conn.patch.reset_mock()
        self.network_device_function_inst.update(
            iscsi_boot={"IPAddressType": "IPv4"})
        self.network_device_function_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/System1/NetworkInterfaces/1/'
            'NetworkDeviceFunctions/1',
            data={"iSCSIBoot": {"IPAddressType": "IPv4"}})

        self.network_device_function_inst._conn.patch.reset_mock()
        self.network_device_function_inst.update(
            ethernet={"MACAddress": "00:0C:29:9A:98:ED"},
            iscsi_boot={"IPAddressType": "IPv4"})
        self.network_device_function_inst._conn.patch.assert_called_once_with(
            '/redfish/v1/Systems/System1/NetworkInterfaces/1/'
            'NetworkDeviceFunctions/1',
            data={"Ethernet": {"MACAddress": "00:0C:29:9A:98:ED"},
                  "iSCSIBoot": {"IPAddressType": "IPv4"}})


class NetworkDeviceFunctionCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(NetworkDeviceFunctionCollectionTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'network_device_function_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        self.network_device_function_col = network_device_function.\
            NetworkDeviceFunctionCollection(
                self.conn,
                '/redfish/v1/Systems/System1/NetworkInterfaces/1/'
                'NetworkDeviceFunctions',
                redfish_version='1.1.0')

    def test__parse_attributes(self):
        self.network_device_function_col._parse_attributes()
        self.assertEqual(
            '1.1.0', self.network_device_function_col.redfish_version)
        self.assertEqual(
            ('/redfish/v1/Systems/System1/NetworkInterfaces/1/'
             'NetworkDeviceFunctions/1',),
            self.network_device_function_col.members_identities)

    @mock.patch.object(
        network_device_function, 'NetworkDeviceFunction',
        autospec=True)
    def test_get_member(self, mock_network_device_function):
        self.network_device_function_col.get_member(
            '/redfish/v1/Systems/System1/NetworkInterfaces/1/'
            'NetworkDeviceFunctions/1')
        mock_network_device_function.assert_called_once_with(
            self.network_device_function_col._conn,
            '/redfish/v1/Systems/System1/NetworkInterfaces/1/'
            'NetworkDeviceFunctions/1',
            redfish_version=self.network_device_function_col.redfish_version)

    @mock.patch.object(
        network_device_function, 'NetworkDeviceFunction',
        autospec=True)
    def test_get_members(self, mock_network_device_function):
        members = self.network_device_function_col.get_members()
        mock_network_device_function.assert_called_once_with(
            self.network_device_function_col._conn,
            '/redfish/v1/Systems/System1/NetworkInterfaces/1/'
            'NetworkDeviceFunctions/1',
            redfish_version=self.network_device_function_col.redfish_version)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
