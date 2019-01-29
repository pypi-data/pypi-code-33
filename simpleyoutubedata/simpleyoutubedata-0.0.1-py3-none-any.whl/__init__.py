from googleapiclient.discovery import build
from youtube import Search as s

__title__ = 'youtube'
__author__ = "Katistic"
__version__ = "0.0.1"

client_set = False
client = None

def setup(data):
    global client_set
    global client

    try:
        client = build(data["API_Service_Name"], data["API_Version"], developerKey = data["DevKey"])
    except:
        print("Failed to build client:", sys.exc_info[0])
        raise

    client_set = True

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
        data = s.Videos(client, kwargs)
        return data

    def playlists(**kwargs):
        data = s.Playlists(client, kwargs)
        return data
