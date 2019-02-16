# -*- coding: utf-8 -*-

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

import pytest
import time

from aesel.model.AeselAssetMetadata import AeselAssetMetadata
from aesel.model.AeselAssetRelationship import AeselAssetRelationship
from aesel.model.AeselGraphHandle import AeselGraphHandle
from aesel.model.AeselObject import AeselObject
from aesel.model.AeselProperty import AeselProperty
from aesel.model.AeselPropertyValue import AeselPropertyValue
from aesel.model.AeselScene import AeselScene
from aesel.model.AeselSceneTransform import AeselSceneTransform
from aesel.model.AeselUserDevice import AeselUserDevice

from aesel.AeselTransactionClient import AeselTransactionClient
from aesel.AeselEventClient import AeselEventClient

# Initial setup of Transaction client
@pytest.fixture
def transaction_client():
    return AeselTransactionClient("http://localhost:8080")

# Initial Setup of Event Client
@pytest.fixture
def event_client():
    return AeselEventClient("localhost", 8762)

# Execute tests on the Property API
def test_property_events(transaction_client, event_client):
    print("Testing Property API")

    # Create a Scene
    print("Creating base scene")
    scn = AeselScene()
    scn.name = "test"
    scn.region = "US-MD"
    scn.latitude = 100.0
    scn.longitude = 100.0
    scn.tags = []
    scn.devices = []
    scn_crt_resp = None
    try:
        scn_crt_resp = transaction_client.create_scene("propEventScene", scn)
    except Exception as e:
        print(e)
        assert(False)
    print(scn_crt_resp)

    # Create a new Property
    print("Create Property")
    prop = AeselProperty()
    prop.name = "testProperty"
    prop.scene = "propEventScene"
    prop.frame = 0
    val = AeselPropertyValue()
    val.value = 100.0
    prop.values.append(val)
    prop_crt_resp = None
    try:
        prop_crt_resp = transaction_client.create_property("propTestScene", prop)
    except Exception as e:
        print(e)
        assert(False)
    print(prop_crt_resp)
    assert(len(prop_crt_resp["properties"]) > 0)
    assert(len(prop_crt_resp["properties"][0]["key"]) > 0)
    prop_key = prop_crt_resp["properties"][0]["key"]

    # Send event
    print("Send Property Event")
    evt_prop = AeselProperty()
    evt_prop.key = prop_key
    evt_prop.scene = "propEventScene"
    evt_prop.frame = 0
    evt_val = AeselPropertyValue()
    evt_val.value = 110.0
    evt_prop.values.append(evt_val)
    event_client.send_property_update(evt_prop)

    # Wait for event to process
    time.sleep(1)

    # Check to make sure that the property value is updated
    print("Check Property")
    prop_get_resp = None
    try:
        prop_get_resp = transaction_client.get_property("propEventScene", prop_key)
    except Exception as e:
        print(e)
        assert(False)
    print(prop_get_resp)
    assert(len(prop_get_resp["properties"]) > 0)
    assert(abs(prop_get_resp["properties"][0]["values"][0]["value"] - 110.0) < 0.001)

    # Delete a Property
    print("Delete Property")
    try:
        transaction_client.delete_property("propTestScene", prop_key)
    except Exception as e:
        print(e)
        assert(False)

# Execute tests on the Object API
def test_object_events(transaction_client, event_client):
    print("Testing Object API")

    # Create a Scene
    print("Creating base scene")
    scn = AeselScene()
    scn.name = "test"
    scn.region = "US-MD"
    scn.latitude = 100.0
    scn.longitude = 100.0
    scn.tags = []
    scn.devices = []
    scn_crt_resp = None
    try:
        scn_crt_resp = transaction_client.create_scene("objEventScene", scn)
    except Exception as e:
        print(e)
        assert(False)
    print(scn_crt_resp)

    # Create a new Object
    print("Create Object")
    obj = AeselObject()
    obj.name = "testObject"
    obj.scene = "objEventScene"
    obj.type = "mesh"
    obj.subtype = "cube"
    obj.frame = 0
    obj.translation = [1, 1, 1]
    obj_crt_resp = None
    try:
        obj_crt_resp = transaction_client.create_object("objEventScene", obj)
    except Exception as e:
        print(e)
        assert(False)
    print(obj_crt_resp)
    assert(len(obj_crt_resp["objects"]) > 0)
    assert(len(obj_crt_resp["objects"][0]["key"]) > 0)
    obj_key = obj_crt_resp["objects"][0]["key"]

    # Send Event
    print("Send Object Event")
    evt_obj = AeselObject()
    evt_obj.key = obj_key
    evt_obj.scene = "objEventScene"
    evt_obj.transform = [2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0]
    event_client.send_object_update(evt_obj)

    # Wait for event to process
    time.sleep(1)

    # Check the current object transform to make sure it updated correctly
    print("Check object event")
    obj_get_resp = None
    try:
        obj_get_resp = transaction_client.get_object("objEventScene", obj_key)
    except Exception as e:
        print(e)
        assert(False)
    print(obj_get_resp)
    assert(len(obj_get_resp["objects"]) > 0)
    assert(abs(obj_get_resp["objects"][0]["transform"][0] - 2.0 < 0.001))

    # Delete an Object
    print("Delete Object")
    try:
        transaction_client.delete_object("objTestScene", obj_key)
    except Exception as e:
        print(e)
        assert(False)
