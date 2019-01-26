#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
The Main Client for accessing all
`HTTP Operations in the Aesel API <https://aesel.readthedocs.io/en/latest/pages/DVS_API.html>`__.
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

from aesel.model.AeselAssetMetadata import AeselAssetMetadata
from aesel.model.AeselAssetRelationship import AeselAssetRelationship
from aesel.model.AeselDataList import AeselDataList
from aesel.model.AeselObject import AeselObject
from aesel.model.AeselProperty import AeselProperty
from aesel.model.AeselScene import AeselScene
from aesel.model.AeselSceneGroup import AeselSceneGroup
from aesel.model.AeselSceneTransform import AeselSceneTransform
from aesel.model.AeselUserDevice import AeselUserDevice

import requests

class AeselTransactionClient(object):
    """
    Initializing the Transaction Client just requires the HTTP(s) address
    which it can use to communicate with the Aesel server.

    :param str aesel_url: The address of the Aesel servers.
    """
    def __init__(self, aesel_url):
        self.aesel_addr = aesel_url
        self.api_version = 'v1'

        # Start an HTTP Session
        # Includes a connection pool, and let's us set global auth attributes
        self.http_session = requests.session()

    # Internal method for generating the base URL String of the Aesel API
    def gen_base_url(self):
        return self.aesel_addr + "/" + self.api_version

    # Internal method for generating the Query Parameters for an Asset Request
    def gen_asset_params(self, asset, relationship):
        query_params = {}
        if asset is not None:
            query_params['content-type'] = asset.content_type
            query_params['asset-type'] = asset.asset_type
            query_params['file-type'] = asset.file_type
        if relationship is not None:
            query_params['related-id'] = relationship.related
            query_params['related-type'] = relationship.type
        return query_params

    # ------------------End User API Methods----------------------------

    # ------------------------------
    # Authentication & Users methods
    # ------------------------------

    def login(self, username, password):
        """
        Login to the Aesel server, storing the Authentication header from
        the response as a bearer token for future requests.

        :param str username: The username with which to login
        :param str password: The password with which to login
        """
        r = self.http_session.post(self.aesel_addr + "/login", json={"username": username, "password": password})

        # Throw an error for bad responses
        r.raise_for_status()

        # Add a header to the session with the returned auth token
        auth_token = r.headers['authorization']
        self.http_session.headers.update({"Authorization": "%s" % auth_token})

    def create_user(self, user):
        """
        Create a new user in the Aesel server.  Note that this will only be
        processed successfully if the logged-in user calling it is an administrator.

        :param user: The user to create
        """
        r = self.http_session.post(self.aesel_addr + "/users/sign-up", json=user.to_dict())

        # Throw an error for bad responses
        r.raise_for_status()

        return r.json()

    def user_query(self, username="", email=""):
        """
        Get an existing User from Aesel by Username or Email

        :param str username: The username to search for
        :param str email: The email to search for
        """
        query_params = {}
        if username != "":
            query_params["username"] = username
        elif email != "":
            query_params["email"] = email
        r = self.http_session.get(self.aesel_addr + "/users/", params=query_params)

        # Throw an error for bad responses
        r.raise_for_status()

        return r.json()

    def get_user(self, key):
        """
        Get an existing User from Aesel by Key

        :param str key: The username for the user
        """
        r = self.http_session.get(self.aesel_addr + "/users/" + key)

        # Throw an error for bad responses
        r.raise_for_status()

        return r.json()

    def update_user(self, key, user):
        """
        Update an existing user in the Aesel server.

        :param key: The key of the user to update
        :param user: The user to create
        """
        user.key = key
        r = self.http_session.put(self.aesel_addr + "/users/" + key, json=user.to_dict())

        # Throw an error for bad responses
        r.raise_for_status()

    def add_favorite_project(self, key, project_key):
        """
        Add a Favorite Project to an existing user in the Aesel server.

        :param key: The key of the user to update
        :param project_key: The key of the project to add to the favorites list
        """
        r = self.http_session.put(self.aesel_addr + "/users/" + key + "/projects/" + project_key)

        # Throw an error for bad responses
        r.raise_for_status()

    def remove_favorite_project(self, key, project_key):
        """
        Remove a Favorite Project from an existing user in the Aesel server.

        :param key: The key of the user to update
        :param project_key: The key of the project to remove from the favorites list
        """
        r = self.http_session.delete(self.aesel_addr + "/users/" + key + "/projects/" + project_key)

        # Throw an error for bad responses
        r.raise_for_status()

    def add_favorite_scene(self, key, scene_key):
        """
        Add a Favorite Scene to an existing user in the Aesel server.

        :param key: The key of the user to update
        :param project_key: The key of the scene to add to the favorites list
        """
        r = self.http_session.put(self.aesel_addr + "/users/" + key + "/scenes/" + scene_key)

        # Throw an error for bad responses
        r.raise_for_status()

    def remove_favorite_scene(self, key, scene_key):
        """
        Remove a Favorite Scene from an existing user in the Aesel server.

        :param key: The key of the user to update
        :param scene_key: The key of the scene to remove from the favorites list
        """
        r = self.http_session.delete(self.aesel_addr + "/users/" + key + "/scenes/" + scene_key)

        # Throw an error for bad responses
        r.raise_for_status()

    def make_user_admin(self, key):
        """
        Make a user an administrator.

        :param key: The key of the user to update
        """
        r = self.http_session.put(self.aesel_addr + "/users/" + key + "/admin")

        # Throw an error for bad responses
        r.raise_for_status()

    def remove_admin_rights(self, key):
        """
        Remove admin priveleges from a User.

        :param key: The key of the user to update
        """
        r = self.http_session.delete(self.aesel_addr + "/users/" + key + "/admin")

        # Throw an error for bad responses
        r.raise_for_status()

    def activate_user(self, key):
        """
        Activate an existing User.

        :param key: The key of the user to update
        """
        r = self.http_session.put(self.aesel_addr + "/users/" + key + "/active")

        # Throw an error for bad responses
        r.raise_for_status()

    def deactivate_user(self, key):
        """
        Deactivate a User.

        :param key: The key of the user to update
        """
        r = self.http_session.delete(self.aesel_addr + "/users/" + key + "/active")

        # Throw an error for bad responses
        r.raise_for_status()

    def delete_user(self, key):
        """
        Delete an existing User from Aesel by Key.

        :param str key: The username for the user
        """
        r = self.http_session.delete(self.aesel_addr + "/users/" + key)

        # Throw an error for bad responses
        r.raise_for_status()

    def set_auth_info(self, auth_token):
        """
        Set the authentication token to be used on Requests

        :param str auth_token: The value of the auth token to use on requests
        """
        self.http_session.headers.update({"Authorization": "Bearer %s" % auth_token})

    def set_cookie_header(self, cookie):
        """
        Set the cookies contained in the Transaction sessions.

        :param cookie: The text value of the desired Cookie header.
        """
        self.http_session.headers.update({"Cookie": "%s" % cookie})

    # ---------------
    # Project Methods
    # ---------------

    def create_project(self, project):
        """
        Create a new project in the Aesel server.

        :param project: AeselProject to be created.
        """
        r = self.http_session.post(self.gen_base_url() + "/project", json=project.to_dict())

        # Throw an error for bad responses
        r.raise_for_status()

        return r.json()

    def update_project(self, key, project):
        """
        Update an existing project in the Aesel server.

        :param str key: The key of the AeselProject to be updated.
        :param project: AeselProject to be updated.
        """
        r = self.http_session.post(self.gen_base_url() + "/project/" + key, json=project.to_dict())

        # Throw an error for bad responses
        r.raise_for_status()

    def add_scene_group(self, key, scene_group):
        """
        Add a scene group to an existing project in the Aesel server.

        :param str key: The key of the AeselProject to be updated.
        :param scene_group: AeselSceneGroup to add to the project.
        """
        r = self.http_session.post(self.gen_base_url() + "/project/" + key + "/groups", json=scene_group.to_dict())

        # Throw an error for bad responses
        r.raise_for_status()

    def update_scene_group(self, key, group_name, scene_group):
        """
        Update a scene group of an existing project in the Aesel server.

        :param str key: The key of the AeselProject to be updated.
        :param str group_name: The name of the scene group to update.
        :param scene_group: AeselSceneGroup to add to the project.
        """
        r = self.http_session.post(self.gen_base_url() + "/project/" + key + "/groups/" + group_name, json=scene_group.to_dict())

        # Throw an error for bad responses
        r.raise_for_status()

    def add_scene_to_scene_group(self, key, group_name, scene_key):
        """
        Add a scene to a scene group in the Aesel server.

        :param str key: The key of the AeselProject to be updated.
        :param str group_name: The name of the scene group to update.
        :param scene_key: The key of the AeselScene to add to the group.
        """
        r = self.http_session.put(self.gen_base_url() + "/project/" + key + "/groups/" + group_name + "/scenes/" + scene_key)

        # Throw an error for bad responses
        r.raise_for_status()

    def remove_scene_from_scene_group(self, key, group_name, scene_key):
        """
        Remove a scene from a scene group in the Aesel server.

        :param str key: The key of the AeselProject to be updated.
        :param str group_name: The name of the scene group to update.
        :param scene_key: The key of the AeselScene to add to the group.
        """
        r = self.http_session.delete(self.gen_base_url() + "/project/" + key + "/groups/" + group_name + "/scenes/" + scene_key)

        # Throw an error for bad responses
        r.raise_for_status()

    def delete_scene_group(self, key, group_name):
        """
        Delete a Scene Group from a Project in the Aesel server.

        :param str key: The key of the AeselProject to be updated.
        :param str group_name: The name of the scene group to update.
        """
        r = self.http_session.delete(self.gen_base_url() + "/project/" + key + "/groups/" + group_name)

        # Throw an error for bad responses
        r.raise_for_status()

    def get_project(self, key):
        """
        Get a project from the Aesel server by key.

        :param str key: The key of the AeselProject to be retrieved.
        """
        r = self.http_session.get(self.gen_base_url() + "/project/" + key)

        # Throw an error for bad responses
        r.raise_for_status()

        return r.json()

    def delete_project(self, key):
        """
        Delete a project from the Aesel server by key.

        :param str key: The key of the AeselProject to be deleted.
        """
        r = self.http_session.delete(self.gen_base_url() + "/project/" + key)

        # Throw an error for bad responses
        r.raise_for_status()

    def project_query(self, project, num_records=10, page=0):
        """
        Query projects from the Aesel server.

        :param project: The AeselProject to be used as a match query.
        :param num_records: The maximum number of records to return in the query.
        :param page: The page number of records to return, with num_records as the page size.
        """
        query_params = {"num_records": num_records, "page": page}
        if project.name is not None:
            query_params["name"] = project.name
        if project.description is not None:
            query_params["description"] = project.description
        if project.category is not None:
            query_params["category"] = project.category
        if len(project.tags) > 0:
            query_params["tags"] = project.tags

        r = self.http_session.get(self.gen_base_url() + "/project", params=query_params)

        # Throw an error for bad responses
        r.raise_for_status()

        return r.json()

    # ------------------------
    # Asset Collection Methods
    # ------------------------

    def create_asset_collection(self, collection):
        """
        Create a new Asset Collection in the Aesel server.

        :param collection: AeselAssetCollection to be created.
        """
        r = self.http_session.post(self.gen_base_url() + "/collection", json=collection.to_dict())

        # Throw an error for bad responses
        r.raise_for_status()

        return r.json()

    def update_asset_collection(self, key, collection):
        """
        Update an existing Asset Collection in the Aesel server.

        :param str key: The key of the AeselAssetCollection to be updated.
        :param collection: AeselAssetCollection to be updated.
        """
        r = self.http_session.post(self.gen_base_url() + "/collection/" + key, json=collection.to_dict())

        # Throw an error for bad responses
        r.raise_for_status()

    def get_asset_collection(self, key):
        """
        Get an Asset Collection from the Aesel server by key.

        :param str key: The key of the AeselAssetCollection to be retrieved.
        """
        r = self.http_session.get(self.gen_base_url() + "/collection/" + key)

        # Throw an error for bad responses
        r.raise_for_status()

        return r.json()

    def get_asset_collections(self, keys):
        """
        Get an Asset Collection from the Aesel server by key.

        :param keys: A list of keys for the AeselAssetCollections to be retrieved.
        """
        r = self.http_session.post(self.gen_base_url() + "/bulk/collection", json={"ids": keys})

        # Throw an error for bad responses
        r.raise_for_status()

        return r.json()

    def delete_asset_collection(self, key):
        """
        Delete an Asset Collection from the Aesel server by key.

        :param str key: The key of the AeselAssetCollection to be deleted.
        """
        r = self.http_session.delete(self.gen_base_url() + "/collection/" + key)

        # Throw an error for bad responses
        r.raise_for_status()

    def asset_collection_query(self, collection, num_records=10, page=0):
        """
        Query Asset Collections from the Aesel server.

        :param collection: The AeselAssetCollection to be used as a match query.
        :param num_records: The maximum number of records to return in the query.
        :param page: The page number of records to return, with num_records as the page size.
        """
        query_params = {"num_records": num_records, "page": page}
        if collection.name is not None:
            query_params["name"] = collection.name
        if collection.description is not None:
            query_params["description"] = collection.description
        if collection.category is not None:
            query_params["category"] = collection.category
        if len(collection.tags) > 0:
            query_params["tags"] = collection.tags

        r = self.http_session.get(self.gen_base_url() + "/collection", params=query_params)

        # Throw an error for bad responses
        r.raise_for_status()

        return r.json()

    # -------------
    # Asset Methods
    # -------------

    def create_asset(self, file, asset=None, relationship=None):
        """
        Create a New Asset in the Aesel Server.

        :param str file: The path to the file to save as an Asset
        :param asset: Optional AssetMetadata to associate with the Asset.
        :param relationship: Optional AssetRelationship to associate with the Asset.
        :return: The key of the newly created object.
        """
        # Set up query parameters
        query_params = self.gen_asset_params(asset, relationship)

        # Deduce the content-type
        content_type = "text/plain"
        if asset is not None:
            if asset.content_type is not None:
                content_type = asset.content_type

        # Send the HTTP Request
        request_file = {'file': (file, open(file, 'rb'), content_type, {'Expires': '0'})}
        r = self.http_session.post(self.gen_base_url() + "/asset", files=request_file, params=query_params, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the body text, which is the Asset ID
        return r.text

    def update_asset(self, key, file, asset=None, relationship=None):
        """
        Update an existing Asset in the Aesel Server.

        :param str file: The path to the file to save as an Asset
        :param asset: Optional AeselAssetMetadata to associate with the Asset.
        :param relationship: Optional AeselAssetRelationship to associate with the Asset.
        :return: The key of the newly created object.
        """
        # Set up query parameters
        query_params = self.gen_asset_params(asset, relationship)

        # Deduce the content-type
        content_type = "text/plain"
        if asset is not None:
            if asset.content_type is not None:
                content_type = asset.content_type

        # Send the HTTP Request
        request_file = {'file': (file, open(file, 'rb'), content_type, {'Expires': '0'})}
        r = self.http_session.post(self.gen_base_url() + "/asset/" + key, files=request_file, params=query_params, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the body text, which is the Asset ID
        return r.text

    def get_asset(self, key):
        """
        Get an Asset by Key, and return the content of the response.

        :param str key: The key of the Asset to retrieve
        :return: The content of the response, usually to be saved to a file.
        """
        # Send a get request
        r = self.http_session.get(self.gen_base_url() + "/asset/" + key, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the content of the response, which can be written to a file
        return r.content

    def query_asset_metadata(self, asset):
        """
        Query Assets by Metadata, and return the json content of the response.

        :param asset: The AeselAssetMetadata which will be used as a match query.
        :return: JSON containing a list of Asset Metadata entries, including keys.
        """
        # Set up query parameters
        query_params = self.gen_asset_params(asset, None)

        # Send a get request
        r = self.http_session.get(self.gen_base_url() + "/asset", params=query_params, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the content of the response, which can be written to a file
        return r.json()

    def bulk_query_asset_metadata(self, keys):
        """
        Query Asset Metadata by ID in bulk, and return the json content of the response.

        :param keys: A list of Asset Keys to retrieve the metadata of.
        :return: JSON containing a list of Asset Metadata entries.
        """
        # Send a get request
        r = self.http_session.post(self.gen_base_url() + "/bulk/asset", json={"ids": keys}, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the content of the response, which can be written to a file
        return r.json()

    def get_asset_history(self, key):
        """
        Get an Asset History by Key, and return the json content of the response.

        :param str key: The key of the Asset to retrieve the history for
        :return: JSON containing an Asset History corresponding to the requested Asset.
        """
        # Send a get request
        r = self.http_session.get(self.gen_base_url() + "/history/" + key, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the content of the response, which can be written to a file
        return r.json()

    def delete_asset(self, key):
        """
        Delete an Asset by Key.

        :param str key: The key of the Asset to delete
        """
        r = self.http_session.delete(self.gen_base_url() + "/asset/" + key, allow_redirects=True)
        r.raise_for_status()

    def save_asset_relationship(self, new_relationship, existing_relationship=None):
        """
        Add an Asset Relationship between the specified asset and related element

        :param new_relationship: The relationship to persist.
        :param existing_relationship: If we are updating, then what do we need to query on to find the existing relationship.
        :return: JSON containing the Relationship and ID.
        """
        query_params = {}
        if existing_relationship is not None:
            query_params['asset'] = existing_relationship.asset
            query_params['related'] = existing_relationship.related
            query_params['type'] = existing_relationship.type
            r = self.http_session.put(self.gen_base_url() + "/relationship", json=new_relationship.to_dict(), params=query_params)
        else:
            r = self.http_session.put(self.gen_base_url() + "/relationship", json=new_relationship.to_dict())

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def delete_asset_relationship(self, asset, type, related):
        """
        Delete an Asset Relationship

        :param str asset: The Asset key in the relationship to delete.
        :param str type: The type of the relationship to delete.
        :param str related: The related entity key in the relationship to delete.
        :return: JSON with deleted asset relationships.
        """
        query_params = {"asset": asset, "type": type, "related": related}
        r = self.http_session.delete(self.gen_base_url() + "/relationship", params=query_params, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def query_asset_relationships(self, query):
        """
        Query for asset relationships.

        :param query: The AeselAssetRelationship to use as a query.
        :return: JSON with a list of found asset relationships, including keys.
        """
        query_params = {}
        if query.asset is not None:
            query_params['asset'] = query.asset
        if query.related is not None:
            query_params['related'] = query.related
        if query.type is not None:
            query_params['type'] = query.type
        r = self.http_session.get(self.gen_base_url() + "/relationship", params=query_params, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    # -------------
    # Scene Methods
    # -------------

    def create_scene(self, key, scene):
        """
        Create a new Scene with the given key

        :param str key: The key of the Scene to create
        :param scene: The AeselScene to persist.
        :return: JSON with a list of created scenes.
        """
        data_list = AeselDataList()
        data_list.num_records = 1
        data_list.start_record = 0
        data_list.data.append(scene)
        r = self.http_session.put(self.gen_base_url() + "/scene/" + key, json=(data_list.to_dict("scenes")), allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def update_scene(self, key, scene):
        """
        Update an existing Scene with the given key

        :param str key: The key of the Scene to update
        :param scene: The AeselScene to persist.
        :return: JSON with a list of updated scenes.
        """
        data_list = AeselDataList()
        data_list.num_records = 1
        data_list.start_record = 0
        data_list.data.append(scene)
        r = self.http_session.post(self.gen_base_url() + "/scene/" + key, json=data_list.to_dict("scenes"), allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def get_scene(self, key):
        """
        Get a Scene with the given key

        :param str key: The key of the Scene to update
        :return: JSON with a list of retrieved scenes.
        """
        r = self.http_session.get(self.gen_base_url() + "/scene/" + key, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def delete_scene(self, key):
        """
        Delete a Scene with the given key

        :param str key: The key of the Scene to delete
        """
        r = self.http_session.delete(self.gen_base_url() + "/scene/" + key, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

    def bulk_scene_query(self, scenes, num_records=10, start_record=0):
        """
        Query for scenes by attribute.  Passing in multiple scenes will
        return the sum of the results of using each scene as a query.

        :param scenes: A list of AeselScenes to use as a query.
        :param num_records: How many records to retrieve.
        :param start_record: The first record to retrieve.  Works with num_records to support pagination.
        :return: JSON with a list of found scenes.
        """
        data_list = AeselDataList()
        data_list.num_records = num_records
        data_list.start_record = start_record
        data_list.data.extend(scenes)
        r = self.http_session.post(self.gen_base_url() + "/scene/query", json=data_list.to_dict("scenes"), allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def scene_query(self, scene, num_records=10, start_record=0):
        """
        Query for scenes by attribute.

        :param scene: An AeselScene to use as a query.
        :param num_records: How many records to retrieve.
        :param start_record: The first record to retrieve.  Works with num_records to support pagination.
        :return: JSON with a list of found scenes.
        """
        return self.bulk_scene_query([scene], num_records, start_record)

    def register(self, scene_key, device, transform=None):
        """
        Register a device to a scene.  Potentially with a transformation.

        :param str scene_key: The key of the AeselScene to register to.
        :param device: The AeselUserDevice which is registering.
        :param transform: The starting AeselSceneTransform to register.
        :return: JSON with a list of updated scenes.
        """
        data_list = AeselDataList()
        data_list.num_records = 2
        data_list.start_record = 0
        scene_data = AeselScene()
        scene_data.key = scene_key
        if transform is not None:
            device.transform = transform
        scene_data.devices.append(device)
        data_list.data.append(scene_data)

        # Send the request
        r = self.http_session.post(self.gen_base_url() + "/scene/" + scene_key + "/register", json=data_list.to_dict("scenes"), allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def deregister(self, scene_key, device_key):
        """
        Deregister a device from a scene.

        :param str scene_key: The key of the AeselScene to deregister from.
        :param str device: The key of the AeselUserDevice which is deregistering.
        :return: JSON with a list of updated scenes.
        """
        data_list = AeselDataList()
        data_list.num_records = 2
        data_list.start_record = 0
        scene_data = AeselScene()
        ud = AeselUserDevice()
        scene_data.key = scene_key
        ud.key = device_key
        scene_data.devices.append(ud)
        data_list.data.append(scene_data)

        # Send the request
        r = self.http_session.post(self.gen_base_url() + "/scene/" + scene_key + "/deregister", json=data_list.to_dict("scenes"), allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def synchronize(self, scene_key, device_key, transform):
        """
        Correct the device transformation relative to the scene.

        :param scene_key: The key of the AeselScene in the relationship.
        :param device_key: The key of the AeselUserDevice which is registered.
        :param transform: The updated transformation.
        :return: JSON with a list of updated scenes.
        """
        data_list = AeselDataList()
        data_list.num_records = 2
        data_list.start_record = 0
        scene_data = AeselScene()
        ud = AeselUserDevice()
        scene_data.key = scene_key
        ud.key = device_key
        ud.transform = transform
        scene_data.devices.append(ud)
        data_list.data.append(scene_data)

        # Send the request
        r = self.http_session.post(self.gen_base_url() + "/scene/" + scene_key + "/align", json=data_list.to_dict("scenes"), allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    # --------------
    # Object Methods
    # --------------

    def create_object(self, scene_key, obj):
        """
        Create a new Object.

        :param str scene_key: The key of the AeselScene the object is associated to.
        :param obj: The AeselObject to persist.
        :return: JSON with a list of created objects, including the newly generated key.
        """
        data_list = AeselDataList()
        data_list.num_records = 1
        data_list.start_record = 0
        data_list.data.append(obj)
        r = self.http_session.post(self.gen_base_url() + "/scene/" + scene_key + "/object", json=data_list.to_dict("objects"), allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def update_object(self, scene_key, obj_key, obj):
        """
        Create a new Object.

        :param str scene_key: The key of the AeselScene the object is associated to.
        :param str obj_key: The key of the AeselObject to update.
        :param obj: The AeselObject to persist.
        :return: JSON with a list of created objects, including the newly generated key.
        """
        data_list = AeselDataList()
        data_list.num_records = 1
        data_list.start_record = 0
        data_list.data.append(obj)
        r = self.http_session.post(self.gen_base_url() + "/scene/" + scene_key + "/object/" + obj_key, json=data_list.to_dict("objects"), allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def get_object(self, scene_key, obj_key):
        """
        Get an Object by key.

        :param str scene_key: The key of the AeselScene to find the object in.
        :param str obj_key: The key of the AeselObject to get.
        :return: JSON with a list of created objects, including the newly generated key.
        """
        r = self.http_session.get(self.gen_base_url() + "/scene/" + scene_key + "/object/" + obj_key, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def delete_object(self, scene_key, obj_key):
        """
        Delete an Object by key.

        :param str scene_key: The key of the AeselScene to find the object in.
        :param str obj_key: The key of the AeselObject to get.
        """
        r = self.http_session.delete(self.gen_base_url() + "/scene/" + scene_key + "/object/" + obj_key, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

    def object_query(self, scene_key, object, num_records=999):
        """
        Query for objects by scene and attribute.

        :param str scene_key: The key of the AeselScene to find objects in.
        :param object: The AeselObject to use as a query.
        :param num_records: How many records to retrieve.
        :return: JSON with a list of found scenes.
        """
        data_list = AeselDataList()
        data_list.num_records = num_records
        data_list.data.append(object)
        r = self.http_session.post(self.gen_base_url() + "/scene/" + scene_key + "/object/query", json=data_list.to_dict("objects"), allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def lock_object(self, scene_key, obj_key, device_key):
        """
        Lock an Object by key.

        :param str scene_key: The key of the AeselScene to find the object in.
        :param str obj_key: The key of the AeselObject to lock.
        :param str device_key: The key of the AeselUserDevice obtaining the lock.
        """
        query_params = {"device": device_key}
        r = self.http_session.get(self.gen_base_url() + "/scene/" + scene_key + "/object/" + obj_key + "/lock", params=query_params, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

    def unlock_object(self, scene_key, obj_key, device_key):
        """
        Unlock an Object by key.

        :param str scene_key: The key of the AeselScene to find the object in.
        :param str obj_key: The key of the AeselObject to unlock.
        :param str device_key: The key of the AeselUserDevice obtaining the lock.
        """
        query_params = {"device": device_key}
        r = self.http_session.delete(self.gen_base_url() + "/scene/" + scene_key + "/object/" + obj_key + "/lock", params=query_params, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

    # ----------------
    # Property Methods
    # ----------------

    def create_property(self, scene_key, property):
        """
        Create a new Property.

        :param str scene_key: The key of the AeselScene the object is associated to.
        :param property: The AeselProperty to persist.
        :return: JSON with a list of created properties, including the newly generated key.
        """
        data_list = AeselDataList()
        data_list.num_records = 1
        data_list.start_record = 0
        data_list.data.append(property)
        r = self.http_session.post(self.gen_base_url() + "/scene/" + scene_key + "/property", json=data_list.to_dict("properties"), allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def update_property(self, scene_key, property_key, property):
        """
        Create a new Property.

        :param str scene_key: The key of the AeselScene the object is associated to.
        :param str property_key: The key of the AeselProperty to update.
        :param property: The AeselProperty to persist.
        :return: JSON with a list of created properties, including the newly generated key.
        """
        data_list = AeselDataList()
        data_list.num_records = 1
        data_list.start_record = 0
        data_list.data.append(property)
        r = self.http_session.post(self.gen_base_url() + "/scene/" + scene_key + "/property/" + property_key, json=data_list.to_dict("properties"), allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def get_property(self, scene_key, property_key):
        """
        Get a Property by key.

        :param str scene_key: The key of the AeselScene to find the object in.
        :param str property_key: The key of the AeselProperty to get.
        :return: JSON with a list of created properties, including the newly generated key.
        """
        r = self.http_session.get(self.gen_base_url() + "/scene/" + scene_key + "/property/" + property_key, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()

    def delete_property(self, scene_key, property_key):
        """
        Delete an Property by key.

        :param str scene_key: The key of the AeselScene to find the object in.
        :param str property_key: The key of the AeselProperty to get.
        """
        r = self.http_session.delete(self.gen_base_url() + "/scene/" + scene_key + "/property/" + property_key, allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

    def property_query(self, scene_key, property, num_records=999):
        """
        Query for properties by scene and attribute.

        :param str scene_key: The key of the AeselScene to find objects in.
        :param property: The AeselProperty to use as a query.
        :param num_records: How many records to retrieve.
        :return: JSON with a list of found scenes.
        """
        data_list = AeselDataList()
        data_list.num_records = num_records
        data_list.data.append(property)
        r = self.http_session.post(self.gen_base_url() + "/scene/" + scene_key + "/property/query", json=data_list.to_dict("properties"), allow_redirects=True)

        # Throw an error for bad responses
        r.raise_for_status()

        # Return the json content of the response
        return r.json()
