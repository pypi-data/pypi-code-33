import requests
from hashlib import md5
from datetime import datetime
from os.path import expanduser

from future.standard_library import install_aliases
install_aliases()
from urllib.parse import quote_plus
try:
    import json
    from json.decoder import JSONDecodeError
except ImportError:
    import simplejson as json
    from simplejson import JSONDecodeError

from swdl.matches import Match
import numpy as np
from getpass import getpass
import os
from builtins import input
from subprocess import call
from time import sleep
from base64 import b64encode


def to_md5(password):
    """
    Hashes a password to md5

    # Arguments
    password(str): The password to be hashed

    # Returns
    str: Password MD5-hash
    """
    return md5(password.encode()).hexdigest()


def save_password():
    """
    Asks for username and password and stores the credentials in ~/.swdlrc
    """
    username = input("Username: ")
    password = to_md5(getpass("Password: "))
    user_file = expanduser("~/.swdlrc")
    user_config = {}
    if os.path.exists(user_file):
        user_config = json.loads(open(user_file).read())
    user_config.update({"username": username, "password": password})
    open(user_file, "w").write(json.dumps(user_config))
    call("chmod 600 {}".format(user_file).split())


class DataService:
    """
    Helper service to download soccerwatch data

    # Attributes
    username (str): Name of the user to connect to the service
    password_hashed (str): MD5 hashed password required to login. Use #to_md5()
    """
    def __init__(self, username=None, password_hashed=None, api="prod"):
        if not username:
            user_file = expanduser("~/.swdlrc")
            if os.path.exists(user_file):
                user_config = json.loads(open(user_file).read())
                username = user_config["username"]
                password_hashed = user_config["password"]
        self.username = username
        self.password = password_hashed
        self.auth = (username, password_hashed)
        self.url_extension = "/intern/rest/v1/streamInterface"
        self.api_stream_url = "https://api-stream-interface-soccerwatch.azurewebsites.net"+self.url_extension
        self.api = api
        self.apis = requests.get("https://api-discovery-dot-sw-sc-de-prod.appspot.com/service/"+api).json()
        self.user_escaped = None
        if username:
            self.user_escaped = username

        #Test Auth
        response = requests.get(self.apis["API_USER"]+"/login", auth = self.auth)
        if response.status_code != 200:
            print("Login failed")

    def fetch(self, url, method = "GET", body = None, retries = 4):
        """
        Performs a get request on the given URL. See alse #DataService.post()

        # Arguments
        url (str): URL to perform get request

        # Retrurns
        str: Dictionary created from JSON dump of the response

        # Example
        ```python
        ds = DataService()
        ds.get("www.google.de")
        ```
        """
        next_token = ""
        while True:
            try:
                ret = ""
                for i in range(retries):
                    if method == "GET":
                        ret = requests.get(url+"/"+next_token, auth = self.auth)
                    else:
                        ret = requests.post(url+"/"+next_token, json=body, auth = self.auth)
                    if (ret.status_code != 200):
                        print(ret.status_code, ret.text)
                        sleep(i**2)
                        continue
                    else:
                        break
                if not ret or not ret.text:
                    return
                response = ret.json()
                yield response
                if "nextToken" in response:
                    next_token = quote_plus(response["nextToken"])
                else:
                    return
            except JSONDecodeError:
                print("could not parse result")
                return
            except requests.HTTPError:
                print("Failed to connect to {}".format(url))
                return

    def get_matches(self):
        """
        Lists all matches

        # Returns
        list: All matches in type #Match`
        """
        url = "{}/metas".format(self.apis["API_VIDEO"])
        for matches in self.fetch(url):
            if not "data" in matches or not matches["data"]:
                return
            else:
                for match in matches["data"]:
                    yield Match.from_json(**match).set_data_service(self)

    def get_match(self, match_id):
        """
        Returns a single #Match for a given match id

        # Arguments
        match_id (int,str): Match id

        #Returns
        Match: The requested match
        """
        url = "{}/meta/{}".format(self.apis["API_VIDEO"],
                                                match_id)
        response = list(self.fetch(url))
        if not response:
            return Match(match_id)
        ret = response[0]

        return Match.from_json(**ret).set_data_service(self)

    def get_events(self, match_id):
        """
        Returns all Events from azure

        # Arguments
        match_id (str,int): Matchid

        # Returns
        list: Events as got as dictionaries
        """
        url = "{}/Tag/{}".format(self.apis["API_TAG"], match_id)
        result = list(self.fetch(url))
        if not result:
            return []
        return result[0]["data"]

    def add_event(self, match_id, event_id, timestamp):
        """
        Add a new event zo azure

        # Arguments
        match_id (str,int): Matchid
        event_id (int): Type of the event
        timestamp (int): Time in secends when the event occurs
        """
        url = "{}/AiTag".format(self.apis["API_TAG"])
        body = {"matchId":str(match_id), "eventType":event_id, "timestamp":timestamp}
        call = self.fetch(url, "POST", body)
        list(call)

    def upload_player_positions(self, timestamp, match):
        try:
            match_id = match.match_id
            players = match.labels.player_positions[timestamp]
            data = {}
            data["playerPositions"] = []
            for i in range(players.shape[0]):
                if players[i][0] == -1:
                    continue
                data["playerPositions"].append({})
                data["playerPositions"][i]["playerId"] = int(players[i][0])
                data["playerPositions"][i]["teamId"] = int(players[i][1])
                data["playerPositions"][i]["positionX"] = float(players[i][2] /
                                                                1000.0)
                data["playerPositions"][i]["positionY"] = float(players[i][3] /
                                                                1000.0)
                data["playerPositions"][i]["certainty"] = float(players[i][4] /
                                                                1000.0)

            url = "{}/playerPositions/{}/".format(self.apis["API_ANALYTICS"],
                                                          match_id,
                                                          timestamp)
            call = self.fetch(url, "POST", data)
            list(call)

        except KeyError:
            # ToDo do something
            pass

    def get_positions(self,
                      match_id,
                      time=None,
                      virtual_camera_id="-1"):
        """
        Get the camera positions of a match

        # Arguments
        match_id (str,int): Match id
        time (datetime): Datetime to limit the data given back. Will only
        return data later than time
        virtual_camera_id (str): The camera id of the positions
        source (str): Should be human or machine

        # Returns
        list: Dictionaries of the positions

        # Example
        """
        if not time:
            last_modified = 0
        elif type(time) == int:
            last_modified = time
        elif type(time) == datetime:
            last_modified = int(time.strftime("%s")) * 1000
        else:
            raise TypeError

        virtual_camera_id = str(virtual_camera_id)

        url = "{}/CameraPosition/{}".format(self.apis["API_ANALYTIC"],
                                                     match_id)
        body = {"virtualCameraId":virtual_camera_id,
                "lastModified":last_modified}
        call = self.fetch(url, "POST", body=body)
        for bulk in call:
            if "data" in bulk:
                for pos in bulk["data"]:
                    yield pos

    def pull_info(self, match):
        """
        Updates the information about a match

        # Arguments
        match (Match): A match

        # Returns
        Match: Updated match

        # Raises
        ValueError: If input is not a match
        """
        if not isinstance(match, Match):
            raise ValueError("Argument must be a valid match")
        return self.get_match(match.match_id)


    def push_labels(self,
                    match,
                    start_index=0,
                    virtual_camera_id="-1",
                    source="human"):
        """
        Uploads the positions greater than the given #start_index to the cloud
        service

        # Arguments
        match (str): The match
        start_index (int): only positions greater than start index will be
        pushed
        virtual_camera_id (str): Camera id the positions belongs to
        source (str): Should be "human" or "machine"
        """

        message_body = self._create_label_body(match.match_id,
                                               match.labels.positions,
                                               start_index,
                                               virtual_camera_id,
                                               source)
        url = "{}/addCameraPositionBulk".format(self.apis["API_ANALYTIC"])
        call = self.fetch(url, "POST", message_body)
        next(call)

    @staticmethod
    def _create_label_body(match_id,
                           position_list,
                           start_index=0,
                           virtual_camera_id="-1",
                           source="human"):

        # ToDo push events and status
        message_body = dict()
        message_body["virtualCameraId"] = str(virtual_camera_id)
        message_body["matchId"] = str(match_id)
        message_body["source"] = str(source)
        message_body["positions"] = list()
        for i in range(start_index, len(position_list)):
            timestamp = int(position_list[i, 0])
            if timestamp == 0:
                continue
            message_body["positions"].append(dict())
            message_body["positions"][-1]["timestamp"] = timestamp
            message_body["positions"][-1]["x"] = str(position_list[i, 1])
            message_body["positions"][-1]["y"] = str(position_list[i, 2])
            message_body["positions"][-1]["zoom"] = str(position_list[i, 3])
        return message_body

    def pull_labels(self, match,
                    time_from=None,
                    virtual_camera_id="-1"):
        """
        Updates the labels of a match. May clear all locally created labels.

        # Arguments
        match (Match): A match
        time_from (datetime,int): Will only get labels later than this time,
        Must be msecs after 1970 or datetime
        virtual_camera_id (str): Camera Id
        source (str): "human" or "machine"

        #Returns
        Match: Updated match

        # Raises
        ValueError: If input is not a match
        """
        if not isinstance(match, Match):
            raise ValueError("Argument must be a valid match")

        if time_from is None:
            time_from = match.last_label_update

        match_id = match.match_id

        label = match.labels
        # Get events
        label.events = np.zeros((0, 3), dtype=np.float32)
        label.status = np.zeros((11,), dtype=np.uint32)
        events = self.get_events(match_id)
        for i, e in enumerate(events):
            e_mapped = self.map_events_from_azure(e)
            if len(e_mapped) == 2:
                label.status[e_mapped[1]] = e_mapped[0]
            else:
                label.events = np.append(label.events,
                                         [e_mapped], axis=0).astype(np.uint32)
        # Get positions
        pos_unsorted = list(self.get_positions(match_id,
                                          time_from,
                                          virtual_camera_id))
        label_resolution = 250
        if pos_unsorted is not None and len(pos_unsorted) > 0:
            positions = sorted(pos_unsorted, key=lambda k: k['timestamp'])
            highest_timestamp = int(positions[-1]["timestamp"])
            label_rows = int(highest_timestamp/label_resolution) + 1
            if label_rows > label.positions.shape[0]:
                label.positions.resize((label_rows, 7), refcheck=False)
            latest_date = datetime.fromtimestamp(0)
            for p in positions:
                timestamp = (p["timestamp"])
                x = float(p["x"])
                y = float(p["y"])
                zoom = float(p["zoom"])
                temp = [timestamp, x, y, zoom, x, y, zoom]
                label.positions[int(timestamp/label_resolution)] = temp
                date = datetime.fromtimestamp(float(p["lastModified"])/1000)
                if (date > latest_date):
                    latest_date = date
            match.last_label_update = latest_date
        match.labels = label
        return match

    @staticmethod
    def map_events_from_azure(event):
        """
        Maps a event dictionary to a list

        # Arguments
        event (dict): Event dictionary

        # Returns
        list: With either 2 or 3 entries
        """
        e = int(event["eventType"])
        timestamp = int(event["timestamp"])
        if e == 0:
            return [timestamp, 0, 0]
        if e == 1:
            return [timestamp, 0, 1]
        if e == 2:
            return [timestamp, 6, 0]
        if e == 3:
            return [timestamp, 6, 1]
        if e == 4:
            return [timestamp, 5, 0]
        if e == 5:
            return [timestamp, 5, 1]
        if e == 6:
            return [timestamp, 4, 0]
        if e == 7:
            return [timestamp, 4, 1]
        if e == 35:
            return [timestamp, 2, 0]
        if e == 36:
            return [timestamp, 2, 1]
        if e == 47:
            return [timestamp, 1, 0]
        if e == 48:
            return [timestamp, 8, 0]
        # For status
        if e == 12:
            return [timestamp * 1000, 1]
        if e == 13:
            return [timestamp * 1000, 2]
        if e == 14:
            return [timestamp * 1000, 3]
        if e == 15:
            return [timestamp * 1000, 4]
        return [timestamp, 7, 0]
