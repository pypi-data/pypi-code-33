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
#   Class representing a device
#   @class StateDevice

class StateDevice:
    def __init__(self, externalDeviceId):
        self.externalDeviceId = externalDeviceId

    # Add a state to the device
    def addState(self, component, capability, attribute, value):
        try:
            self.states
        except:
            self.states = []

        state = {
            "component": component,
            "capability": capability,
            "attribute": attribute,
            "value": value
        }

        self.states.append(state)
