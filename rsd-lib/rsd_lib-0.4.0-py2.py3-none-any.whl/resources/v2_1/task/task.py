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

from sushy.resources import base


class MessagesField(base.ListField):
    message_id = base.Field("MessageId")
    """The message id"""

    related_properties = base.Field("RelatedProperties")
    """The message related properties"""

    message = base.Field("Message")
    """The message returned"""

    message_args = base.Field("MessageArgs")
    """The message args"""

    severity = base.Field("Severity")
    """The message severity"""


class Task(base.ResourceBase):
    identity = base.Field("Id")
    """The task identity"""

    name = base.Field("Name")
    """The task name"""

    description = base.Field("Description")
    """The task description"""

    task_state = base.Field("TaskState")
    """The task state"""

    start_time = base.Field("StartTime")
    """The task start time"""

    end_time = base.Field("EndTime")
    """The task end time"""

    task_status = base.Field("TaskStatus")
    """"The task status"""

    messages = MessagesField("Messages")
    """The task message"""

    def delete(self):
        """Delete this task"""
        self._conn.delete(self.path)


class TaskCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Task

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a Task Collection

        :param connector: A Connector instance
        :param path: The canonical path to the task collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(TaskCollection, self).__init__(connector,
                                             path,
                                             redfish_version)
