# Copyright 2018 Intel, Inc.
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

from sushy import utils

from rsd_lib.resources.v2_2.system import system
from rsd_lib.resources.v2_3.system import ethernet_interface


class System(system.System):

    @property
    @utils.cache_it
    def ethernet_interfaces(self):
        """Property to provide reference to `EthernetInterfaceCollection`

        It is calculated once the first time it is queried. On refresh,
        this property is reset.
        """
        return ethernet_interface.EthernetInterfaceCollection(
            self._conn, self._get_ethernet_interfaces_collection_path(),
            redfish_version=self.redfish_version)


class SystemCollection(system.SystemCollection):

    @property
    def _resource_type(self):
        return System
