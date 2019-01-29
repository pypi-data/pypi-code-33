# -*- coding: utf-8 -*-
#   *******************************************************
#   amieci - python client for amie.ai
#
#   Sign up for free at http://www.amie.ai
#   Copyright (C) 2017-2019 amie ivs
#   This file can not be copied and/or distributed without the express
#   permission of amie ivs.
#   *******************************************************

"""
Authors: Johannes Beil, Giulio Ungaretti

This module contains classes to communicate with the amie API

"""




import base64
import io
import json
import logging
import mimetypes
import os
import random
import time
import uuid
from collections import OrderedDict

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from amieci.exceptions import (ApiKeyNotFound, CurrentLeafNotSaved,
                               CurrentTreeNotSaved, CurrentTreeNotSet,
                               DatafileNotValid, LeafAlreadySaved,
                               LeafDoesNotExist, LeafNotValid,
                               MismatchedParent, TreeAlreadySaved,
                               TreeNotValid)

LOG_LEVEL = os.environ.get("AMIECI_LOGLEVEL", "INFO")
LOG_MSG_FORMAT = "amieci %(levelname)s: %(message)s"
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)


class CustomEncoder(json.JSONEncoder):
    """
    Mixin class that uses a to_json method on objects that are not by default
    json serializable
    """
    def default(self, o):  # pylint: disable=method-hidden
        try:
            return o.to_json()
        except AttributeError as exception:
            LOGGER.error(exception)
            return json.JSONEncoder.default(self, o)


def _post_json(url, endpoint, session, body):
    response = session.post(
        url="{:s}{:s}".format(url, endpoint),
        data=json.dumps(body, cls=CustomEncoder))
    response.raise_for_status()
    return response

def _post(url, endpoint, session, body):
    response = session.post(url="{:s}{:s}".format(url, endpoint), data=body)
    response.raise_for_status()
    return response



def _get_query(url, endpoint, session, params):
    response = session.get(url="{:s}{:s}".format(url, endpoint), params=params)
    response.raise_for_status()
    return response


def _get(url, endpoint, session):
    response = session.get(url="{:s}{:s}".format(url, endpoint))
    response.raise_for_status()
    return response


class API:
    """A api object holding the login and data information for a single user"""

    def __init__(self,
                 url: str,
                 key: str = None) -> None:
        """Initialize with login or registration information

        Args:
            password (str)      : min 6 character password
            email (str)         : unique email of the user
            url (str)           : url to the server
            stay_logged_in      : whether or not to keep the user logged-in

        """
        if key is None:
            try:
                key = os.environ["AMIECI_API_KEY"]
            except KeyError:
                LOGGER.error("key was not provided nor found in your enviroment, read how to get started here")
                raise  ApiKeyNotFound
        self.url = url
        self._reference_endpoint = "/reference"
        self._tree_endpoint = "/tree"
        self._tree_share_endpoint = "/tree/share/{:s}"
        self._post_leaf_endpoint = "/leaf"
        self._post_team_endpoint = "/team"
        self._post_team_member_endpoint = "/team/add"
        self._edge_endpoint = "/edge"
        self._upload_endpoint = "/upload"
        self._garden_endpoint = "/garden/{:d}"
        self._get_leaf_endpoint = "/leaf/{:d}/{:s}"
        self._session = requests.Session()
        self._session.mount(
            url,
            HTTPAdapter(
                max_retries=Retry(
                    total=3,
                    backoff_factor=2,
                    method_whitelist=False,
                    status_forcelist=[500, 502, 503, 504],
                )))
        resp = _post(self.url, "/client/auth", self._session, key).json()
        self._user_id = resp["user"]["user_id"]
        self._username = resp["user"]["username"]

    def get_garden(self):
        """Get all trees for the user
        Returns :
            tree (dict) : parsed JSON response from the server or an error message
          Example :
            {"trees": {"9a1662f9-20fb-43be-a442-aca7314f2236":
                  {"tree_id": "9a1662f9-20fb-43be-a442-aca7314f2236",
                  "color": "#E6A0C4",
                  "user_id": 16,
                  "leaves": [
                  "68ad05a6-dff6-40fb-873d-46d51fe71457",
                  "1cd789dc-1c65-4abb-b949-8b2811572b40"],
                  "edges": [{ "edge_id" : 1,
                  "parent_id" :  "68ad05a6-dff6-40fb-873d-46d51fe71457",
                  "child_id": "1cd789dc-1c65-4abb-b949-8b2811572b40",
                  "tree_id": "1cd789dc-1c65-4abb-b949-8b2811572b40"
                       }
                     ]
                  }
            }
        """
        endpoint = self._garden_endpoint.format(self._user_id)
        return _get(self.url, endpoint, self._session).json()

    def get_leaf(self, leaf_id):
        """ get the leaf with the given leaf_id

        Args :
            leaf_id (str) : Id of the specific leaf one wants to get

        Returns
            leaf (dict) : a leaf dict

        """
        endpoint = self._get_leaf_endpoint.format(self._user_id, leaf_id)
        return _get(self.url, endpoint, self._session).json()

    def post_ref(self, reference):
        """Add a reference. All reference information will be given in the new_ref dict

        Args :
            reference (dict) : dict specifying the new reference
                Example:{"user_id":16,
                         "parent_id":"9a1662f9-20fb-43be-a442-aca7314f2236",
                         "child_id": "1a1662f9-20fb-43be-a442-aca7314f2236",
                         "tree_id": "1a1662f9-20fb-43be-a442-aca7314f2236"}
        """
        _post_json(self.url, self._reference_endpoint, self._session,
                   reference)

    def post_edge(self, edge):
        """Add an edge. All edge information will be given in the new_edge dict

        Args :
            edge (dict) : dict specifying the new edge
                Example:{"user_id":16,
                         "parent_id":"9a1662f9-20fb-43be-a442-aca7314f2236",
                         "child_id": "1a1662f9-20fb-43be-a442-aca7314f2236",
                         "tree_id": "1a1662f9-20fb-43be-a442-aca7314f2236"}
        """
        _post_json(self.url, self._edge_endpoint, self._session, edge)

    def _post_leaf(self, leaf):
        """Add a leaf. All leaf information will be given in the new_leaf dict

        Args :
            leaf (dict) : dict specifying the leaf
                Example:{"user_id":16,
                         "parent_id":"9a1662f9-20fb-43be-a442-aca7314f2236",
                         "tree_id": "1a1662f9-20fb-43be-a442-aca7314f2236",
                         "title": "big discovery,
                         "description" : "blah"}
        """
        endpoint = self._post_leaf_endpoint
        _post_json(self.url, endpoint, self._session, leaf)

    def post_tree(self, tree):
        """Add a tree. All tree information will be given in the new_tree dict

        Args :
            tree (dict) : dict specifying the new tree
                Example:
                    {"user_id":16,
                     "color": "#E6A0C4",
                     "tree_id": "1a1662f9-20fb-43be-a442-aca7314f2236"}
        """
        _post_json(self.url, self._tree_endpoint, self._session, tree)

    def _share_tree(self, tree_id):
        foo_body = {"_": "_"}
        _post(self.url, self._tree_share_endpoint.format(tree_id), self._session, foo_body)

    def _post_team(self, teamname):
        team = {"name" : teamname}
        _post_json(self.url, self._post_team_endpoint, self._session, team)

    def _post_team_member(self, email, role):
        team_member = {"email" : email, "role" : role}
        _post_json(self.url,
                    self._post_team_member_endpoint,
                    self._session,
                    team_member)

    def upload(self, upload):
        """Upload a file.

        Args:
            upload (dict): {
              "fileaname": "asd.txt",
              "mine": "text/html",
              "lastModified": 12345678,
              "size": 10,
              "data": "xxoxoxoxXX11199900",
              “leaf_id” : “ljkdsfljksdfasdfjkl”
                            }
        """

        return _post_json(self.url, self._upload_endpoint, self._session,
                          upload)

    def new_leaf(self, leaf):
        """Add a new leaf

        You can add leaves to a specific leaf or tree or to the last used
        leaf if parent_id and tree_id are None. It will also add the edge
        connecting the new leaf to it's parent_id leaf.

        Args:
            tree_id (str)       : The id of the tree where we want to add the
            leaf.
            parent_id (str)     : The id of the leaf where we want to attach the

            leaf_id(str)        : UUID of the new leaf.
            leaf

            first_leaf(bool)    : Whether it is the first leaf in the tree. In this
                                case it won't have a parent and no edge will be added

            title (str)         : Title of the leaf. If None _leaf_msg will generate one
            description (str)   : Description text of the leaf. If None _leaf_msg will generate one
            kvs (dict)          : Key value pairs

            data [dict,...]     : List of the datafile dicts

            references [dict,..]: List of the references

        Returns:
            success (bool)      : It all went well, it will return True
        """
        # upload data-attachments to server
        if leaf.data:
            for _, data in leaf.data.items():
                self.upload(data)

        self._post_leaf(leaf)

        if leaf.references:
            for ref in leaf.ref_dict_list():
                self.post_ref(ref)

        if not leaf.first:
            # If the leaf was successfully created, add the edge connecting the
            # new leaf to its parent.
            # Generate the message for the new edge
            edge = {
                "user_id": leaf.user_id,
                "parent_id": leaf.parent_id,
                "child_id": leaf.leaf_id,
                "tree_id": leaf.tree_id
            }
            # Send the message
            self.post_edge(edge)


class Garden:
    """The garden object holding all trees a logged in user can access

    Attributes:
        trees (OrderedDict) :   The trees in the garden indexed by tree_id,
                                which is a UUID
        ct (tree)           :   The current tree


    """

    def __init__(self,
                 url: str = "https://amie.ai/api",
                 key: str = None) -> None:
        """
         Args:
            password (str)      : min 6 character password
            email (str)         : unique email of the user
            url (str)           : url to the server
            stay_logged_in      : whether or not to keep the user logged-in

        """

        self._api = API(url, key)
        self._ct = None
        self._saved = False
        self.trees = AttrOrdDict()  # type: OrderedDict[str, Tree]
        self._references_by_id = OrderedDict()  # type: OrderedDict[str, str]
        self._edges = {}

    def load(self):
        """ Fetch a garden which contains all the knowledge for a user or team
        """

        resp = self._api.get_garden()

        for tree_id, tree_dict in resp['trees'].items():
            new_tree = Tree(self._api, "")
            new_tree.load_from_dict(tree_dict)
            self.trees.update({tree_id: new_tree})
            # Set the last loaded tree as the current tree.
            self._ct = new_tree

        # Load the references
        if resp['references']:
            for ref in resp['references']:
                try:
                    self._references_by_id[ref['parent_id']].append(ref['child_id'])
                except KeyError:
                    self._references_by_id.update({
                        ref['parent_id']: [ref['child_id']]
                        })

       # # Set the refereneces in the leaves.
       #  if self._references_by_id:
       #      for parent_id, child_list in self._references_by_id.items():
       #              for child_id in child_list:
       #                  self.leaves_by_version[parent_id].references.append(self.leaves_by_version[child_id])

        #load the edges
        for tree_id, tree in resp['trees'].items():
            self._edges.update({tree_id: {}})
            if tree['edges']:
                for edge in tree['edges']:
                    try:
                        self._edges[tree_id][edge['parent_id']].append(edge['child_id'])
                    except KeyError:
                        self._edges[tree_id].update({edge['parent_id']:[edge['child_id']]})



    def discard_tree(self, tree_id: str):
        """Discard a tree by uuid of the tree.

        Args:
            tree_id (str)   : UUID of the tree you want to delete.

        """
        if not self.trees[tree_id].saved:
            del self.trees[tree_id]
            self._ct = self.latest
        else:
            raise TreeAlreadySaved

    def _share_tree(self, tree_id: str):
        self._api._share_tree(tree_id)

    def new_tree(self):
        """Initialize a new tree into the garden.

        Returns:
            nt (tree)   : A new instance of the tree object.
        """
        if self.trees:
            color = make_color(len(self.trees))
        else:
            color = random.choice(colorlist)
        new_tree = Tree(self._api, color)
        self._ct = new_tree
        self.trees.update({new_tree.tree_id: new_tree})
        return new_tree

    def set_ct(self, tree_id):
        """Set the 'current tree' which is the tree in the garden which is in
        focus and can be accessed by garden.ct.

        Args:
            tree_id (str)    : UUID of the tree to set as current tree

        """
        self._ct = self.trees[tree_id]

    def set_cl(self, leaf_id):
        """Set the current leaf in the garden which is in focus
        and can be accessed by garden.ct.cl . If the new leaf is in a differnt
        tree than current tree, the current tree will also be changed.

        Args:
            leaf_id (str)    : UUID of the leaf to set as current leaf.
        """
        leaf = self.leaves[leaf_id]
        self.set_ct(leaf.tree_id)
        self.ct.set_cl(leaf.leaf_id)

    def __repr__(self):
        out = ""
        for key, val in self._status().items():
            out += "{} : {}".format(key, val)
            out += "\n"
        return out

    def _status(self):
        status = OrderedDict()
        if self._ct:
            status.update({'Current tree': self.ct.tree_id})
            status.update({'Current tree title': self.ct.title})
            status.update({'Current tree saved': self.ct.saved})
            if self.ct.cl:
                status.update({'Current leaf': self.ct.cl.leaf_id})
                status.update({'Current leaf title': self.ct.cl.leaf_id})
                status.update({'Current leaf saved': self.ct.cl.saved})
        else:
            status.update({'Current tree': 'Not set yet'})

        return status

    def status(self, r=False):
        """Print the current status of the garden

        Args:
            r (optional) (bool)    : UUID of the tree to set as current tree

        Returns:
            status (OrderedDict) : Status of the garden containing (if set):
                'Current tree' : (str) UUID of the current tree
                'Current tree title' : (str) title of the current tree
                'Current tree saved' : (bool) whether the current tree has been
                    saved
                'Current leaf' : (str) UUID of the current leaf
                'Current leaf title' : (str) title of the current leaf
                'Current leaf saved' : (bool) whether the current leaf has been
                    saved
        """
        status = self._status().items()
        for key, val in status:
            print(str(key) + " : " + str(val))
        if r:
            return status

    def get_vals(self, key):
        """Get the values of the key value pairs in any leaf of the key.

        Args:
            key (str)    : Key of the key value pair

        Returns:
            vals ([str]) : List of the values as strings
        """

        vals = []
        for t in list(self.trees.items())[:][1]:
            for l in list(t.leaves.items())[:][1]:
                try:
                    v = getattr(l.kvs, key)
                    vals.append(v)
                except AttributeError:
                    pass
        return vals

    @property
    def latest(self):
        """Get the most recently added tree

        Returns:
            tree (tree) : The most recently added instance of the tree class
        """
        if self.trees:
            return list(self.trees.items())[-1][1]
        else:
            print("No trees yet")

    @property
    def first(self):
        """Get first tree added to the garden

        Returns:
            tree (tree) : The most recently added instance of the tree class
        """
        if self.trees:
            return list(self.trees.items())[0][1]
        else:
            print("No trees yet")

    @property
    def size(self):
        """Get the number of trees in the garden

        Returns:
            length (int) : Number of trees in the garden
        """
        return len(self.trees)

    @property
    def ct(self):
        """Return the 'current tree'.

        Returns:
            tree (tree) : the current tree.
        """
        if self._ct:
            return self._ct
        raise CurrentTreeNotSet

    @property
    def leaves(self):
        """Return all leaves in the garden as a dict

        Returns:
            leaves (dict) : A dict of all leaves in the garden indexed by UUID
                leaves{UUID (str) : leaf (leaf)}
        """
        leaves = {}
        if self.trees:
            for _, tree in self.trees.items():
                if tree.leaves:
                    for leaf_id, leaf in tree.leaves.items():
                        leaves.update({leaf_id: leaf})
        return leaves

    @property
    def leaves_by_version(self):
        """Return dict of the leafs by version

        Returns:
            leaves (dict) : A dict of all leaves in the garden indexed by UUID
                leaves{UUID (str) : leaf (leaf)}
        """
        leaves = {}
        if self.trees:
            for _, tree in self.trees.items():
                if tree.leaves:
                    for _, leaf in tree.leaves.items():
                        leaves.update({leaf.version_id: leaf})
        return leaves


    def leaves_by_title(self, r=False):
        """Return all leaves in the garden as an ordered dict. It is indexed
        by title and in inverse insertion order, so the most recently added
        one first.

        Returns:
            ll (OrderdDict) : A dict of all leaves in the garden indexed by title
                ll{title (str) : leaf (leaf)}
        """
        leaves = OrderedDict()
        for key, val in self.leaves.items():
            leaves.update({key: val.title})
            print(str(key) + " : " + str(val.title))
        if r:
            return leaves

    def leaves_by_description(self, r=False):
        """Return all leaves in the garden as an ordered dict. It is indexed
        by description and in inverse insertion order, so the most recently added
        one first.

        Returns:
            ll (OrderdDict) : A dict of all leaves in the garden indexed by title
                ll{description (str) : leaf (leaf)}
        """

        leaves = OrderedDict()
        for key, val in self.leaves.items():
            leaves.update({key: val.description})
            print(str(key) + " : " + str(val))
        if r:
            return leaves

    def trees_by_title(self):
        """Return all trees in the garden as an ordered dict. It is indexed
        by title and in inverse insertion order, so the most recently added
        one first.

        Returns:
            tt (OrderdDict) : A dict of all leaves in the garden indexed by title
                ll{description (str) : tree (tree)}
        """

        trees = OrderedDict()
        if self.trees:
            for key, val in self.trees.items():
                trees.update({key: val})
                print(str(key) + " : " + val.title)
            return trees
        print("No trees yet")

    def trees_by_description(self):
        """Return all trees in the garden as an ordered dict. It is indexed
        by description and in inverse insertion order, so the most recently
        added one first.

        Returns:
            tt (OrderdDict) : A dict of all leaves in the garden indexed by title
                ll{description (str) : tree (tree)}
        """
        trees = OrderedDict()
        if self.trees:
            for key, val in self.trees.items():
                trees.update({key: val.description})
                print(str(key) + ": " + val.description)
            return trees
        print("No trees yet")

    def tips(self):
        """
        Gather all of the last leaves in all trees. This gives you the latest state of all trees.


        Returns:
            tips (dict) : Dictionary of the ending leaves by tree_id. {str : [str, str, ...]}
                          Example:
                              {tree_id: [leaf_id1, leaf_id2, ...]}
        """
        tips = {}
        for tree_id, edges in self._edges.items():
            tips.update({tree_id: []})
            # In case there is a tree with only one leaf.
            if (not edges) and self.trees[tree_id].leaves:
                tips[tree_id].append(self.trees[tree_id].first.leaf_id)
            for parent, children in edges.items():
                for child in children:
                    try:
                        edges[child]
                    except KeyError:
                        tips[tree_id].append(child)
        return tips


class Tree:
    """The tree class which holds leaves

    Attributes:
        leaves (OrderedDict)    :   All leaves in the tree indexed by leaf_id
                                    which is a uuid string.
        cl (leaf)               :   The current leaf.
        tree_id (str)           :   The uuid string uniquely identifying the
                                    tree.
        title (str)             :   The description text of the tree
        description (str)       :   The description text of the tree

    Note:
        More public attributes are added when loading the tree from the server

    """

    def __init__(self, api: API, color: str, title=None,
                 description=None) -> None:
        """Initialize a tree, typically done from the garden object, which
        passes the user specific API() object.

        Args:
            api (amieci.api.API)            :  API object.
            title (optional) (string)       :  Title of the tree
            description (optional) (string) :  Description of the tree

        """
        self._api = api
        self._user_id = self._api._user_id
        self.leaves = AttrOrdDict()  # type: OrderedDict[str, Leaf]
        self._cl = None
        self.description = description
        self.title = title
        self.tree_id = str(uuid.uuid4())
        self.color = color
        self._saved = False

    @property
    def saved(self):
        """
        returns if the tree is saved
        """
        return self._saved

    def load_from_dict(self, tree_dict):
        """Load the tree attributes from a dictionary and load the leafs it
        contains. This is for loading a tree from the server and is called in
        garden.load().

        Args:
            tree_dict (dict) : dictionary from unmarshalling a JSON from the
            server.
            Example:
                {"user_id" : int,
                "color" : str,
                "tree_id" : str,
                "title" : str,
                "description" : str,
                "created" : int,
                "shared"  : bool,
                "leaves" : [{leaf_id: {leaf...}}]}

        """
        try:
            self.user_id = tree_dict['user_id']
            self.color = tree_dict['color']
            self.tree_id = tree_dict['tree_id']
            self.title = tree_dict['title']
            self.description = tree_dict['description']
            self.created = tree_dict['created']
            self.shared = tree_dict['shared']

            # The leaves are dicts stored in a list. Go through the list and add them to the leaves OrderedDict
            # by leaf_id
            if tree_dict['leaves']:
                for leaf_dict in tree_dict['leaves']:
                    new_leaf = Leaf(self._api, leaf_dict["tree_id"])
                    new_leaf.load_from_dict(leaf_dict)
                    self.leaves.update({new_leaf.leaf_id: new_leaf})

            # Set the current leaf to the last loaded leaf, which is most recently created one.
            if self.leaves:
                self._cl = list(self.leaves.items())[-1][1]

            # If it is loaded from the server, it has been saved already.
            self._saved = True
        except KeyError:
            LOGGER.error("The tree you're trying to download does not exist")
            raise TreeNotValid


    def discard_leaf(self, leaf_id=None):
        """Discard a leaf by uuid from the tree. By default the most recent one.

        Args:
            leaf_id (optional) (str)   : UUID of the leaf you want to delete.

        """
        if leaf_id is None:
            leaf_id = self.latest.leaf_id
        try:
            if not self.leaves[leaf_id].saved:
                del self.leaves[leaf_id]
                self._cl = list(self.leaves.items())[-1][1]
            else:
                raise LeafAlreadySaved
        except KeyError:
            # TODO this is debatable: should the exectution stop?
            # should the user just notifed ?(I(g) would take the latter)
            LOGGER.info("Leaf {:s} does not exist".format(leaf_id))

    def set_title(self, title):
        """Set the tile of the tree. This will overwrite the previous title if
        it is already set.

        Args:
            title (str)   : The title

        """
        self.title = title

    def set_description(self, description):
        """Set the description of the tree. This will overwrite the previous
        description if it is already set.

        Args:
            description (str)   : The title

        """
        self.description = description

    def save(self):
        """Save the tree to the server. This will send the tree to the server
        if it is not already saved.

        """

        requirements = [(not self._saved), self.title, self.description]
        messages = [
            "Tree is already saved", "Add a title", "Add a description"
        ]
        for idx, requirement in enumerate(requirements):
            if not requirement:
                LOGGER.error(messages[idx])
                raise TreeNotValid
        self._api.post_tree(self)
        self._saved = True

    def to_json(self):
        return {
            'user_id': self._user_id,
            'color': self.color,
            'title': self.title,
            'tree_id': self.tree_id,
            'description': self.description
        }

    def new_leaf(self, parent=None):
        """Create a new leaf. If no parent is specified, it will be a child of
        the current leaf. The parent has to be in the same tree. If there are
        no leafs in the tree, this will automatically become the first leaf
        without parents. The new leaf will also become the current leaf and is
        accessed from the garden as garden.ct.cl .

        Args:
            parent (optional) (leaf)    : The leaf where you want to attach the
            new leaf.

        Returns:
            nl (leaf)                   : The new instance of the leaf class
        """
        if not self._saved:
            LOGGER.error("Save the tree before adding leaves")
            raise CurrentTreeNotSaved
        if parent is None:
            if self.leaves:
                new_child = self._cl.new_child()
                if new_child:
                    self._cl = new_child
                    self.leaves.update({new_child.leaf_id: new_child})
            else:
                new_child = Leaf(self._api, self.tree_id, first=True)
                self._cl = new_child
                self.leaves.update({new_child.leaf_id: new_child})
        else:
            if isinstance(parent, Leaf):
                if self.tree_id == parent.tree_id:
                    new_child = parent.new_child()
                    self._cl = new_child
                    self.leaves.update({new_child.leaf_id: new_child})
                else:
                    LOGGER.error("Parent must be in the same tree!")
                    raise MismatchedParent
            else:
                LOGGER.error("Parent is not a leaf :(")
                raise TypeError
        return new_child

    def add_leaf(self, leaf):
        """Add a leaf to the garden. A leaf has to be an instance of the leaf
        class. You can only add leafes that have not been saved yet.

        Args:
            leaf (leaf)   : An instance of the leaf class which has not
                                  been saved yet.
        """
        if not self._cl.saved:
            if isinstance(leaf, leaf):
                self.leaves.update({leaf.leaf_id: leaf})
                self._cl = leaf
            else:
                print("That is not a leaf :(")
        else:
            print("Save current leaf first!")

    def leaves_by_title(self, r=False):
        """Return all leaves in the tree as an ordered dict. It is indexed
        by title and in inverse insertion order, so the most recently added
        one first.

        Returns:
            ll (OrderdDict) : A dict of all leaves in the garden indexed by title
                ll{title (str) : leaf (leaf)}
        """
        leaves = OrderedDict()
        for key, val in self.leaves.items():
            leaves.update({key: val.title})
            print(str(key) + " : " + str(val.title))
        if r:
            return leaves

    def leaves_by_description(self, r=False):
        """Return all leaves in the garden as an ordered dict. It is indexed
        by description and in inverse insertion order, so the most recently added
        one first.

        Returns:
            ll (OrderdDict) : A dict of all leaves in the garden indexed by title
                ll{description (str) : leaf (leaf)}
        """

        leaves = OrderedDict()
        for key, val in self.leaves.items():
            leaves.update({key: val.description})
            print(str(key) + " : " + str(val))
        if r:
            return leaves

    @property
    def size(self):
        """The number of leaves in the tree

        Returns:
            (int)   : Number of leaves in the tree
        """
        return len(self.leaves)

    @property
    def latest(self):
        """The most recently added leaf in the tree

        Returns:
            leaf (leaf) :   instance of the leaf class
        """
        return list(self.leaves.items())[-1][1]

    @property
    def first(self):
        """The most first leaf in the tree

        Returns:
            leaf (leaf) :   instance of the leaf class
        """
        return list(self.leaves.items())[0][1]

    @property
    def cl(self):
        """The current leaf.

        Returns:
            cl (leaf) :   instance of the leaf class
        """
        if self._cl:
            return self._cl
        else:
            print("No current leaf set yet")

    def set_cl(self, leaf_id):
        """Set the current leaf to the leaf given by the uuid. The leaf has
        to be in the tree. If you want to set a leaf from a difffernt tree
        you have to change it in garden with garden.set_cl .

        Args:
            leaf_id (str)   :   UUID string of the leaf

        """
        self._cl = self.leaves[leaf_id]

    def set_cl_latest(self):

        self._cl = self.latest

    def set_cl_first(self):

        self._cl = self.frist




class Leaf:
    """The leaf class which holds all data, metaparemters, and thoughts.

    Metaparmeters and data have their own objects which live in leaf.data and
    leaf.kvs. You can access metaparameter values by leaf.kvs.'key', and
    datafiles or liked data by leaf.kvs.data.'filename'

    Attributes:
        kvs (kvs)           :   metaparemeters as key value pairs
                                which is a uuid string.
        data (datas)        :   Data to be uploaded or linked to the leaf
        references (list)   :   List of leaves this leaf referes to
        leaf_id (str)       :   The uuid string uniquely identifying the leaf
        parent_id (str)     :   The leaf_id of the the parent. kvs are
                                inherited from the parents.
        title (str)         :   The title text of the leaf
        description (str)   :   The description text of the leaf

    Note:
        More public attributes are added when loading the leaf from the server

    """

    def __init__(self,
                 api: API,
                 tree_id,
                 title=None,
                 description=None,
                 parent_id=None,
                 first=False) -> None:
        """Initialize a leaf, typically done from the tree object with
        tree.new_leaf(), but it can also live on it's own.

        Args:
            api (amieci.api.API)            :  API object.
            title (optional) (string)       :  Title of the leaf
            description (optional) (string) :  Description of the leaf

        """
        self._api = api
        self.user_id = self._api._user_id
        self._saved = False
        self.data = OrderedDict()
        self.kvs = Kvs()
        self.leaf_id = str(uuid.uuid4())
        self.version_id = str(uuid.uuid4())
        self.parent_id = parent_id
        self.child_id = None
        self._first = first
        self.tree_id = tree_id
        self.references = []  # type: typing.List[Leaf]
        self.title = title
        self.description = description

    @property
    def saved(self):
        """
        returns if the leaf is saved
        """
        return self._saved

    @property
    def first(self):
        """
        returns if the leaf is the first of tree
        """
        return self._first



    def load_from_dict(self, leaf_dict):
        """Load the leaf attributes from a dictionary. This is for loading a tree
        from the server and is called through garden.load().

            Args:
                leaf_dict (dict) : dictionary from unmarshalling a JSON from the
                server.
                Example:
                    {'created_on': 1536084144417300992,
                    'data': [dict, dict, ...],
                    'description': str,
                    'kv_pairs': {str: str, ...}
                    'leaf_id': str,
                    'version_id': str,
                    'timestamp': int,
                    'title': str,
                    'tree_id': str,
                    'user_id': int}
        """

        try:
            self.created_on = leaf_dict['created_on']
            self.description = leaf_dict['description']
            self.title = leaf_dict['title']
            self.leaf_id = leaf_dict['leaf_id']
            self.timestamp = leaf_dict['timestamp']
            self.user_id = leaf_dict['user_id']
            self.version_id = leaf_dict['version_id']

            # Datafiles are stored in a list and get their own dictionary
            if leaf_dict['data']:
                self.load_data_from_leaf_list(leaf_dict['data'])

            # KV pairs are not normal attributes, they have their own classes.
            self.kvs.add_dict(leaf_dict['kv_pairs'])


            # Set saved to True because everything loaded from the server has already been saved.
            self._saved = True
        except KeyError:
            LOGGER.error("The leaf you're trying to download does not exist")
            raise LeafNotValid




    def set_title(self, title):
        """Set the title of the leaf. An existing title will be overwritten

        Args:
            title (str): The title as a string
        """
        if not self._saved:
            self.title = title
        else:
            raise LeafAlreadySaved


    def set_description(self, description):
        """Set the description of the leaf. An exsiting description will be
        overwritten.

        Args:
            description (str): The description of the leaf.
        """
        if not self._saved:
            self.description = description
        else:
            raise LeafAlreadySaved

    def append_description(self, description):
        """Add to the bottom of the existing leaf description

        Args:
            description (str): The description text
        """

        if not self.description:
            self.description = " "
        if not self._saved:
            self.description = self.description + '\n' + description
        else:
            raise LeafAlreadySaved

    def insert_description(self, description):
        """Add to the top of the existing leaf description

        Args:
            description (str): The description text
        """
        if not self._saved:
            self.description = description + '\n' + self.description
        else:
            raise LeafAlreadySaved

    def add_reference(self, garden: Garden, leaf_id: str):
        """Add a reference to annother leaf to the leaf. The leaf can be any
        leaf in the garden, so a leaf that is at last visible to the user.
        The reference is the full object, however when saving to the server
        it will only store the UUID and make a note in the description which
        can be used to jump to the refered leaf in the frontend.

        Args:
            garden (Garden): The garden in which the leaf is.
            leaf_id (str): uuid of the leaf you want to reference
        """
        try:
            self.references.append(garden.leaves[leaf_id])
            description = "@" + leaf_id + "@"
            self.append_description(description)
        except KeyError:
            LOGGER.error("The leaf you're trying to reference does not exist")
            raise LeafDoesNotExist

    def ref_dict_list(self):
        """Return the references as a list of of dicts.

        Returns:
            list: list of dictionaries for the referneces
        """
        ref_dict_list = []
        for reference in self.references:
            ref_dict_list.append({
                'user_id': self.user_id,
                'parent_id': reference.version_id,
                'child_id': self.version_id
            })
        return ref_dict_list

    def save(self):
        """Save the leaf to the server.

        This will cast all information contained in the leaf into JSON format
        and sent it to the amie API.


        """
        if not self._saved:
            self._api.new_leaf(self)
            self._saved = True
        else:
            raise LeafAlreadySaved

    def to_json(self):
        return {
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "data": self.data_to_upload_format(),
            "parent_id": self.parent_id,
            "first_leaf": self.first,
            "leaf_id": self.leaf_id,
            "version_id": self.version_id,
            "kv_pairs": self.kvs,
            "tree_id": self.tree_id,
            "created_on": int(time.time() * 1e3),
            "timestamp": int(time.time() * 1e3)
        }

    def new_child(self):
        """Return a new leaf as a child of this leaf. The parent_id is set to
        this leafs leaf_if and it will be in the same tree.
        Metaparameters will be inherited.

        If the leaf is not saved yet, it will complain and return None.

        Returns:
           l (leaf): A new leaf object.
        """
        if self._saved:
            child_leaf = Leaf(self._api, self.tree_id, parent_id=self.leaf_id)
            return child_leaf
        LOGGER.info("This leaf is not saved, save it before adding a child it to it")
        raise CurrentLeafNotSaved

    def data_to_upload_format(self):
        """
        converts datas to the json rapresentation the api wants, that is wihtout the acutual data
        """
        data_attachments = []
        for _, val in self.data.items():
            if isinstance(val, DataAttachment):
                data_attachments.append(val.to_dict())
        return data_attachments

    def add_data(self, filename, file, caption='', mime=None):
        """Add a datafile as an attribute to Datas by filename.

        The file is added as a bytes. If no mimetype is given, we try to guess
        it by the filename.


        Args:
            filename (str): The filename which will also be the attribute.
            file (bytes):
            caption (str, optional): Defaults to ''. caption text, displyed
                                     in the frontend under the file
            mime (str, optional): Defaults to None. Mime type of the file.
        """

        # Format data to bitstream
        data = base64.b64encode(file).decode('utf-8')

        # Guess mime if it's not given
        if not mime:
            mime = mimetypes.guess_type(filename)[0]

        attachment = DataAttachment(filename, data, caption, mime)

        self.data.update({attachment.fileID : attachment})

    def add_plot(self, filename, fig, caption=''):
        """Add a mayplotlib figure as a png datafile. It will become anl
        attribute and can be accessed by filenme. Before passing the figure,
        initalize it with fig = plt.figure(). Then after plotting the figure
        can be passed to add_plot.

        Filenames can't include spaces because attributes can't have spaces,
        so spaces will be replaced with _ after a warning.

        The file will be converted to base64 encoded bytes.

        Args:
            filename (str): The name of the file.
            fig (matplotlib.figure.Figure): the matplotlib figure
            caption (str, optional): Defaults to ''. A caption for the figure.
                                     It will be displayed in the frontend under
                                     the figure.
        """

        # Format data to bitstream
        file = io.BytesIO()
        fig.savefig(file, format='png')
        file.flush()
        data = base64.b64encode(file.getvalue()).decode('utf-8')

        attachment = DataAttachment(filename, data, caption, 'image/png')

        self.data.update({attachment.fileID:attachment})


    def load_data_from_leaf_list(self, datafilelist):
        """Add datafiles from leafs from the server. The data will not be
        immediately downloaded but added as a DataLink object.

        Args:
            datafilelist (list of dicts): List of datafile responses from the
                                          server. Each datafile has it's own
                                          dictionary.
                                Example:
                                        {'caption': 'wine',
                                        'checksum': str,
                                        'fileID': str,
                                        'filename': str,
                                        'lastModified': int,
                                        'mime': str,
                                        'rawDataURL': str,
                                        'size': 1234,
                                        'thumbnailURL': str}
        """

        for data_entry in datafilelist:
            try:
                caption = data_entry['caption']
                checksum = data_entry['checksum']
                fileID = data_entry['fileID']
                filename = data_entry['filename']
                lastModified = data_entry['lastModified']
                mime = data_entry['mime']
                size = data_entry['size']
                new_datalink = DataLink(filename,
                                        fileID,
                                        caption,
                                        size,
                                        mime,
                                        lastModified,
                                        checksum,
                                        self._api.url,
                                        self.leaf_id,
                                        self.version_id)
                self.data.update({fileID: new_datalink})
            except KeyError:
                LOGGER.error("The datafile you are trying to download is not valid")
                raise DatafileNotValid

    def download_data(self, uuid=None, filename=None):
        """

        Args:
            uuid (str): UUID of the file
            filename (string) : name or part of the name of the file

        Returns:

        """
        downloads = []
        if ((not uuid) and (not filename)):
            for _, val in self.data.items():
                downloads.append(val.download())
        elif uuid:
            return self.data[uuid]
        elif filename:
            for _, val in self.data.items():
                if filename in val.filename:
                    downloads.append(val.download())
        return downloads

    def filenames(self):
        """
        Return the names of all files in a leaf

        Returns:
            filenames [str, str...] : List of filenames

        """
        file_names = []
        for _, val in self.data.items():
            file_names.append(val.filename)
        return file_names






class DataAttachment:
    """Object to hold datafiles for upload.

    Attributes:
        data (str) : base64 encoded bitstring
        size (int) : size of the datafile in bytes
        caption (str) : caption string for the file
        fileID (str)  : uuid of the datafile
        lastModified (int) : time when the file was last modified in the object
        filename (str) : name of the file inlcuding extension
        mime (str) : mimetype of the file.
    """

    def __init__(self, filename, data, caption, mime):
        """Initialize the DataAttachment. Typicially called from Datas.add

        Args:
            data (str) : base64 encoded bitstring
            caption (str) : caption string for the file
            filename (str) : name of the file inlcuding extension
            mime (str) : mimetype of the file.
        """
        self.data = data
        self.size = len(data)
        self.caption = caption
        # NOTE: this is weirdly capitalized because we want the JSON repr
        # to have fileID field
        self.fileID = str(uuid.uuid4())
        self.last_modified = int(time.time() * 1e3)
        self.filename = filename
        self.mime = mime

    def __repr__(self):
        return str(self.filename)

    def to_json(self):
        return self.__dict__

    def to_dict(self):
        """
        converts a DataAttachment to a data less dict that can
        be used inside a leaf.
        """
        data_less_representation = {}
        for key, value in self.__dict__.items():
            if key == "data":
                pass
            else:
                data_less_representation[key] = value

        return data_less_representation


class DataLink:
    def __init__(self,
             filename,
             fileID,
             caption,
             size,
             mime,
             lastModified,
             checksum,
             api_url,
             leaf_id,
             version_id):

        self.filename = filename
        self.fileID = fileID
        self.caption = caption
        self.size = size
        self.mime = mime
        self.lastModified = lastModified
        self.checksum = checksum
        self.leaf_id = leaf_id
        self.version_id = version_id
        self.url = api_url + "/file/" + fileID

    def download_pandas(self):
        """Returns the data as a pandas dataframe if it is a CSV.
    `   """
        return pd.read_csv(self.url, sep=';', index_col=0)

    def download(self):
        """Returns the data as a file like object
        """
        resp = requests.get(self.url)
        return io.BytesIO(resp.content)


class Kvs:
    def __init__(self):
        pass

    def to_json(self):
        output = {}
        for key, val in self.__dict__.items():
            output[key] = val
        return output

    def load_from_dict(self, kv_pairs):
        for key, val in kv_pairs.items():
            self.add(key, val)

    def deep_copy(self):
        new_kvs = Kvs()
        for key, val in self.__dict__.items():
            setattr(new_kvs, key, val)
        return new_kvs

    def add(self, key, val):
        if " " in key:
            LOGGER.warning("Don't use spaces in keys. Will replace with _")
            key = key.replace(" ", "_")
        value_as_string = str(val)
        setattr(self, key, value_as_string)

    def add_dict(self, dictionary):
        for key, value in dictionary.items():
            self.add(key, value)

    def remove(self, key):
        delattr(self, key)

    def add_or_update(self, key, val):
        try:
            getattr(self, key).update(str(val))
        except AttributeError:
            self.add(key, val)

    def add_or_update_dict(self, dictionary):
        for key, value in dictionary.items():
            self.add_or_update(key, value)


colorlist = [
    "#AED6C9", "#93A2A9", "#7E98CE", "#DEADA0", "#D4D5EC", "#EAA9CB",
    "#C1E0DD", "#DE852D", "#FDF4DA", "#C82E18", "#DDE4E3", "#D4502B",
    "#C68486", "#68B1AA", "#FED55C", "#2195A3", "#65AA69", "#9B9795",
    "#EDECED", "#BF7195", "#cce5dd", "#c6ced2", "#c8d2ea", "#ebcec6",
    "#b8b9e0", "#f0c1da", "#aad4d0", "#f5d9bd", "#fae39e", "#f7c3bb",
    "#b8c6c4", "#fae39e", "#fad7d1", "#b8c6c4", "#f2cac0", "#e7cbcc",
    "#cde5e3", "#fee59a", "#c0edf2", "#bddbbf", "#e2ddd0", "#dad8d8",
    "#dfb9cb", "#99ccbc", "#aab6bb", "#a3b5dc", "#ca7d68", "#8385c9",
    "#e184b4", "#66b2ab", "#eebf91", "#f6ce55", "#ef8676", "#8ea4a1",
    "#f5c73d", "#f29a8d", "#8ea4a1", "#e1846b", "#d7a8a9", "#9acbc6",
    "#fecb34", "#80dbe5", "#8cc08e", "#c4baa1", "#c1bfbd", "#b38097",
    "#66b29a", "#71858e", "#466ab9", "#bd5d42", "#4e51b1", "#fa99cb",
    "#4d9991", "#c7731f", "#f2b90d", "#ea5e48", "#667f7c", "#daa60b",
    "#e74a32", "#667f7c", "#a94023", "#af5053", "#458780", "#e4ac01",
    "#41c9d8", "#519455", "#a79872", "#9c969c", "#b04f7c", "#448872",
    "#4f5d63", "#2a406f", "#713828", "#36397c", "#d2468f", "#336661",
    "#9a5918", "#aa8109", "#892010", "#445552", "#916f08", "#892010",
    "#445552", "#7f301a", "#8c4043", "#2b5450", "#987201", "#16616a",
    "#366339", "#6e6245", "#b39180", "#7b3757"
]


def make_color(nr):
    return colorlist[nr]


class AttrOrdDict(OrderedDict):
    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value
