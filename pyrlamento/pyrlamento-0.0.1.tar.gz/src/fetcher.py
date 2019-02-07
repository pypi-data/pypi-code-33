import requests
import logging

log = logging.getLogger(__name__)

http_headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:1.0) Gecko/20100101 Pyrlamento'}


class Session:
    """
    A session behaves like a browser session, maintaining (some) state across requests.
    """

    def __init__(self):
        self.__requests_session__ = requests.Session()

    def get(self, url: str) -> requests.Response:
        """
        Fetches a remote URL using an HTTP GET method using the current session attributes
        :param url: URL to fetch
        :return: Request response
        """
        log.debug('Fetching:' + url)
        return self.__requests_session__.get(url, headers=http_headers)
