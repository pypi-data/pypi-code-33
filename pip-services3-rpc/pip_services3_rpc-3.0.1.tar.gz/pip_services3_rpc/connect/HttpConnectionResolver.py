# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.connect.HttpConnectionResolver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    HttpConnectionResolver implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from urllib.parse import urlparse

from pip_services3_commons.config import IConfigurable
from pip_services3_commons.errors import ConfigException
from pip_services3_commons.refer import IReferenceable
from pip_services3_components.connect import ConnectionResolver


class HttpConnectionResolver(IReferenceable, IConfigurable):
    """
    Helper class to retrieve connections for HTTP-based services abd clients. In addition to regular functions of ConnectionResolver is able to parse http:// URIs and validate connection parameters before returning them.

    ### Configuration parameters ###

    - connection:
        - discovery_key:               (optional) a key to retrieve the connection from IDiscovery
        - ...                          other connection parameters
    - connections:                   alternative to connection
        - [connection params 1]:       first connection parameters
        -  ...
        - [connection params N]:       Nth connection parameters
        -  ...

    ### References ###

    - *:discovery:*:*:1.0        (optional) IDiscovery services to resolve connection

    Example:
          config = ConfigParams.from_tuples("connection.host", "10.1.1.100","connection.port", 8080)
          connectionResolver = HttpConnectionResolver()
          connectionResolver.configure(config)
          connectionResolver.set_references(references)
          params = connectionResolver.resolve("123")
    """
    _connection_resolver = None

    def __init__(self):
        """
        Create connection resolver.
        """
        self._connection_resolver = ConnectionResolver()

    def configure(self, config):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._connection_resolver.configure(config)

    def set_references(self, references):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._connection_resolver.set_references(references)

    def validate_connection(self, correlation_id, connection):
        if connection == None:
            return ConfigException(correlation_id, "NO_CONNECTION", "HTTP connection is not set")

        uri = connection.get_uri()
        if uri == None:
            return None

        protocol = connection.get_protocol("http")
        if protocol != "http":
            return ConfigException(correlation_id,
                                   "WRONG_PROTOCOL",
                                   "Protocol is not supported by REST connection")\
                .with_details("protocol", protocol)

        host = connection.get_host()
        if host == None:
            return ConfigException(correlation_id, "NO_HOST", "Connection host is not set")

        port = connection.get_port()
        if port == 0:
            return ConfigException(correlation_id, "NO_PORT", "Connection port is not set")

    def update_connection(self, connection):
        if connection == None:
            return

        uri = connection.get_uri()

        if uri == None or uri == "":
            protocol = connection.get_protocol("http")
            host = connection.get_host()
            port = connection.get_port()

            uri = protocol + "://" + host
            if port != 0:
                uri = uri + ":" + str(port)
            connection.set_uri(uri)

        else:
            address = urlparse(uri)
            connection.set_protocol(address.scheme)
            connection.set_host(address.hostname)
            connection.set_port(address.port)

    def resolve(self, correlation_id):
        """
        Resolves a single component connection. If connections are configured to be retrieved from Discovery service it finds a IDiscovery and resolves the connection there.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :return: resolved connection.
        """
        connection = self._connection_resolver.resolve(correlation_id)
        self.validate_connection(correlation_id, connection)
        self.update_connection(connection)
        
        return connection

    def resolve_all(self, correlation_id):
        """
        Resolves all component connection. If connections are configured to be retrieved from Discovery service it finds a IDiscovery and resolves the connection there.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :return: resolved connections.
        """
        connections = self._connection_resolver.resolve_all(correlation_id)
        for connection in connections:
            self.validate_connection(correlation_id, connection)
            self.update_connection(connection)

        return connections

    def register(self, correlation_id):
        """
        Registers the given connection in all referenced discovery services. This method can be used for dynamic service discovery.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        connection = self._connection_resolver.resolve(correlation_id)
        self.validate_connection(correlation_id, connection)
        self._connection_resolver.register(correlation_id, connection)



