"""twitchvod models.py"""

import json
from enum import Enum
from .utils import locate_with_default


STREAM_EXT_MEDIA_STARTS_WITH = "#EXT-X-STREAM-INF:"


class HttpMethod(Enum):
    """Enum to describe an HTTP method and the corresponding value."""

    GET = "GET"
    POST = "POST"
    HEAD = "HEAD"
    PUT = "PUT"


class AccessToken:
    """Class to represent an AccessToken object"""

    def __init__(self, token_data):
        """Initializer for the AccessToken object. This access token is used
        to request information about a particular VOD.

        :params token_data: token data from Client.get_access_token.

        :rtype: None.
        """

        self.token = token_data
        self.vod_id = self._parse_vod_id(token_data)

    def __repr__(self):
        """String representation of the AccessToken Class."""

        return "<AccessToken [{}-vod_id]>".format(self.vod_id)

    # pylint: disable=no-self-use
    def _parse_vod_id(self, token_data):
        """Attempt to parse the vod_id from the access token data.

        :param token_data: Access token from Client.get_accessP_token.
        :type token_data: dict.

        :return: The vod_id included in the access token data.
        :rtype: int.
        """

        return json.loads(token_data["token"]).get("vod_id")


def get_ext_media_indexes(m3u8_data):
    """Extract the pair of indexes from the m3u8_data list for each
    variation of the VOD. Each variation is for a different quality and or
    resolution.

    Each stream variation consists of two rows from the output. This method
    just groups those records together by tracking the indexes.

    Below is an example of the two types of records we are grouping. The first
    one is metadata for the stream, and the next record contains the actual
    url to the transport stream index for that quality.

    ...
    1: #EXT-X-STREAM-INF: <resolution>, <frame-rate>, other metadata...
    2: https://vod-metro.twitch.tv/...
    ...

    :param m3u8_data: A list of strings that describe the different stream
                      qualities / variations.
    :type m3u8_data: list[str].
    :return: A list of tuples that contain integers that represent the rows to
             be extracted for each stream variation.
    :rtype: list[tuple[int, int]].
    """

    rows_to_extract = []

    for rec_num, record in enumerate(m3u8_data):
        if record.startswith(STREAM_EXT_MEDIA_STARTS_WITH):
            rows_to_extract.append((rec_num, rec_num+1,))

    return rows_to_extract


def parse_stream_info_from_response(raw_m3u8_response):
    """Parse the raw stream info response from the m3u8 data into a list of
    Vod objects.  Each one of these objects represents a
    different variation / resolution / framerate of a VOD.

    :param raw_m3u8_response: A string of characters from the m3u8 Twitch
                              endpoint.
    :type raw_m3u8_response: str.
    :return: A list of Vod objects.
    :rtype: list[Vod].
    """

    records = raw_m3u8_response.splitlines()
    indexes = get_ext_media_indexes(records)
    vod_versions = []

    for record_index, url_index in indexes:
        inf_record = records[record_index]
        url = records[url_index]
        vod_versions.append(
            parse_stream_version_info_from_raw(inf_record, url)
        )

    return vod_versions


def parse_stream_version_info_from_raw(raw_stream_data, stream_url):
    """Build a models.Vod object from raw data that comes from the Twitch
    stream information.

    :param raw_stream_data: a string of chararacters to be parsed.
    :param stream_url: a string of characters representing the url of the
                       vod stream.
    :return: A Vod object.
    :rtype: Vod.
    """

    prog_id = locate_with_default(r"PROGRAM-ID=(\d*?),", raw_stream_data)
    program_id = int(prog_id) if prog_id is not None else None

    bandw = locate_with_default(r"BANDWIDTH=(\d*?),", raw_stream_data)
    bandwidth = int(bandw) if bandw is not None else None

    cdcs = locate_with_default(r"CODECS=\"(\S*?)\",", raw_stream_data)
    codecs = cdcs.split(",") if cdcs is not None else None

    video = locate_with_default(r"VIDEO=\"(\S*?)\"", raw_stream_data)
    resolution = locate_with_default(r"RESOLUTION=\"(\S*?)\"", raw_stream_data)

    return Vod(
        program_id=program_id,
        bandwidth=bandwidth,
        codecs=codecs,
        resolution=resolution,
        video=video,
        url=stream_url
    )


class Vod:
    """Class that represents the information regarding a particular stream
    version.
    """

    def __init__(
            self,
            program_id=None,
            bandwidth=None,
            codecs=None,
            resolution=None,
            video=None,
            url=None
    ):
        """Initialize an instance of a Vod Class with parsed
        data from the m3u8 file.

        :param program_id: (optional) program-id from m3u8 file.
        :type program_id: int.
        :param bandwidth: (optional) bandwidth from m3u8 file.
        :type bandwidth: int.
        :param codecs: (optional) list of codecs from the m3u8 file.
        :type codecs: list[str].
        :param resolution: (optional) resolution from the m3u8 file.
        :type resolution: str.
        :param video: (optional) video from the m3u8 file.
        :type video: str.
        :param url: (optional) url provided from the m3u8 file.
        :type url: str.

        :rtype: None
        """

        self.program_id = program_id
        self.bandwidth = bandwidth
        self.codecs = codecs if codecs is not None else []
        self.resolution = resolution
        self.video = video
        self.url = url

    def __repr__(self):
        return "<Vod [{}{}]>".format(
            self.video,
            "," + self.resolution if self.resolution else ""
        )

    def __eq__(self, other):
        """Compare two SteamVersionInfo objects.

        :param other: Instance of another Vod object.
        :type other: Vod.

        :return: Boolean if both instances have equal __dict__ attributes.
        :rtype: bool.
        """

        return self.__dict__ == other.__dict__


def strip_last_filename_from_url(url, sep="/"):
    """Given a url with a filename at the end, strip the last part off of the
    url and return the previous segment. If the seperator can't be located,
    this method will return the unmodified url.

    > strip_last_filename_from_ur("http://utldr.co/s/document.html")
    > "http://utldr.co/s/"

    :param url: The url to trim the filename off of.
    :type url: str.
    :param sep: (optional) Seperator to use when splitting the filename.

    :returns: The url with the last filename chopped off.
    :rtype: str.
    """

    path = "".join(reversed(url))
    index = path.find(sep)

    if index == -1:
        return url

    return "".join(reversed(path[index:]))


def parse_stream_indexes_from_response(raw_index_response):
    """Parse the data from the stream index response to locate all of the
    different MPEG-2 transport stream files. Return a list of all files found
    in the index response.

    :param raw_index_response: Stream index response data.
    :type raw_index_response: str.

    :returns: List of MPEG-2 transport stream files.
    :rtype: list[str].
    """

    indexes = []

    for row in raw_index_response.splitlines():
        ts_filename = locate_with_default(r"^(\d*.ts)$", row)
        if ts_filename:
            indexes.append(ts_filename)

    return indexes


class VodChunk:
    """Class that represents the Vod Index information that has been parsed
    from Twitch. Users can use this class to loop over the MPEG-2 transport
    stream files / urls.
    """

    def __init__(self, base_url):
        """Initializer for the VodChunk Class. with the provided
        base_url.

        :param base_url: The base url for the MPEG-2 transport stream files.
        :type base_url: str.

        :rtype: None.
        """

        self._base_url = base_url
        self._index_files = []

    def __repr__(self):
        """String representation of the Class."""

        return "<VodChunk [{}-chunks]>".format(len(self._index_files))

    def __eq__(self, other):
        """Compare this with other VodChunk instances."""

        return self.__dict__ == other.__dict__

    def add_chunk(self, index_filename):
        """Add an index to the VodChunk object.

        :param index_filename: The new filename to add to the index. "5.ts".
        :type index_filename: str.

        :rtype: None.
        """

        self._index_files.append(index_filename)

    def chunks(self):
        """Return a generator that yields an full index paths. These will be the
        full url to the MPEG-2 transport stream file.

        :returns: Generator that yields MPEG-2 transport stream files.
        :rtype: Generator.
        """

        for index in self._index_files:
            yield (index, self._base_url + index,)
