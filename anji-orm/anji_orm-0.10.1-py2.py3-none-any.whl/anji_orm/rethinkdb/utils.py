from typing import Dict
from urllib.parse import urlparse

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.1"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["parse_rethinkdb_connection_uri"]

CONNECTION_URI_MAPPING = {
    'hostname': 'host',
    'port': 'port',
    'username': 'user',
    'password': 'password',
}


def parse_rethinkdb_connection_uri(connection_uri: str) -> Dict:
    parsed_url = urlparse(connection_uri)
    connection_kwargs = {}
    for uri_field, connection_arg in CONNECTION_URI_MAPPING.items():
        if getattr(parsed_url, uri_field):
            connection_kwargs[connection_arg] = getattr(parsed_url, uri_field)
    if parsed_url.query:
        connection_kwargs.update({
            x[0]: x[1] for x in (x.split('=') for x in parsed_url.query.split('&'))
        })
    return connection_kwargs
