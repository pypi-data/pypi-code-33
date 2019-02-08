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


class LocationField(base.ListField):
    language = base.Field("Language")
    """The location language"""

    publication_uri = base.Field("PublicationUri")
    """The location publication uri"""


class Registries(base.ResourceBase):
    identity = base.Field("Id")
    """The registries identity"""

    name = base.Field("Name")
    """The registries name"""

    description = base.Field("Description")
    """The registries description"""

    languages = base.Field("Languages")
    """The registries languages"""

    registry = base.Field("Registry")
    """The registry"""

    location = LocationField("Location")
    """The registries location"""

    oem = base.Field("Oem")
    """The registries oem"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a Registries

        :param connector: A Connector instance
        :param identity: The identity of the registries resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(Registries, self).__init__(connector, identity, redfish_version)


class RegistriesCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Registries

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a RegistriesCollection

        :param connector: A Connector instance
        :param path: The canonical path to the registries collection
            resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(RegistriesCollection, self).__init__(connector, path,
                                                   redfish_version)
