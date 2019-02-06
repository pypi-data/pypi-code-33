import requests
import logging
from datetime import datetime


class Tcat():
    """Representation of a TCAT instance over the TCAT API.

    Supports only HTTP basic authentication."""

    _headers = {'accept': 'application/json'}

    def __init__(self, url, username, password, loadbins=False, verify=True):
        """Constructor.

        Parameters:
            url (string): Server address.
            username (string): user name.
            password (string): password.
            loadbins (bool): Pre-load all the bins. This is slow.
            verify (bool): Check the server SSL certificates.
        """
        self.endpoint = f'{url}/api/'
        self.auth = (username, password)
        self.logger = logging.getLogger('tcat')
        self.verify = verify
        self._binnames = None
        self._bins = {}

        try:
            self._handshake()
            if loadbins:
                self.load_all_bins()
        except requests.exceptions.HTTPError:
            raise

    def __str__(self):
        return f"{self.endpoint}"

    def __repr__(self):
        return f"{type(self)} {self.endpoint}"

    def _handshake(self):
        """Utility to check connection with TCAT instance."""
        requests.get(self.endpoint, auth=self.auth, verify=self.verify,
                     headers=type(self)._headers).raise_for_status()

    def _query(self, action, param=None):
        """Utility to request query bins."""
        url = f'{self.endpoint}{action}'
        if param:
            url = f'{url}/{param}'

        resp = requests.get(url, auth=self.auth, verify=self.verify,
                            headers=type(self)._headers)
        resp.raise_for_status()
        data = resp.json()
        del(data['original_request'])
        return data

    def bins(self, reload=False):
        """List the bins in this TCAT."""
        if not self._binnames or reload:
            self.logger.debug('Refreshing bins')
            self._binnames = list(self._query('querybin.php').values())
        return self._binnames

    def get_bin(self, binname, reload=False):
        """Get information about a particular bin."""
        self.logger.debug(f'Getting bin {bin}')
        if reload:
            del(self._bins[binname])
        try:
            return self._bins[binname]
        except KeyError:
            data = self._query('querybin.php', binname)
            self._bins[binname] = QueryBin(data)
            return self._bins[binname]

    def load_all_bins(self, reload=False):
        """Ask the instance to fetch and get cache all bins"""
        try:
            self._handshake()
            for qbin in self.bins():
                self.get_bin(qbin, reload=reload)
        except requests.exceptions.HTTPError:
            raise

    def notweets(self, binname, startdate, enddate):
        """Get the number of tweets in this bin."""
        raise NotImplementedError

    def tweets(self, binname, startdate, enddate, format='csv'):
        """Export tweets in CSV of TSV format."""
        raise NotImplementedError

    def purge(self):
        """Delete tweets from the selected time period."""
        raise NotImplementedError


class QueryBin():
    """Class to represent a query bin."""
    def __init__(self, data):
        """Constructor."""
        self.bin = data['bin']
        self.type = data['type']
        self.active = bool(int(data['active']))
        self.comments = data['comments']
        self.notweets = int(data['notweets'])
        try:
            self.mintime = datetime.fromisoformat(data['mintime'])
        except TypeError:
            self.mintime = None
        try:
            self.maxtime = datetime.fromisoformat(data['maxtime'])
        except TypeError:
            self.maxtime = None
        self.nohashtags = int(data['nohashtags'])
        self.nomentions = int(data['nomentions'])
        self.keywords = [kw.strip() for kw in data['keywords'].split(',')]

    def __str__(self):
        return f"{self.bin}"

    def __repr__(self):
        return f"{type(self)} {self.bin}"
