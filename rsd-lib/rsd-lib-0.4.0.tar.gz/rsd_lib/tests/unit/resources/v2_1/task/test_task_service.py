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

from rsd_lib.resources.v2_1.task import task
from rsd_lib.resources.v2_1.task import task_service


class TaskServiceTestCase(testtools.TestCase):

    def setUp(self):
        super(TaskServiceTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/task_service.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.task_service_inst = task_service.TaskService(
            self.conn, '/redfish/v1/TaskService',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.task_service_inst._parse_attributes()
        self.assertEqual("TaskService", self.task_service_inst.identity)
        self.assertEqual("Tasks Service", self.task_service_inst.name)
        self.assertEqual("2015-03-13T04:14:33+06:00",
                         self.task_service_inst.date_time)
        self.assertEqual("Manual",
                         self.task_service_inst.
                         completed_task_overwrite_policy)
        self.assertEqual(True,
                         self.task_service_inst.
                         life_cycle_event_on_task_state_change)
        self.assertEqual("Enabled", self.task_service_inst.status.state)
        self.assertEqual("OK", self.task_service_inst.status.health)
        self.assertEqual(True, self.task_service_inst.service_enabled)
        self.assertEqual({}, self.task_service_inst.oem)

    def test__get_task_collection_path(self):
        expected = '/redfish/v1/TaskService/Tasks'
        result = self.task_service_inst._get_task_collection_path()
        self.assertEqual(expected, result)

    def test_tasks(self):
        # | GIVEN |
        self.conn.get.return_value.json.reset_mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'task_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN |
        actual_tasks = self.task_service_inst.tasks
        # | THEN |
        self.assertIsInstance(actual_tasks,
                              task.TaskCollection)
        self.conn.get.return_value.json.assert_called_once_with()

        # reset mock
        self.conn.get.return_value.json.reset_mock()
        # | WHEN & THEN |
        # tests for same object on invoking subsequently
        self.assertIs(actual_tasks,
                      self.task_service_inst.tasks)
        self.conn.get.return_value.json.assert_not_called()

    def test_tasks_on_refresh(self):
        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'task_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.task_service_inst.tasks,
                              task.TaskCollection)

        # On refreshing the event_service instance...
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'task_service.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.task_service_inst.invalidate()
        self.task_service_inst.refresh(force=False)

        # | GIVEN |
        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'task_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())
        # | WHEN & THEN |
        self.assertIsInstance(self.task_service_inst.tasks,
                              task.TaskCollection)
