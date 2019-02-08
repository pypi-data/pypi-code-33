# Copyright (c) 2018 Intel, Corp.
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

from jsonschema import validate
import logging

from rsd_lib.resources.v2_1.node import node as v2_1_node
from rsd_lib.resources.v2_2.node import schemas as node_schemas


LOG = logging.getLogger(__name__)


class NodeCollection(v2_1_node.NodeCollection):

    def _create_compose_request(self, name=None, description=None,
                                processor_req=None, memory_req=None,
                                remote_drive_req=None, local_drive_req=None,
                                ethernet_interface_req=None,
                                security_req=None, total_system_core_req=None,
                                total_system_memory_req=None):

        request = {}

        if name is not None:
            request['Name'] = name
        if description is not None:
            request['Description'] = description

        if processor_req is not None:
            validate(processor_req,
                     node_schemas.processor_req_schema)
            request['Processors'] = processor_req

        if memory_req is not None:
            validate(memory_req,
                     node_schemas.memory_req_schema)
            request['Memory'] = memory_req

        if remote_drive_req is not None:
            validate(remote_drive_req,
                     node_schemas.remote_drive_req_schema)
            request['RemoteDrives'] = remote_drive_req

        if local_drive_req is not None:
            validate(local_drive_req,
                     node_schemas.local_drive_req_schema)
            request['LocalDrives'] = local_drive_req

        if ethernet_interface_req is not None:
            validate(ethernet_interface_req,
                     node_schemas.ethernet_interface_req_schema)
            request['EthernetInterfaces'] = ethernet_interface_req

        if security_req is not None:
            validate(security_req,
                     node_schemas.security_req_schema)
            request['Security'] = security_req

        if total_system_core_req is not None:
            validate(total_system_core_req,
                     node_schemas.total_system_core_req_schema)
            request['TotalSystemCoreCount'] = total_system_core_req

        if total_system_memory_req is not None:
            validate(total_system_memory_req,
                     node_schemas.total_system_memory_req_schema)
            request['TotalSystemMemoryMiB'] = total_system_memory_req

        return request

    def compose_node(self, name=None, description=None,
                     processor_req=None, memory_req=None,
                     remote_drive_req=None, local_drive_req=None,
                     ethernet_interface_req=None, security_req=None,
                     total_system_core_req=None, total_system_memory_req=None):
        """Compose a node from RackScale hardware

        :param name: Name of node
        :param description: Description of node
        :param processor_req: JSON for node processors
        :param memory_req: JSON for node memory modules
        :param remote_drive_req: JSON for node remote drives
        :param local_drive_req: JSON for node local drives
        :param ethernet_interface_req: JSON for node ethernet ports
        :param security_req: JSON for node security requirements
        :param total_system_core_req: Total processor cores available in
            composed node
        :param total_system_memory_req: Total memory available in composed node
        :returns: The location of the composed node

        When the 'processor_req' is not none: it need a computer system
        contains processors whose each processor meet all conditions in the
        value.

        When the 'total_system_core_req' is not none: it need a computer
        system contains processors whose cores sum up to number equal or
        greater than 'total_system_core_req'.

        When both values are not none: it need meet all conditions.

        'memory_req' and 'total_system_memory_req' is the same.
        """
        target_uri = self._get_compose_action_element().target_uri
        properties = self._create_compose_request(
            name=name, description=description,
            processor_req=processor_req,
            memory_req=memory_req,
            remote_drive_req=remote_drive_req,
            local_drive_req=local_drive_req,
            ethernet_interface_req=ethernet_interface_req,
            security_req=security_req,
            total_system_core_req=total_system_core_req,
            total_system_memory_req=total_system_memory_req)
        resp = self._conn.post(target_uri, data=properties)
        LOG.info("Node created at %s", resp.headers['Location'])
        node_url = resp.headers['Location']
        return node_url[node_url.find(self._path):]
