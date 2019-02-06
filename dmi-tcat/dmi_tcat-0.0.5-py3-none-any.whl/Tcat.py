import requests
import logging

class Tcat():
    """A class to represent a TCAT instance."""
    def __init__(self, url, username, password):
        """Initialize a TCAT API."""
        self.logger = logging.getLogger()
        self.endpoint = f'{url}/api/'
        self.auth = (username, password)
        self._binnames = None
        self._bins = {}
        
    def _query(self, action, param=None):
        """Utility to request query bins."""
        url = f'{self.endpoint}{action}'
        if param:
            url = f'{url}/{param}'
        resp = requests.get(url, auth=self.auth, headers={'accept': 'application/json'})
        data = resp.json()
        del(data['original_request'])
        return data

    def bins(self):
        """List the bins in this TCAT."""
        if not self._binnames:
            self.logger.debug('Refreshing bins')
            self._binnames = list(self._query('querybin.php').values())
        return self._binnames
    
    def get_bin(self, binname):
        """Get information about a particular bin."""
        self.logger.debug(f'Getting bin {bin}')
        try:
            return self._bins[binname]
        except KeyError:
            self._bins[binname] = self._query('querybin.php', binname)
            return self._bins[binname]
    
    def get_all_bins(self):
        """Ask the instance to fetch and get cache all bins"""
        for qbin in self.bins():
            self.get_bin(qbin)
