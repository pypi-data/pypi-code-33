if __name__ == "__main__":
    raise

from youtube.Video import Video

class Playlist:
    OtherProps = {}

    def __init__(self, data):
        for x in data:
            if x == "nextPageToken":
                continue

            if type(data[x]) != dict:
                self.OtherProps[x] = data[x]
                continue

            for y in data[x]:
                setattr(self, y, data[x][y])

        self.OriginalData = data

def _GetPlaylistItems(client, kwargs):
    response = client.playlistItems().list(**kwargs).execute()

    items = []
    for item in response["items"]:
        items.append(Video(item))

    try:
        nextPageToken = response["nextPageToken"]
    except:
        nextPageToken = None

    #items.append(Video({'stuff': {"title": "break", "description": ""}}))

    while nextPageToken != None:
        response = client.playlistItems().list(**kwargs, pageToken=nextPageToken).execute()

        for item in response["items"]:
            items.append(Video(item))

        try:
            nextPageToken = response["nextPageToken"]
        except:
            nextPageToken = None

    return items

def GetPlaylistItems(client, playlist):
    id = playlist.playlistId

    kwargs = {
        'part': 'snippet',
        'maxResults': 50,
        'playlistId': id
    }

    items = _GetPlaylistItems(client, kwargs)
    return items
