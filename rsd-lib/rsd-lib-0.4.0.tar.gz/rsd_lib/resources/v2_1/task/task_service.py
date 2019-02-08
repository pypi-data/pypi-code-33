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

from rsd_lib.resources.v2_1.task import task
from sushy.resources import base
from sushy import utils


class StatusField(base.CompositeField):
    state = base.Field("State")
    """The status state"""

    health = base.Field("Health")
    """The status health"""


class TaskService(base.ResourceBase):
    identity = base.Field("Id")
    """The task service identity"""

    name = base.Field("Name")
    """The task service name"""

    date_time = base.Field("DateTime")
    """The task service date time"""

    completed_task_overwrite_policy = base.Field(
        "CompletedTaskOverWritePolicy")
    """The task service date completed task overwrite policy"""

    life_cycle_event_on_task_state_change = base.Field(
        "LifeCycleEventOnTaskStateChange", adapter=bool)
    """Whether the task service cycle event on task state change"""

    status = StatusField("Status")
    """The task service status"""

    service_enabled = base.Field("ServiceEnabled", adapter=bool)
    """Whether the task service is enabled"""

    oem = base.Field("Oem")
    """The task service oem"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a TaskService

        :param connector: A Connector instance
        :param identity: The identity of the TaskService resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(TaskService, self).__init__(connector, identity, redfish_version)

    def _get_task_collection_path(self):
        """Helper function to find the TaskCollection path"""
        return utils.get_sub_resource_path_by(self, 'Tasks')

    @property
    @utils.cache_it
    def tasks(self):
        """Property to provide reference to `TaskCollection` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return task.TaskCollection(
            self._conn, self._get_task_collection_path(),
            redfish_version=self.redfish_version)
