#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A User Device represents the final end-user of Aesel, and is always bound to
a computer, phone, or other piece of physical hardware.  These devices are
expected to send and recieve UDP messages (Events) from the Aesel servers.

:key: The Unique Identifier of the device.
:hostname: The hostname of the device.
:port: The port of the device.
:connection_string: The full URL of the device.
:transform: An AeselSceneTransform which can be passed in during Registration flows.
"""

"""
Apache2 License Notice
Copyright 2018 Alex Barry
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

class AeselUserDevice(object):
    def __init__(self):
        self.key = None
        self.hostname = None
        self.port = None
        self.connection_string = None
        self.transform = None
