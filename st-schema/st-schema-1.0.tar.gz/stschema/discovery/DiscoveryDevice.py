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

# Class representing a device in ST schema
class DiscoveryDevice:
    def __init__(self, id, friendlyName, deviceHandlerType):
        self.externalDeviceId = id
        self.friendlyName = friendlyName
        self.deviceHandlerType = deviceHandlerType

    # Set manufacturer name of the device
    def manufacturerName(self, name):
        try:
            self.manufacturerInfo
        except:
            self.manufacturerInfo = {}
        self.manufacturerInfo['manufacturerName'] = name

    # Set model name of the device
    def modelName(self, name):
        try:
            self.manufacturerInfo
        except:
            self.manufacturerInfo = {}
        self.manufacturerInfo['modelName'] = name

    # Set hardware version of the device
    def hwVersion(self, version):
        try:
            self.manufacturerInfo
        except:
            self.manufacturerInfo = {}
        self.manufacturerInfo['hwVersion'] = version

    # Set software version of the device
    def swVersion(self, version):
        try:
            self.manufacturerInfo
        except:
            self.manufacturerInfo = {}
        self.manufacturerInfo['swVersion'] = version

    # Set room name of the device
    def roomName(self, name):
        try:
            self.deviceContext
        except:
            self.deviceContext = {}
        self.deviceContext['roomName'] = name

    # Add a group to the device
    def addGroup(self, groupName):
        try:
            self.deviceContext
        except:
            self.deviceContext = {}
        try:
            self.deviceContext['groups']
        except:
            self.deviceContext['groups'] = []
        self.deviceContext['groups'].append(groupName)

    # Add a category to the device
    def addCategory(self, categoryName):
        try:
            self.deviceContext
        except:
            self.deviceContext = {}
        try:
            self.deviceContext['category']
        except:
            self.deviceContext['category'] = []
        self.deviceContext['category'].append(categoryName)
