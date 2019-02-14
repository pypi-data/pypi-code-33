"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import unittest

from cortex_client.client import build_client
from cortex_client.client import _Client
from cortex_client.types import InputMessage
from cortex_client.datasetsclient import DatasetsClient


class Test_Client(unittest.TestCase):

    def setUp(self):
        self.message = {
            "instanceId": "agent1", 
            "sessionId":"session1", 
            "channelId": "proc1", 
            "typeName": "aType", 
            "timestamp":"12:00:00", 
            "token": "foo",
            "payload": {},
            "apiEndpoint": "http://google.com", 
            "properties": {}
        }

    def test_build_client_base_url(self):
        self.message['apiEndpoint'] = 'http://google.com'
        im = InputMessage.from_params(self.message)
        c = build_client(_Client, im, 2)
        self.assertIsInstance(c, _Client)
        self.assertEqual(c._serviceconnector.base_url, 'http://google.com/v2')

    def test_build_dataset_client(self):
        self.message['apiEndpoint'] = 'http://google.com'
        im = InputMessage.from_params(self.message)
        c = build_client(DatasetsClient, im, 16)
        self.assertIsInstance(c, DatasetsClient)
        self.assertEqual(c._serviceconnector.base_url, 'http://google.com/v16')