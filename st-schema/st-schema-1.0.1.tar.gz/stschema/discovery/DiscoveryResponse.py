#
#	Copyright 2019 SmartThings
#
#	Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
#	in compliance with the License. You may obtain a copy of the License at:
#
#		http://www.apache.org/licenses/LICENSE-2.0
#
#	Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
#	on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License
#	for the specific language governing permissions and limitations under the License.
#

import json, ast
import stschema.STBase as STBase
from stschema.discovery.DiscoveryDevice import DiscoveryDevice as Device

# Class representing a discovery response in ST schema
class DiscoveryResponse(STBase.STBase):
    def __init__(self, schema, version, requestId):
        super().__init__(schema, version, "discoveryResponse", requestId)

    # Add a device to discovery response
    def addDevice(self, id, friendlyName, deviceHandlerType):
        try:
            self.devices
        except:
            self.devices = []
        device = Device(id, friendlyName, deviceHandlerType)
        return device

    def push(self, device):
        try:
            self.devices.append(ast.literal_eval(json.dumps(device.__dict__)))
        except:
            print("No available devices to push")
