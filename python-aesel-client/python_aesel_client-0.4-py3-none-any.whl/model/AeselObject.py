#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
An Object is represented by a transformation matrix representing it’s position
in 3-space, as well as a collection of Assets (Mesh files, Texture files,
Shader scripts, etc.). Objects are meant to be interacted with by individual
devices, and these changes will be streamed to all devices via the
Event API. This API exposes CRUD and Query operations for Objects.

Objects may also have a frame/timestamp, as well as animation graph handles.
Both of these are, however, optional.

:key: The Unique ID of the Object, assigned by Aesel.
:name: The Name of the Object.
:scene: The ID of the Scene which contains the Object.
:type: The type of the object (ie. "mesh", "curve", etc).
:subtype: The subtype of the object (ie. "cube", "sphere", etc).
:frame: The integer frame of the object
:timestamp: The integer timestamp of the object (in ms since the Unix Epoch).
:transform: The transformation matrix of the object, in a single array.  The first four elements make up the first row of the matrix, and this pattern continues.
:translation: An array of 3 floats, for the translation of the object (ie. [x,y,z]).
:euler_rotation: An array of 3 floats, for the euler rotation of the object (ie. [x,y,z]).
:quaternion_rotation: An array of 4 floats, for the quaternion rotation of the object (ie. [w,x,y,z]).
:scale: An array of 3 floats, for the scale of the object (ie. [x,y,z]).
:translation_handle: An array of AnimationGraphHandle's which correspond to the [x,y,z] values in the translation array.
:rotation_handle: An array of 4 AnimationGraphHandle's which correspond to the [w,x,y,z] values in the rotation arrays.
:scale_handle: An array of 3 AnimationGraphHandle's which correspond to the [x,y,z] values in the scale array.
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

import copy
import json

class AeselObject(object):
    def __init__(self):
        self.key = None
        self.name = None
        self.scene = None
        self.type = None
        self.subtype = None
        self.frame = None
        self.timestamp = None
        self.transform = []
        self.translation = []
        self.euler_rotation = []
        self.quaternion_rotation = []
        self.scale = []
        self.translation_handle = None
        self.rotation_handle = None
        self.scale_handle = None

    def to_dict(self):
        return_dict = copy.deepcopy(vars(self))
        if self.translation_handle is not None:
            return_dict['translation_handle'] = vars(self.translation_handle)
            return_dict['rotation_handle'] = vars(self.rotation_handle)
            return_dict['scale_handle'] = vars(self.scale_handle)
        return return_dict

    def to_transform_json(self):
        msg_dict = {
                    "msg_type": 1,
                    "key":self.key,
                    "name":self.name,
                    "frame":self.frame,
                    "scene":self.scene,
                    "transform": self.transform
                    }
        if self.translation_handle is not None:
            msg_dict['translation_handle'] = vars(self.translation_handle)
        if self.rotation_handle is not None:
            msg_dict['rotation_handle'] = vars(self.rotation_handle)
        if self.scale_handle is not None:
            msg_dict['scale_handle'] = vars(self.scale_handle)
        return json.dumps(msg_dict)
