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
from rsd_lib.resources.v2_2.ethernet_switch import metrics
import testtools


class MetricsTestCase(testtools.TestCase):

    def setUp(self):
        super(MetricsTestCase, self).setUp()
        self.conn = mock.Mock()
        with open(
                'rsd_lib/tests/unit/json_samples/v2_2/'
                'ethernet_switch_metrics.json',
                'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.metrics_inst = metrics.Metrics(self.conn,
                                            '/redfish/v1/EthernetSwitches/'
                                            'Switch1/Metrics',
                                            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.metrics_inst._parse_attributes()
        self.assertEqual('EthernetSwitch Metrics for Switch1',
                         self.metrics_inst.name)
        self.assertEqual('description-as-string',
                         self.metrics_inst.description)
        self.assertEqual('Metrics for Switch1', self.metrics_inst.identity)
        self.assertEqual('OK', self.metrics_inst.health)
