if __name__ == "__main__":
    raise

from googleapiclient.discovery import build
from youtube import Search
from youtube import Playlist
from youtube import Video

__title__ = 'youtube'
__author__ = "Katistic"
__version__ = "0.0.24"

client_set = False
client = None

def setup(data):
    global client_set
    global client

    try:
        client = build(data["API_Service_Name"], data["API_Version"], developerKey = data["DevKey"])
    except:
        raise Exception("Failed to build client:", sys.exc_info[0])

    client_set = True

def ClientNotSetErr():
    raise Exception("Client has not been set.")

def SetClient(devkey):
    data = {
        "DevKey": devkey,
        "API_Service_Name": "youtube",
        "API_Version": "v3"
    }

    setup(data)

def _valid_client():
    if client != None:
        return True
    return False

def _setup():
    if client_set and _valid_client:
        return True
    return False

class search:
    def videos(**kwargs):
        if client_set:
            data = Search.Videos(client, kwargs)
            return data
        else:
            ClientNotSetErr()

    def playlists(**kwargs):
        if client_set:
            data = Search.Playlists(client, kwargs)
            return data
        else:
            ClientNotSetErr()

    def channels(**kwargs):
        if client_set:
            data = Search.Channels(client, kwargs)
            return data
        else:
            ClientNotSetErr()

class playlist:
    def getItems(playlistObj):
        if client_set:
            data = Playlist.GetPlaylistItems(client, playlistObj)
            return data
        else:
            ClientNotSetErr()

    def getItemsFromId(id):
        if client_set:
            return Playlist.GetPlaylistItemsFromId(client, id)
        else:
            ClientNotSetErr()

    def getFromId(id):
        if client_set:
            return Playlist.GetFromId(client, id)
        else:
            ClientNotSetErr()

class video:
    def getFromId(id):
        if client_set:
            return Video.GetFromId(client, id)
        else:
            ClientNotSetErr()
