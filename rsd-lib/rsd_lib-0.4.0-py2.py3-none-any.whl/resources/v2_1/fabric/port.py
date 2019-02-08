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

import logging

from sushy import exceptions
from sushy.resources import base
from sushy.resources import common
from sushy import utils

LOG = logging.getLogger(__name__)


class StatusField(base.CompositeField):
    state = base.Field("State")
    """The status state"""

    health = base.Field("Health")
    """The status health"""


class ActionsField(base.CompositeField):
    reset = common.ResetActionField("#Port.Reset")
    """The action port reset"""


class LinksField(base.CompositeField):
    associated_endpoints = base.Field("AssociatedEndpoints", default=[],
                                      adapter=utils.get_members_identities)
    """The link associated endpoints"""


class IntelRackScaleField(base.CompositeField):
    odata_type = base.Field("@odata.type")
    """The Intel Rack Scale odata type"""

    pcie_connection_id = base.Field("PCIeConnectionId")
    """The Intel Rack Scale PCIe Connection Id"""


class OemField(base.CompositeField):
    intel_rackScale = IntelRackScaleField("Intel_RackScale")
    """The oem intel rack scale"""


class Port(base.ResourceBase):
    identity = base.Field("Id")
    """The port identity string"""

    name = base.Field("Name")
    """The port name"""

    description = base.Field("Description")
    """The port description"""

    status = StatusField("Status")
    """The port status"""

    port_id = base.Field("PortId")
    """The port id"""

    port_protocol = base.Field("PortProtocol")
    """The port protocol"""

    port_type = base.Field("PortType")
    """The port type"""

    current_speed_gbps = base.Field("CurrentSpeedGbps")
    """The port current speed Gbps"""

    width = base.Field("Width")
    """The port width"""

    max_speed_gbps = base.Field("MaxSpeedGbps")
    """The port max speed gbps"""

    actions = ActionsField("Actions")
    """The port actions"""

    oem = OemField("Oem")
    """The port oem"""

    links = LinksField("Links")
    """The port links"""

    def __init__(self, connector, identity, redfish_version=None):
        """A class representing a Port

        :param connector: A Connector instance
        :param identity: The identity of the Port resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(Port, self).__init__(connector, identity,
                                   redfish_version)

    def _get_reset_action_element(self):
        reset_action = self.actions.reset
        if not reset_action:
            raise exceptions.MissingActionError(action='#Port.Reset',
                                                resource=self._path)
        return reset_action

    def get_allowed_reset_port_values(self):
        """Get the allowed values for resetting the port.

        :returns: A set with the allowed values.
        """
        reset_action = self._get_reset_action_element()

        return reset_action.allowed_values

    def reset_port(self, value):
        """Reset the port.

        :param value: The target value.
        :raises: InvalidParameterValueError, if the target value is not
            allowed.
        """
        valid_resets = self.get_allowed_reset_port_values()
        if value not in valid_resets:
            raise exceptions.InvalidParameterValueError(
                parameter='value', value=value, valid_values=valid_resets)

        target_uri = self._get_reset_action_element().target_uri

        self._conn.post(target_uri, data={'ResetType': value})


class PortCollection(base.ResourceCollectionBase):
    @property
    def _resource_type(self):
        return Port

    def __init__(self, connector, path, redfish_version=None):
        """A class representing a Port

        :param connector: A Connector instance
        :param path: The canonical path to the Port collection resource
        :param redfish_version: The version of RedFish. Used to construct
            the object according to schema of the given version.
        """
        super(PortCollection, self).__init__(connector, path, redfish_version)
