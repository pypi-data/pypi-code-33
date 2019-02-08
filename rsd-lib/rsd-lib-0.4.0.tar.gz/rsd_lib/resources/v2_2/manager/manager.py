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

from rsd_lib.resources.v2_1.manager import manager as v2_1_manager


class ManagerResetFiled(base.CompositeField):
    target = base.Field("target")
    """The manager reset target"""


class ActionsField(base.CompositeField):
    manager_reset = ManagerResetFiled("#Manager.Reset")
    """The actions manager reset """


class Manager(v2_1_manager.Manager):

    actions = ActionsField("Actions")
    """The manager actions"""


class ManagerCollection(base.ResourceCollectionBase):

    description = base.Field("Description")
    """The manager collection description"""

    @property
    def _resource_type(self):
        return Manager

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a Manager Collection

        :param connector: A Connector instance
        :param path: The canonical path to the chassis collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ManagerCollection, self).__init__(connector,
                                                path,
                                                redfish_version)
