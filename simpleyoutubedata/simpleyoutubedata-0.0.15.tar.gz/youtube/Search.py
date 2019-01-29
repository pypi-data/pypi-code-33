if __name__ == "__main__":
    raise

from youtube.Playlist import Playlist
from youtube.Video import Video
from youtube.Channel import Channel

def _Videos(client, ignore_private, kwargs):
    response = client.search().list(**kwargs).execute()

    items = []
    for item in response['items']:
        items.append(Video(item))

    if ignore_private:
        for item in items:
            if item.private:
                items.remove(item)

    return items

def Videos(client, kwargs):
    if "ignore_private" in kwargs and type(kwargs["ignore_private"]) == bool:
        ignore_private = kwargs.pop("ignore_private")
    else:
        ignore_private = True

    kwargs["part"] = "snippet"
    kwargs["type"] = "video"

    data = _Videos(client, ignore_private, kwargs)
    return data

def _Playlists(client, kwargs):
    response = client.search().list(**kwargs).execute()

    items = []
    for item in response['items']:
        items.append(Playlist(item))

    return items

def Playlists(client, kwargs):
    kwargs["part"] = "snippet"
    kwargs["type"] = "playlist"

    data = _Playlists(client, kwargs)
    return data

def _Channels(client, kwargs):
    response = client.search().list(**kwargs).execute()

    items = []
    for item in response["items"]:
        items.append(Channel(item))

    return items

def Channels(client, kwargs):
    kwargs["part"] = "snippet"
    kwargs["type"] = "channel"

    data = _Channels(client, kwargs)
    return data
