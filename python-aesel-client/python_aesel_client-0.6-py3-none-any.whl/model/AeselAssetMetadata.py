#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
An asset is a resource that each device will need in order to accurately depict
objects around it. This can vary, from an .obj file, containing mesh information,
to a .glsl file, containing shader information, to a .png or .jpg file containing
an image. Assets can either be associated to a Scene or an Object.

Asset Metadata is stored as part of an Asset, and can be queried separately.

:content_type: The HTTP Content Type to store instead of multipart
:file_type: The File Extension of the uploaded file
:asset_type: The type of asset being stored (defaults to "standard")
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

class AeselAssetMetadata(object):
    def __init__(self):
        self.name = None
        self.file_type = None
        self.content_type = None
        self.asset_type = None
        self.isPublic = None
        self.user = None

    def to_dict(self):
        return copy.deepcopy(vars(self))
