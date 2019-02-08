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


class TaskTestCase(testtools.TestCase):

    def setUp(self):
        super(TaskTestCase, self).setUp()
        self.conn = mock.Mock()
        with open('rsd_lib/tests/unit/json_samples/v2_1/task.json',
                  'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.task_inst = task.Task(
            self.conn, '/redfish/v1/TaskService/Tasks/1',
            redfish_version='1.0.2')

    def test__parse_attributes(self):
        self.task_inst._parse_attributes()
        self.assertEqual("1", self.task_inst.identity)
        self.assertEqual("Task 1", self.task_inst.name)
        self.assertEqual("Task 1", self.task_inst.description)
        self.assertEqual("Completed", self.task_inst.task_state)
        self.assertEqual("2016-08-18T12:00+01:00", self.task_inst.start_time)
        self.assertEqual("2016-08-18T13:13+01:00", self.task_inst.end_time)
        self.assertEqual("OK", self.task_inst.task_status)
        self.assertEqual("Base.1.0.Created",
                         self.task_inst.messages[0].message_id)
        self.assertEqual([], self.task_inst.messages[0].related_properties)
        self.assertEqual("The resource has been created successfully",
                         self.task_inst.messages[0].message)
        self.assertEqual([], self.task_inst.messages[0].message_args)
        self.assertEqual("OK", self.task_inst.messages[0].severity)

    def test_delete(self):
        self.task_inst.delete()
        self.task_inst._conn.delete.assert_called_once()


class TaskCollectionTestCase(testtools.TestCase):

    def setUp(self):
        super(TaskCollectionTestCase, self).setUp()
        self.conn = mock.Mock()

        with open('rsd_lib/tests/unit/json_samples/v2_1/'
                  'task_collection.json', 'r') as f:
            self.conn.get.return_value.json.return_value = json.loads(f.read())

        self.task_col = task.TaskCollection(self.conn,
                                            '/redfish/v1/TaskService/Tasks',
                                            redfish_version='1.0.2')

    def test_parse_attributes(self):
        self.task_col._parse_attributes()
        self.assertEqual("Task Collection", self.task_col.name)
        self.assertEqual(('/redfish/v1/TaskService/Tasks/1',),
                         self.task_col.members_identities)

    @mock.patch.object(task, 'Task', autospec=True)
    def test_get_member(self, mock_task):
        self.task_col.get_member('/redfish/v1/TaskService/Tasks/1')

        mock_task.assert_called_once_with(
            self.task_col._conn,
            '/redfish/v1/TaskService/Tasks/1',
            redfish_version=self.task_col.redfish_version
        )

    @mock.patch.object(task, 'Task', autospec=True)
    def test_get_members(self, mock_task):
        members = self.task_col.get_members()
        self.assertEqual(mock_task.call_count, 1)
        self.assertIsInstance(members, list)
        self.assertEqual(1, len(members))
