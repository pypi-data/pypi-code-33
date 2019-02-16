#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
A Project has a set of Scene Groups, as well as a set of asset collections.
They are meant to help end-users organize their work in Aesel to correspond
with real-life projects (ie. a movie or game) being worked on.

:key: The Unique ID of the project, assigned by Aesel.
:name: The Name of the project.
:description: A readable description of the project.
:category: The category of the project.
:tags: Comma-delimited list of searchable tags for the project.
:sceneGroups: A list of scene groups which make up the project.
:assetCollectionIds: A list of asset collections which make up the project.
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

class AeselAssetCollection(object):
    def __init__(self):
        self.key = None
        self.name = None
        self.description = None
        self.category = None
        self.tags = []
        self.isPublic = None
        self.user = None

    def to_dict(self):
        return copy.deepcopy(vars(self))
