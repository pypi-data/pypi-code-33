from client import Client
from models import parse_stream_info_from_response
from downloader import download_vod
import requests

VOD_ID = "371106349"
CLIENT_ID = "jzkbprff40iqj646a697cyrvl0zt2m6"


if __name__ == "__main__":

    c = Client(CLIENT_ID)
    token = c.get_vod_access_token(VOD_ID)
    streams = c.get_stream_info(token, VOD_ID)
    indexes = c.get_stream_indexes(streams[0])
    download_vod(indexes)

    # for filename, url in indexes.index_paths():
        # with open("data/{0}".format(filename), "wb+") as ts_file:
            # ts_file.write(
                # requests.get(url).content
            # )

# ffmpeg -i all.ts -acodec copy -vcodec copy all.mp4