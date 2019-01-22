#!/usr/bin/env python
"""Abstract API over the Backscatter API."""
import json
import logging
import requests


__author__ = "Brandon Dixon"
__copyright__ = "Copyright, Backscatter"
__credits__ = ["Brandon Dixon"]
__license__ = "MIT"
__maintainer__ = "Brandon Dixon"
__email__ = "brandon@backscatter.io"
__status__ = "BETA"


class RequestFailure(Exception):
    """Exception to capture a failed request."""
    pass


class InvalidResponse(Exception):
    """Exception to capture a failed response parse."""
    pass


def valid_date(date):
    """Check the input date and ensure it matches the format."""
    import datetime
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")


def valid_ip(ip_address, strict=True):
    """Check if the IP address is valid."""
    import socket
    try:
        socket.inet_aton(ip_address)
        return True
    except socket.error:
        if strict:
            raise ValueError("Invalid IP address")
        return False


class Backscatter:

    """Abstract interface for Backscatter."""

    NAME = "Backscatter"
    LOG_LEVEL = logging.DEBUG
    BASE_URL = "https://api.backscatter.io"
    CLIENT_VERSION = 1
    API_VERSION = "v0"
    EP_ENRICHMENT = "enrichment/{query_type}"
    EP_OBSERVATIONS = "observations/{query_type}"
    EP_TRENDS_POPULAR = "trends/popular/{trend_type}"
    VALID_ENRICHMENT = ['ip', 'asn', 'network']
    VALID_OBSERVATIONS = ['ip', 'asn', 'country', 'network', 'port']
    VALID_TRENDS = ['ip', 'asn', 'country', 'network', 'port']

    def __init__(self, api_key, version=API_VERSION, log_level=LOG_LEVEL):
        """Init the object."""
        self._log = self._logger()
        self.api_key = api_key
        self.version = version
        self.set_log_level(log_level)

    def _logger(self):
        """Create a logger to be used between processes.

        :returns: Logging instance.
        """
        import sys
        logger = logging.getLogger(self.NAME)
        logger.setLevel(self.LOG_LEVEL)
        shandler = logging.StreamHandler(sys.stdout)
        fmt = '\033[1;32m%(levelname)-5s %(module)s:%(funcName)s():'
        fmt += '%(lineno)d %(asctime)s\033[0m| %(message)s'
        shandler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(shandler)
        return logger

    def set_log_level(self, level):
        """Set the log level."""
        to_set = 0
        if level == 20:
            to_set = logging.INFO
        if level == 10:
            to_set = logging.DEBUG
        if level == 40:
            to_set = logging.ERROR
        self._log.setLevel(to_set)

    def _request(self, endpoint, params=dict(), data=None):
        """Handle the requesting of information from the API."""
        client_value = "Python Backscatter v%s" % (str(self.CLIENT_VERSION))
        headers = {'X-Request-Client': client_value, 'X-API-Key': self.api_key}
        url = '/'.join([self.BASE_URL, self.API_VERSION, endpoint])
        self._log.debug('Requesting: %s', url)
        response = requests.get(url, headers=headers, timeout=7, params=params,
                                data=data)
        if response.status_code not in range(200, 299):
            raise RequestFailure(response.status_code, response.content)
        try:
            loaded = json.loads(response.content)
        except Exception as error:
            raise InvalidResponse(error)
        return loaded

    def get_observations(self, query, query_type, scope=None):
        """Get observations based on a specific query value.

        :param query: Value to search with
        :type query: str
        :param query_type: Type of observation search to run
        :type query_type: str
        :param scope: Days of history to search back from today
        :type scope: int
        :return: Listing of observations from Backscatter
        :rtype: dict
        """
        if query_type not in self.VALID_OBSERVATIONS:
            message = "Invalid observation type. Must be of: %s" % (', '.join(self.VALID_OBSERVATIONS))
            raise RequestFailure(message)
        endpoint = self.EP_OBSERVATIONS.format(query_type=query_type)
        params = {'query': query, 'scope': scope}
        return self._request(endpoint, params=params)

    def get_trends(self, trend_type, scope=None, size=25):
        """Get observations based on a specific query value.

        :param trend_type: Type of trend return
        :type trend_type: str
        :param scope: Days of history to search back from today
        :type scope: int
        :return: Listing of observations from Backscatter
        :rtype: dict
        """
        if trend_type not in self.VALID_TRENDS:
            message = "Invalid trend type. Must be of: %s" % (', '.join(self.VALID_TRENDS))
            raise RequestFailure(message)
        endpoint = self.EP_TRENDS_POPULAR.format(trend_type=trend_type)
        params = {'scope': scope, 'size': size}
        return self._request(endpoint, params=params)

    def enrich(self, query, query_type):
        """Enrich a specific value with additional context.

        :param query: Value to search with
        :type query: str
        :param query_type: Type of observation search to run
        :type query_type: str
        :return: Enrichment information for the query
        :rtype: dict
        """
        if query_type not in self.VALID_ENRICHMENT:
            message = "Invalid enrichment type. Must be of: %s" (', '.join(self.VALID_ENRICHMENT))
            raise RequestFailure(message)
        endpoint = self.EP_ENRICHMENT.format(query_type=query_type)
        params = {'query': query}
        return self._request(endpoint, params=params)
