#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A Scene Transform represents the transformation needed to move between two scenes,
or between a scene and the local coordinate system of a device.

:translation: A List of 3 floats, [x,y,z], which represent the translation.
:rotation: A list of 3 floats, [x,y,z], which represent the euler rotation.
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

class AeselSceneTransform(object):
    def __init__(self):
        self.translation = []
        self.rotation = []
