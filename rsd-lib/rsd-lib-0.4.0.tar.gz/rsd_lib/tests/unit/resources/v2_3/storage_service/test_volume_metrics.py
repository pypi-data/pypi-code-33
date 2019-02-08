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

from rsd_lib.resources.v2_3.storage_service import volume_metrics


class VolumeMetricsTestCase(testtools.TestCase):

    def setUp(self):
        super(VolumeMetricsTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_3/volume_metrics.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.volume_metrics_inst = volume_metrics.VolumeMetrics(
            self.conn, '/redfish/v1/StorageServices/NVMeoE1/Volumes/1/Metrics',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.volume_metrics_inst._parse_attributes()
        self.assertEqual('Volume Metrics', self.volume_metrics_inst.name)
        self.assertEqual('Metrics', self.volume_metrics_inst.identity)
        self.assertEqual('Metrics for Volume 1',
                         self.volume_metrics_inst.description)
        self.assertEqual(6799708160,
                         self.volume_metrics_inst.capacity_used_bytes)
