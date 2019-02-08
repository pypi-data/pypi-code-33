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


from rsd_lib.resources.v2_1.manager import network_protocol


class NetworkProtocolTestCase(testtools.TestCase):

    def setUp(self):
        super(NetworkProtocolTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
                'rsd_lib/tests/unit/json_samples/v2_1/'
                'network_protocol.json',
                'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.network_protocol_inst = network_protocol.NetworkProtocol(
            self.conn, 'redfish/v1/Managers/BMC1/NetworkProtocol',
            redfish_version='1.1.0')

    def test_parse_attributes(self):
        self.network_protocol_inst._parse_attributes()
        self.assertEqual('NetworkProtocol', self.network_protocol_inst.
                         identify)
        self.assertEqual(
            'Manager Network Protocol',
            self.network_protocol_inst.name)
        self.assertEqual('Manager Network Service Status',
                         self.network_protocol_inst.description)
        self.assertEqual('mymanager', self.network_protocol_inst.hostname)
        self.assertEqual(
            'mymanager.mydomain.com',
            self.network_protocol_inst.fqdn)

        # Status section
        self.assertEqual('Enabled',
                         self.network_protocol_inst.status.state)
        self.assertEqual('OK',
                         self.network_protocol_inst.status.health)
        self.assertEqual(None,
                         self.network_protocol_inst.status.health_rollup)

        self.assertEqual(True,
                         self.network_protocol_inst.http.protocol_enables)
        self.assertEqual(80,
                         self.network_protocol_inst.http.port)

        self.assertEqual(True,
                         self.network_protocol_inst.https.protocol_enables)
        self.assertEqual(443, self.network_protocol_inst.https.port)

        self.assertEqual(True,
                         self.network_protocol_inst.ipmi.protocol_enables)
        self.assertEqual(623, self.network_protocol_inst.ipmi.port)

        self.assertEqual(True,
                         self.network_protocol_inst.ssh.protocol_enables)
        self.assertEqual(22, self.network_protocol_inst.ssh.port)

        self.assertEqual(True,
                         self.network_protocol_inst.snmp.protocol_enables)
        self.assertEqual(161,
                         self.network_protocol_inst.snmp.port)

        self.assertEqual(True,
                         self.network_protocol_inst.
                         virtual_media.protocol_enables)
        self.assertEqual(17988,
                         self.network_protocol_inst.virtual_media.port)

        self.assertEqual(True,
                         self.network_protocol_inst.ssdp.protocol_enables)
        self.assertEqual(1900,
                         self.network_protocol_inst.ssdp.port)
        self.assertEqual(600,
                         self.network_protocol_inst.
                         ssdp.notify_multicast_interval_seconds)
        self.assertEqual(5, self.network_protocol_inst.ssdp.notify_ttl)
        self.assertEqual('Site', self.network_protocol_inst.
                         ssdp.notify_ipv6_scope)

        self.assertEqual(True, self.network_protocol_inst.
                         telnet.protocol_enables)
        self.assertEqual(23, self.network_protocol_inst.telnet.port)

        self.assertEqual(True, self.network_protocol_inst.kvm_ip.
                         protocol_enables)
        self.assertEqual(5288, self.network_protocol_inst.kvm_ip.port)
