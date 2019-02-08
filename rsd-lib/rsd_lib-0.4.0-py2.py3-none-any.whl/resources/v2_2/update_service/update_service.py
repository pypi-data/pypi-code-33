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

from rsd_lib.resources.v2_2.update_service import action_info
from rsd_lib import utils as rsd_lib_utils
from sushy.resources import base
from sushy import utils


class StatusField(base.CompositeField):
    state = base.Field("State")
    """The status state"""

    health = base.Field("Health", adapter=rsd_lib_utils.num_or_none)
    """The status health"""

    health_rollup = base.Field("HealthRollup",
                               adapter=rsd_lib_utils.num_or_none)
    """The status health rollup"""


class SimpleUpdateField(base.CompositeField):
    target = base.Field("target")
    """The simple update target"""


class ActionsField(base.CompositeField):
    simple_update = SimpleUpdateField("#UpdateService.SimpleUpdate")
    """The actions simple update"""

    oem = base.Field("Oem")
    """The actions oem"""


class UpdateService(base.ResourceBase):
    identity = base.Field("Id")
    """The update service identity"""

    name = base.Field("Name")
    """The update service name"""

    status = StatusField("Status")
    """The update service name"""

    service_enabled = base.Field("ServiceEnabled", adapter=bool)
    """Whether the update service is enabled"""

    actions = ActionsField("Actions")
    """The update service actions"""

    oem = base.Field("Oem")
    """The update service oem"""

    odata_context = base.Field("@odata.context")
    """The update service odata context"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a UpdateService

        :param connector: A Connector instance
        :param identity: The identity of the UpdateService resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(UpdateService, self).__init__(connector, identity,
                                            redfish_version)

    def _get_action_info_path(self):
        """Helper function to find the ActionInfo path"""
        return self.json.get("Actions").get("#UpdateService.SimpleUpdate").get(
            "@Redfish.ActionInfo")

    @property
    @utils.cache_it
    def action_info(self):
        """Property to provide reference to `ActionInfo` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return action_info.ActionInfo(
            self._conn, self._get_action_info_path(),
            redfish_version=self.redfish_version)
