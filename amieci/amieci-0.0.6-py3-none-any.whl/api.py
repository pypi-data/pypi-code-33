import json
import requests
import uuid
import time


def register(url, user):
    """Registration witht the server

    Args:
        url (str) : Url to the server /api
            Example:
                url = "http://192.168.1.194:8080/api"
        user (dict): dict with the user information neceaary for login:
            Example:
                user = {"email": "huasdhuw@amie.dk",
		        "password": "dupeaaaaar",
		        "username": "johaasdasfdnasdfasfnesdfasda"}

    Retruns:
        request (dict) : the message back from the server. The only new thing
                         should be the user_id which is assigned by the server
            Example:
            {'user_id': 29,
            'username': 'johaasdasfdnasdfasfnesdfasda',
            'email': 'huasdhuw@amie.dk'}
    """

    # Find the right endpoint
    url = url + "/register"
    request = requests.post(url, json=user)
    #Check for error messages from the server
    print(request.status_code)
    if request.status_code != requests.codes.ok:
        print(request)
        sucess = False
        return request, sucess
    else :
        try:
            # Try to decode the JSON response from the server
            r = request.json()
            try:
                # If everything is good, it will return the dict with {"user":
                # {"user_id..."}
                response = r['user']
                success = True
                return response, success
            except KeyError:
                try:
                    #If it fails on the server side, for exmaple user name
                    # clashes, it will return an error dict

                    response = r['errors']
                    success = False
                    return response, success
                except KeyError:
                    response = "Unknown message from server"
                    success = False
                    return response, success
        except ValueError:
            success = False
            print("Server didn't return a JSON!")
            return request, success



def login(url, user, stayLoggedIn = True):
    """Function to login to the server with user email and password

    Args:
        url (str) : url to the server
            Example : url = "http://192.168.1.194:8080/api"
        user (dict): dict containg user informatin for login. You can resue the
        one from register(...)
            Example : user = {"email": "huasdhuw@amie.dk",
		                      "password": "dupeaaaaar",
		                      "username": "johaasdasfdnasdfasfnesdfasda"}
        stayLoggedIn (bool) : If True the server will return a cookie for
                              authentificaition

    Returns:
        response (dict) : The response from the server. Will reiterate the user
                          information but also contain a "user_id" and "cookie"
                          field.
    """

    url = url + "/login"
    user["stayLoggedIn"] = stayLoggedIn

    request = requests.post(url, json=user)

    if request.status_code != requests.codes.ok:
        print(request.text)
        success = False
        return request, success
    else:
        try:
            r = request.json()
            try:
                response = r["user"]
                success = True
                user_id = response["user_id"]
                cookies = request.cookies
                response["cookie"] = cookies
                return response, success
            except KeyError:
                try:
                    response = r["errors"]
                    success = False
                    return response, success
                except KeyError:
                    response = "Unknown message from server"
                    success = False
                    return response, success
        except ValueError:
            success = False
            print("Server didn't return a JSON")
            return request, False

def get_title_suggestion(query, url, user_id, cookies, leaf_id):
    url += "/title/{}/{}?rqstr={}".format(int(user_id), leaf_id, query)
    print(url)
    request = requests.get(url, cookies=cookies)

    return get_error_handler(request)

def get_search(query, url, user_id, cookies):
    url += "/search/{}?search={}".format(int(user_id), query)
    print(url)
    request = requests.get(url, cookies=cookies)

    return get_error_handler(request)


def post_error_handler(request):
    """Handle errors from POST requests

    Args:
        request (Request()) : response from the server

    Returns:
        sucess (bool) : True if successful, False if there was an error
    """
    if request.status_code != requests.codes.ok:
        print(request.text)
        return False
    else:
        return True

def get_error_handler(request):
    """Handle errors from GET requests

    Args:
        request (Request()) : response from the server
    Retruns:
        request (dict) : The decoded JSON request from the server
        success (bool) : True if there were no errors, False otherwise

    """

    if request.status_code != requests.codes.ok:
        print(request.text, request.status_code)
        return request, False
    else:
        return request.json(), True


def get_garden(url, user_id, cookies, tree_id=None):
    """Get all trees for the user of user_id or a specific tree if tree_id is
    not None

    Args:
        url (str) : the url to the server
        user_id (int) : user id
        cookies (cookiejar) : the cookie for the user user_id
        tree_id (str) : uuid of a specific tree

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
        sucess (bool) : True if success, False if there was an error
    """

    url += "/garden/%i" % user_id

    if tree_id is not None:
        url += "/%s" % tree_id

    request = requests.get(url, cookies=cookies)

    return get_error_handler(request)


def get_leaf(url, user_id, cookies, leaf_id=None):
    """Get all leaves for the user of user_id or a specific leaf if
    leaf_id is not None

    Args :
        url (str) : Url to the server
        user_id (int) : user id
        cookies (cookiejar) : Cookies matching user_id
        leaf_id (str) : Id of the specific leaf one wants to get

    Returns
        leaf ([dict, ...]) : list of all the leaf dicts
        success (bool) : True if everythin worked. If it's false, there will be
        an error message instead of leaf


    """
    url += "/leaf/%i" % user_id

    if leaf_id is not None:
        url += "/%s" % leaf_id

    request = requests.get(url, cookies=cookies)

    return get_error_handler(request)

def get_edge(url, user_id, cookies, edge_id=None):
    """Get all edges for the user of user_id or a specific edge if
    edge_id is not None

    Args :
        url (str) : Url to the server
        user_id (int) : user id
        cookies (cookiejar) : Cookies matching user_id
        edge_id (int) : Id of the specific edge one wants to get

    Returns
        edge ([dict, ...]) : list of all the edges
        success (bool) : True if everythin worked. If it's false, there will be
        an error message instead of edge
    """
    url += "/edge/%i" % user_id

    if edge_id is not None:
        url += "/%s" % edge_id

    request = requests.get(url, cookies=cookies)

    return get_error_handler(request)


def get_merge(url, user_id, cookies, merge_id = None):
    """Get all merges for the user of user_id or a specific merge if
    merge_id is not None

    Args :
        url (str) : Url to the server
        user_id (int) : user id
        cookies (cookiejar) : Cookies matching user_id
        merge_id (int) : Id of the specific merge one wants to get

    Returns
        merge ([dict, ...]) : list of all the merge dicts
        success (bool) : True if everythin worked. If it's false, there will be
        an error message instead of edge
    """

    url += "/merge/%i" % user_id

    if merge_id is not None:
        url += "/%s" % merge_id

    request = requests.get(url, cookies=cookies)

    return get_error_handler(request)





def post_tree(url, cookies, new_tree):
    """Add a tree. All tree information will be given in the new_tree dict

    Args :
        url (str) : Url to the server
        cookies (cookiejar) : Cookies matching user_id in new_tree
        new_tree (dict) : dict specifying the new tree
            Example:
                {"user_id":16,
                 "color": "#E6A0C4",
                 "tree_id": "1a1662f9-20fb-43be-a442-aca7314f2236"}

    Returns
       sucess (bool) : True is everything worked
    """

    url += "/tree"

    request = requests.post(url, json=new_tree, cookies=cookies)

    return post_error_handler(request)

def post_edge(url, cookies, new_edge):
    """Add an edge. All edge information will be given in the new_edge dict

    Args :
        url (str) : Url to the server
        cookies (cookiejar) : Cookies matching user_id in new_edge
        new_edge (dict) : dict specifying the new tree
            Example:{"user_id":16,
                     "parent_id":"9a1662f9-20fb-43be-a442-aca7314f2236",
                     "child_id": "1a1662f9-20fb-43be-a442-aca7314f2236",
                     "tree_id": "1a1662f9-20fb-43be-a442-aca7314f2236"}

    Returns:
       sucess (bool) : True is everything worked
    """
    url += "/edge"

    request = requests.post(url, json=new_edge, cookies=cookies)

    return post_error_handler(request)

def post_ref(url, cookies, new_ref):
    """Add a reference. All reference information will be given in the new_ref dict

    Args :
        url (str) : Url to the server
        cookies (cookiejar) : Cookies matching user_id in new_edge
        new_ref (dict) : dict specifying the new tree
            Example:{"user_id":16,
                     "parent_id":"9a1662f9-20fb-43be-a442-aca7314f2236",
                     "child_id": "1a1662f9-20fb-43be-a442-aca7314f2236",
                     "tree_id": "1a1662f9-20fb-43be-a442-aca7314f2236"}

    Returns:
       sucess (bool) : True is everything worked
    """
    url += "/reference"

    request = requests.post(url, json=new_ref, cookies=cookies)

    return post_error_handler(request)

def post_leaf(url, cookies, new_leaf):
    """Add a leaf. All leaf information will be given in the new_leaf dict

    Args :
        url (str) : Url to the server
        cookies (cookiejar) : Cookies matching user_id in new_edge
        new_leaf (dict) : dict specifying the new tree
            Example:{"user_id":16,
                     "parent_id":"9a1662f9-20fb-43be-a442-aca7314f2236",
                     "tree_id": "1a1662f9-20fb-43be-a442-aca7314f2236",
                     "title": "big discovery,
                     "description" : "blah"}

    Returns:
       sucess (bool) : True is everything worked
    """
    url += "/leaf"

    request = requests.post(url, json=new_leaf, cookies=cookies)

    return post_error_handler(request)

def post_merge(url, cookies, new_merge):
    """Add a merge. All merge information will be given in the new_merge dict

    Args :
        url (str) : Url to the server
        cookies (cookiejar) : Cookies matching user_id in new_merge
        new_merge (dict) : dict specifying the new tree
            Example:{ Not implemented yet.... }

    Returns:
       sucess (bool) : True is everything worked
    """
    url += "/merge"

    request = requests.post(url, json=new_merge, cookies=cookies)

    return post_error_handler(request)


def post_upload(url, cookies, upload):
    """Upload a file.

    Args:
        url (str) : Url to the server
        cookies (cookiejar) : Cookies machting user_id
        upload (dict): {
	                    "fileaname": "asd.txt",
	                    "mine": "text/html",
	                    "lastModified": 12345678,
	                    "size": 10,
	                    "data": "xxoxoxoxXX11199900",
	                    “leaf_id” : “ljkdsfljksdfasdfjkl”
                        }
    Returns:
        sucess (bool) : True if everything worked
        response (dict) :{
                        “uuid”: “8483io-xjxjx”,
                        “thumbnail-url”: “/url/to/thumbnail”,
                        “raw-data-url: ““/url/to/data”
                        }
    """


    url += "/upload"
    request = requests.post(url, json=upload, cookies=cookies)
    return request.json()

class API(object):
    """A api object holding the login and data information for a single user"""

    def __init__(self, url, username, password, email, user_id=None):
        """Initialize with login or registration information

        Args:
            url (str) : url to the server
            username (str)      : The (unique) username of the user starting the session
            password (str)      : min 6 character password
            email (str)         : unique email of the user
            user_id (int)       : unique user id for the user, will be assigned during
                                  registration
            cookie (cookiejar)  : cookie used for authentification. Will be assigned
                                  during login
            treelist ([str,..]) : list of all of the tree_ids ( uuid ) for the
                                  trees of that user
            leaves (tree_id : [leaf_id, ... ])
                                : dict of leaf lists belonging
                                to every tree of the user indexed by tree_id
            edges ({tree_id : [(parent, child), ...]})
                                : dict of edge lists belonging to every tree of the
                                  user indexed by tree_id. The edges only consist
                                  of the (parent, child) leaf_ids.
            graphs ({tree_id : nx.Graph()})
                                : dict of the netwrokxx graphs belinging to every
                                  tree of the user indexed by tree id
            current_tree        : The tree_id of the last added tree
            current_leaf      : The leaf_id of the lest added leaf

    """

        #Login information
        self._url = url
        self._username = username
        self._password = password
        self._email = email
        self._user_id = user_id
        self._cookie = None
        self._treelist = []
        self._leaves = {}
        self._edges = {}
        self._graphs = {}
        self._trees = {}
        self._current_tree = None
        self._current_leaf = None

    def _asdict(self):
        """Return login informaiton as a dictionary"""
        return {'user_id'  : self._user_id,
                'username'  : self._username,
                'password'  : self._password,
                'email'     : self._email}

    def register(self):
        """Regiser the a new user

        Args:
            see register(url, user)
        """
        response, scs = register(self._url, {"user": self._asdict()})
        if scs:
            self._user_id = response["user_id"]
        else:
            print("Could not register !")
            print(response)

    """
    def reload_tree(self):
        Reload all the trees of the user

        resp, scs = get_garden(self._url, self._user_id, self._cookie)

        if scs :
            response = res
        else:
            print('Could not reload the tree')

        response, scs = get_garden*
    """

    def login(self):
        """Login at the server, fetch the trees

        After registration login in to the server, get the cookie, and
        populate the leaf and edge lists with the stored (if any) trees.

        Args:
            see login(url, user)
        """
        response, scs = login(self._url, self._asdict())
        if scs:
            self._cookie = response['cookie']
            self._user_id = response['user_id']
            print("Logged in with user number %i" % self._user_id)
            print("email : %s" %self._email )
            print("username : %s" %self._username)
            print("password:  %s" %self._password)
            resp, scs = get_garden(self._url, self._user_id, self._cookie)

            if scs:
                try:
                    for tree in resp["trees"]:
                        #Check wheter there are any trees. Otherweise the list
                        #will be empty.
                        if tree:
                            self._treelist.append(tree)

                            newtree = {}
                            for key,val in resp["trees"][tree].items():
                                if key not in ["leaves", "edges"]:
                                    newtree[key] = val
                            newtree["leaf_list"] = []
                            for l in resp["trees"][tree]["leaves"]:
                                newtree["leaf_list"].append(l["leaf_id"])
                            self._trees[tree] = newtree

                            self._leaves[tree] = resp["trees"][tree]["leaves"]

                            self._edges[tree] = []
                            edges = resp["trees"][tree]["edges"]
                            if edges:
                                for edge in edges:
                                    self._edges[tree].append((edge["parent_id"],
                                                              edge["child_id"]))
                except TypeError:
                    print("No trees yet")
            else:
                print("Could not load tree!")
        else:
            print("Could not log on!")
            print(response)
            return False

        if self._treelist:
            number_of_trees = len(self._treelist)
            tree_index = -1
            while True:
                self._current_tree = self._treelist[tree_index]
                maybe_current_leaf = self._leaves[self._current_tree][-1]
                if maybe_current_leaf:
                    self._current_leaf = maybe_current_leaf
                    print("Current tree: %s" % self._current_tree)
                    print("Current leaf : %s" % maybe_current_leaf)
                    break
                else:
                    tree_index -= 1
                if tree_index == -number_of_trees:
                    print("No trees with leaves found")
                    break



    def _leaf_msg(self, tree_id, title=None, description=None, kvs=None, data = None, created_on = None):
        """Generate the message for the server for adding a leaf to the db

        The leaf_id will be generated as a uuid.uuid4().
        If no title and description are given, it will automaticially put the
        date and time as title and a uuid as description

        Args:
            tree_id (str)       : Which tree the leaf should belong to
            title (str)         : Optional. Title of the leaf.
            description (str)   : Optional. Description text
            kvs (dict)          : Optional. Key value pairs as a dict
            data [dict,..]      : Optional. List of data file UUIDs
            created_on (float)  : Optional. Seconds since epoch at creation

        Returns :
            new_leaf (dict)   : Dict containing the message to the server
            leaf_id (str)     : The leaf id
        """
        if not title:
            title = time.ctime()

        if not description:
            description = str(uuid.uuid4())

        if not kvs:
            kvs = None

        leaf_id = str(uuid.uuid4())

        new_leaf = { "user_id" : self._user_id,
                    "leaf_id" : leaf_id,
                    "tree_id" : tree_id,
                    "title" : title,
                    "description" : description,
                    "kv_pairs" : kvs,
                    "data" : data,
                    "created_on" : created_on}
        return new_leaf, leaf_id


    def _tree_msg(self, title, description, created_on, color="#E6A0C4"):
        """Generate the message for the server for adding a tree
        see _leaf_msg for details
        """

        tree_id = str(uuid.uuid4())
        new_tree = {"user_id" : self._user_id,
                    "color" : color,
                    "tree_id" : tree_id,
                    "title" : title,
                    "description" : description,
                    "created" : created_on}
        return new_tree, tree_id


    def _edge_msg(self, tree_id, parent_id, child_id):
        """Generate the message for the server for adding an edge
        see _leaf_msg for details
        """
        new_edge = {"user_id" : self._user_id,
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "tree_id": tree_id}
        return new_edge

    def _ref_msg(self, tree_id, parent_id, child_id):
        """Generate the message for the server for adding an edge
        see _leaf_msg for details
        """
        new_ref = {"user_id" : self._user_id,
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "tree_id": tree_id}
        return new_ref

    def _first_leaf(self, tree_id, title=None, description=None, kvs=None, created_on = None):
        """Adding an initial leaf when building a tree.

        This function is a helper function for new_tree. Don't add leaves with
        out trees !

        Args:
            tree_id (str) : Id of the tree where to add the leaf
            title, description : see leaf_msg for details

        Returns:
            leaf_id (str): Id of the newly created leaf, if everything
            worked
        """
        #Generate the message to create the leaf
        leaf_msg, leaf_id = self._leaf_msg(tree_id,
                                                 title=title,
                                                 description=description,
                                                 kvs=kvs,
                                                 created_on=created_on)

        #Send the message
        scs = post_leaf(self._url, self._cookie, leaf_msg)

        #Analyse output, handle errors
        if not scs:
            print("creating leaf failed !")
        else:
            #Make the tree the current tree
            self._current_tree = tree_id

            #Make the leaf the current leaf
            self._current_leaf = leaf_id

            #Add the leaf to the leaf list
            self._leaves[tree_id] = []
            self._leaves[tree_id].append(leaf_id)

#            #Add the leaf as a node to the new nx.Graph() object. This is ini
#            #tilaized here because it is only used for making the first leaf
#            #in a tree
#            self._graphs[tree_id] = nx.Graph()
#            self._graphs[tree_id].add_node(leaf_id)

        return leaf_id


    def new_leaf(self, tree_id=None, parent_id=None,
                   title=None, description=None, kvs=None, data=None, created_on = '1521109443083000000'):
        """Add a new leaf

        You can add leaves to a specific leaf or tree or to the last used
        leaf if parent_id and tree_id are None. It will also add the edge
        connecting the new leaf to it's parent_id leaf.

        Args:
            tree_id (str)       : The id of the tree where we want to add the
                                  leaf.
            parent_id (str)     : The id of the leaf where we want to attach the
                                  leaf
            title (str)         : Title of the leaf. If None _leaf_msg will
                                  generate one
            description (str)   : Description text of the leaf. If None
                                  _leaf_msg will generate one
            kvs (dict)          : Key value pairs
            data [dict,...]     : List of the datafile dicts

        Returns:
            success (bool)      : It all went well, it will return True
        """

        # If no tree is specified, use the last used tree
        if not tree_id:
            tree_id = self._current_tree

        # If no parent leaf is specified, use the last used leaf
        if not parent_id:
            parent_id = self._current_leaf

        #TODO Check that the parent leaf is in the right tree

        #Upload files

        upload_leaf = []
        index = 0
        if data:
            for d in data:
                index += 1
                upload_response = self.upload(d)
                upload_dict = {"filename" : d["filename"],
                                "mime" : d["mime"],
                                "size" : d["size"],
                                "lastModified": d["lastModified"],
                                "fileID": upload_response["fileID"],
                                "caption": d["caption"],
                                "index": index}
                upload_leaf.append(upload_dict)


        #Generate the messag to the server
        leaf_msg, leaf_id = self._leaf_msg(tree_id, title=title,
                                                 description=description,
                                                 kvs=kvs, data=upload_leaf,
                                                 created_on = created_on)


        scs = post_leaf(self._url, self._cookie, leaf_msg)

        #Handle errors
        if not scs:
            print("creating leaf failed !")
            return False

        else:
            #If the leaf was sucessfully created, add the edge connecting the
            #new leaf to its parent.

            #Generate the message for the new edge
            edge_msg = self._edge_msg(tree_id, parent_id, leaf_id)

            #Send the message
            scs = post_edge(self._url, self._cookie, edge_msg)

            #Handle errors
            if not scs:
                print("creating edge failed!")
                return False

            else:
                #Make this tree the new current tree
                self._current_tree = tree_id

                #Make this leaf the new current leaf
                self._current_leaf = leaf_id

                #Add the leaf to the leaf dict
                self._leaves[tree_id].append(leaf_id)

                #Add the edge to the edges dict
                try:
                    self._edges[tree_id].append((parent_id, leaf_id))
                except KeyError:
                    self._edges[tree_id] = []
                    self._edges[tree_id].append((parent_id, leaf_id))

 #               #Add leaf and edge as node and edge to the nx.Graph() tree
 #               self._graphs[tree_id].add_node(leaf_id)
 #               self._graphs[tree_id].add_edge(parent_id, leaf_id)
                return True

    def new_tree(self, color="#E6A0C4", title=None, description=None,
                 leaf_title=None, leaf_description=None,
                 kvs=None, created_on = None):
        """Create a new tree

        Args:
            color (str)       : The color of the tree, a frontend leftover
            title (str)       : The title for the first leaf in the tree
            description (str) : The description of the first leaf in the tree

        Returns:
            success (bool)    : True if everything worked

        """

        #Generate the message
        tree_msg, tree_id = self._tree_msg(title, description, created_on, color=color)

        #Send the message
        scs = post_tree(self._url, self._cookie, tree_msg)

        #Handle errors
        if scs:

            #If the new tree has been added successfully, add the new first
            #leaf to the tree. We use the self._first_leaf(...) function
            #here because new_leaf needs a parent_id and this leaf does
            #not have a parent.
            leaf_id = self._first_leaf(tree_id, title=leaf_title,
                                           description=leaf_description, kvs=kvs,
                                           created_on = created_on)
            print("New tree added !")

        if not scs:
            print("Adding new tree failed!")

        #Make this leaf the new current leaf
        self._current_leaf = leaf_id

        #Make this tree the new current tree
        self._current_tree = tree_id

        #Add tree to treelist
        self._treelist.append(tree_id)

    def new_ref(self, tree_id, parent_id, leaf_id):
        msg = self._ref_msg(tree_id, parent_id, leaf_id)
        scs = post_ref(self._url, self._cookie, msg)
        return scs

    def suggest_title(self, query):
        title, scs = get_title_suggestion(query, self._url, self._user_id,
                        self._cookie, self._current_leaf)
        if scs:
            return title

    def search(self, query):
        search, scs = get_search(query, self._url, self._user_id,
                        self._cookie)
        if scs:
            return search

    def upload(self, upload):
        upload_response = post_upload(self._url, self._cookie, upload)
        return upload_response



    def get_leaf(self, tree_id=None, leaf_id=None, field=None, print=False):
        """Load the full leaves or only certain fields.

        If nothing is specified only the current_leaf is loaded. If the tree is
        specified but not the leaf, all leaves from thet tree area loaded. If
        the leaf_id is set to "all" all leaves from all trees of the user will
        be loaded.

        Args:
            tree_id (str)       :Either uuid() of the tree or none. If none it is
                                    assumed to be the current tree. If "all" all trees
            leaf_id (str)     :Either uudi(), None or "all". If uuid only this
                                    leaf will be loaded, regardless of the tree.
                                    If "all", all leaves will be loaded.
            field (str)         :Which field to load from the leaves. If None
                                    all fields will be loaded.
            print (bool)        :If 'True' print the result to the commandline

        Returns:
            leaves ([dict,..]) :Single leaf as a dict or a list of dicts of all
                                    the trees which were loaded
        """

        if not tree_id:
            tree_id = self._current_tree

        if not leaf_id:
            leaf_id = self._current_leaf

        leaf, scs = get_leaf(self._url, self._user_id,
                        self._cookie, leaf_id)

        if scs:
            if not field:
                return leaf
            else:
                return leaf[field]








