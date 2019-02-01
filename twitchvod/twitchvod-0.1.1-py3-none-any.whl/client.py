"""twitchvod client.py"""

import requests

from .models import (HttpMethod, VodChunk, AccessToken,
                     strip_last_filename_from_url,
                     parse_stream_indexes_from_response,
                     parse_stream_info_from_response,)

from .exceptions import HTTPClientError, HTTPServerError, HTTPGenericError


class Client:
    """HTTP Client to interact with the Twitch API to fetch VOD information."""

    TOKEN_PATTERN = "https://api.twitch.tv/api/vods/{vod_id}/access_token"
    VOD_M3U8_PATTERN = "https://usher.ttvnw.net/vod/{vod_id}.m3u8"

    USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Ubuntu Chromium/71.0.3578.98 "
        "Chrome/71.0.3578.98 Safari/537.36"
    )

    def __init__(self, client_id):
        """Initializer for the twitchvod Client. This client take a client_id
        for the current user. This client id is used to make requests to
        Twitch on your behalf.

        :param client_id: The client_id for your twitch dev account.
        :type client_id: str.

        :rtype: None.
        """

        self._client_id = client_id

    def __repr__(self):
        """String representation of the Class."""

        return "<Client>"

    def _send_request(self, method, path, params=None, headers=None):
        """Send a request to the specified path using the supplied HTTP method
        and parameters (if required). It will return an HTTP Response upon
        success and raise the appropriate twitchvod.exceptions.HTTPError on
        non-200 responses.

        :param method: The desired HTTP method to use.
        :type method: The twitchvod.models.HttpMethod.
        :param path: The path to use in the request.
        :type path: str.
        :param params: (optional) The params to send with the request.
        :type params: dict.
        :param headers: (optional) The headers to send in the request.
        :rtype headers: dict.

        :returns: HTTP response.
        :rtype: requests.Response.
        """

        if headers is not None:
            headers = self._apply_useragent(headers)

        http_response = requests.request(
            method.value,
            path,
            params=params,
            headers=headers
        )

        self._raise_on_status(http_response)

        return http_response

    def _apply_useragent(self, headers):
        """Apply a default useragent to the headers param if it does not exist
        in the supplied headers already.

        :param headers: The headers to apply the user agent string to.
        :type headers: dict.

        :return: Headers with the user-agent included.
        :rtype: dict.
        """

        if "user-agent" not in [a.lower() for a in list(headers.keys())]:
            headers["User-Agent"] = self.USER_AGENT

        return headers

    # pylint: disable=no-self-use
    def _raise_on_status(self, response):
        """Inspect the status on the response parameter and raise the matching
        client exception based on the HTTP status code.

        :param response: The HTTP response.
        :type response: requests.Response.
        """

        stat = response.status_code

        if stat in range(400, 500):
            raise HTTPClientError(
                "Client HTTP error code. Status={0}".format(stat),
                http_response=response
            )
        elif stat in range(500, 600):
            raise HTTPServerError(
                "Server HTTP error code. Status={0}".format(stat),
                http_response=response
            )
        elif stat not in range(200, 300):
            raise HTTPGenericError(
                "Generic HTTP error code. Status={0}".format(stat),
                http_response=response
            )

    def get_access_token(self, vod_id):
        """Get the VOD access token required to pull metadata related to that
        data on the Twitch services. Will raise different HTTPError exceptions
        based on the non-200 status code of the response.

        :param vod_id: The id of VOD the user wants to fetch metadata on.
        :type vod_id: int.

        :returns: The access token data from the Twitch services.
        :rtype: models.AccessToken.
        """

        response = self._send_request(
            HttpMethod.GET,
            self.TOKEN_PATTERN.format(vod_id=vod_id),
            params={"client_id": self._client_id}
        )

        return AccessToken(response.json())

    def _get_vod_m3u8_refs(self, vod_access_token):
        """Get the raw response string from fetching the m3u8 data from the
        Twitch services. This request uses the the previously requested access
        tokens for this particular VOD. Raw content is a list of MPEG-2
        transport stream files. Will raise different HTTPError exceptions
        based on the non-200 status code of the response.

        :param vod_access_token: The access token generated with the Client
                                 method get_vod_access_token.
        :type vod_access_token: models.AccessToken.

        :returns: The unmodified text from the m3u8 request.
        :rtype: str.
        """

        req_params = {
            "client_id": self._client_id,
            "token": vod_access_token.token["token"],
            "sig": vod_access_token.token["sig"],
            "allow_source": "true",
            "allow_audio_only": "true"
        }

        raw_resp = self._send_request(
            HttpMethod.GET,
            self.VOD_M3U8_PATTERN.format(vod_id=vod_access_token.vod_id),
            params=req_params
        )

        return raw_resp.text

    def get_vods(self, vod_access_token):
        """Fetch a variety of stream qualities/resolutions from Twitch for
        a given VOD token. Returns a list of models.Vod objects.
        Will raise different HTTPError exceptions based on the non-200 status
        code of the response.

        :param vod_access_token: The access token generated with the Client
                                 method get_vod_access_token.
        :type vod_access_token: dict.

        :returns: A list of models.Vod objects.
        :rtype: list[models.Vod].
        """

        return parse_stream_info_from_response(
            self._get_vod_m3u8_refs(vod_access_token)
        )

    def get_chunks(self, vod):
        """Fetch the MPEG-2 transport stream paths contained in
        models.VodChunk for the supplied models.Vod object parameter.
        Will raise different HTTPError exceptions based on the non-200 status
        code of the response.

        :param vod: The selected vod.
        :type vod: models.Vod.

        :returns: Data related to the different MPEG-2 transport streams for
                  the supplied stream variation.
        :rtype: models.VodChunk.
        """

        index_resp = self._send_request(
            HttpMethod.GET,
            vod.url
        )

        base_url = strip_last_filename_from_url(vod.url)
        index_names = parse_stream_indexes_from_response(index_resp.text)

        indexes = VodChunk(base_url)

        for index in index_names:
            indexes.add_chunk(index)

        return indexes
