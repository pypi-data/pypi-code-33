#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
n Asset Relationship is a link between an asset and any other data entity which
is identifiable by a unique ID. Each relationship contains an Asset ID and a
Related ID, as well as a Relationship Type. These are used to model relationships
with both external sources (such as Scenes and Objects), and between assets
(such as having one Asset be the thumbnail of another).

:asset: The ID of the Asset specified in the Relationship.
:related: The ID of the Related entity in the Relationship.
:type: The type of Relationship (ie. "scene", "property", "object", etc).
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

class AeselAssetRelationship(object):
    def __init__(self):
        self.asset = None
        self.asset_sub_id = None
        self.related = None
        self.type = None
        self.subtype = None

    def to_dict(self):
        return {
                    "assetId": self.asset,
                    "assetSubId": self.asset_sub_id,
                    "relationshipType": self.type,
                    "relationshipSubtype": self.subtype,
                    "relatedId": self.related
                }
