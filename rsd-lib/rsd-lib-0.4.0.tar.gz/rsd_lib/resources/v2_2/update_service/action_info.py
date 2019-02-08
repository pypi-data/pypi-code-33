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
from sushy import utils

NAME_MAPPING = {
    "Name": "name",
    "Required": "required",
    "DataType": "data_type",
    "AllowableValues": "allowable_values"
}


class ActionInfo(base.ResourceBase):
    oem = base.Field("Oem")
    """The action info oem"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a ActionInfo

        :param connector: A Connector instance
        :param identity: The identity of the ActionInfo resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(ActionInfo, self).__init__(
            connector, identity, redfish_version)

    @property
    @utils.cache_it
    def parameters(self):
        """Property to provide reference to `ActionInfo` instance

        It is calculated once when it is queried for the first time. On
        refresh, this property is reset.
        """
        parameters = []
        for i in self.json.get('Parameters'):
            item = {}
            for key in i.keys():
                item[NAME_MAPPING[key]] = i.get(key, None)
            parameters.append(item)

        return parameters
