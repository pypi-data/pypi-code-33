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

from sushy import utils

from rsd_lib.resources.v2_2.manager import manager
from rsd_lib.resources.v2_3.system import ethernet_interface


class Manager(manager.Manager):

    @property
    @utils.cache_it
    def ethernet_interfaces(self):
        """Property to provide reference to `EthernetInterfaceColection`

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        return ethernet_interface.EthernetInterfaceCollection(
            self._conn, self._get_ethernet_interfaces_path(),
            redfish_version=self.redfish_version)


class ManagerCollection(manager.ManagerCollection):

    @property
    def _resource_type(self):
        return Manager
