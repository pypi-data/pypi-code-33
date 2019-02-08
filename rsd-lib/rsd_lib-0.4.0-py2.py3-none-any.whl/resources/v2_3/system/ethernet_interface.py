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

from rsd_lib.resources.v2_1.system import ethernet_interface
from rsd_lib import utils as rsd_lib_utils


class IntelRackScaleField(base.CompositeField):
    supported_protocols = base.Field("SupportedProtocols")
    """"This property shall represent an array of supported protocol types
        by the Ethernet interface.
    """


class OemField(base.CompositeField):
    intel_rackscale = IntelRackScaleField("Intel_RackScale")
    """The Oem Intel_RackScale"""


class LinksIntelRackScaleField(base.CompositeField):
    neighbor_port = base.Field("NeighborPort",
                               adapter=rsd_lib_utils.get_resource_identity)
    """The neighbor port of Rack ScaleIntel"""


class LinksOemField(base.CompositeField):
    intel_rackscale = LinksIntelRackScaleField("Intel_RackScale")
    """The Oem Intel_RackScale"""


class LinksField(base.CompositeField):
    oem = LinksOemField("Oem")
    """"The oem of Links"""

    endpoints = base.Field(
        "Endpoints", adapter=rsd_lib_utils.get_resource_identity)
    """The value of this property shall be a reference to the resources that
       this ethernet interface is associated with and shall reference a
       resource of type Endpoint.
    """


class EthernetInterface(ethernet_interface.EthernetInterface):

    uefi_device_path = base.Field('UefiDevicePath')
    """The value of the property shall be the UEFI device path to the device
       that implements the interface (port).
    """

    oem = OemField("Oem")
    """"The oem fields of Ethernet Interface"""

    links = LinksField("Links")
    """The EthernetInterface links"""


class EthernetInterfaceCollection(ethernet_interface.
                                  EthernetInterfaceCollection):

    @property
    def _resource_type(self):
        return EthernetInterface

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a EthernetInterface Collection

        :param connector: A Connector instance
        :param path: The canonical path to the EthernetInterface collection
            resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """

        super(EthernetInterfaceCollection, self).__init__(connector,
                                                          path,
                                                          redfish_version)
