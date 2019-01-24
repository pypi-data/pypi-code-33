# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.client.RestClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    REST client implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import requests

from pip_services3_commons.config import ConfigParams, IConfigurable
from pip_services3_commons.run import IOpenable, IClosable
from pip_services3_commons.refer import IReferenceable
from pip_services3_components.connect import ConnectionParams, ConnectionResolver
from pip_services3_components.log import CompositeLogger
from pip_services3_components.count import CompositeCounters
from pip_services3_commons.errors import ConfigException, UnknownException, InvocationException
from pip_services3_commons.errors import ErrorDescription, ApplicationExceptionFactory
from pip_services3_commons.data import IdGenerator
from ..connect.HttpConnectionResolver import HttpConnectionResolver

class RestClient(IOpenable, IConfigurable, IReferenceable):
    """
    Abstract client that calls remove endpoints using HTTP/REST protocol.

    ### Configuration parameters ###
    - base_route:              base route for remote URI
    - connection(s):
        - discovery_key:         (optional) a key to retrieve the connection from IDiscovery
        - protocol:              connection protocol: http or https
        - host:                  host name or IP address
        - port:                  port number
        - uri:                   resource URI or connection string with all parameters in it
    - options:
        - retries:               number of retries (default: 3)
        - connect_timeout:       connection timeout in milliseconds (default: 10 sec)
        - timeout:               invocation timeout in milliseconds (default: 10 sec)

    ### References ###

    - *:logger:*:*:1.0         (optional) ILogger components to pass log messages
    - *:counters:*:*:1.0         (optional) ICounters components to pass collected measurements
    - *:discovery:*:*:1.0        (optional) IDiscovery services to resolve connection

    Example:
        class MyRestClient(RestClient, IMyClient):
            def get_data(self, correlation_id, id):
                timing = self.instrument(correlationId, 'myclient.get_data')
                result = self._controller.get_data(correlationId, id)
                timing.end_timing()
                return result

            ...

        client = MyRestClient()
        client.configure(ConfigParams.fromTuples("connection.protocol", "http",
                                                 "connection.host", "localhost",
                                                 "connection.port", 8080))

        data = client.getData("123", "1")
        ...
    """
    _default_config = None 

    _client = None
    _uri = None
    _timeout = 1000
    _connection_resolver = None
    _logger = None
    _counters = None
    _options = None
    _base_route = None
    _retries = 1
    _headers = None
    _connect_timeout = 1000


    def __init__(self):
        """
        Creates a new instance of the client.
        """
        self._connection_resolver = HttpConnectionResolver()
        self._default_config = ConfigParams.from_tuples(
            "connection.protocol", "http",
            "connection.host", "0.0.0.0",
            "connection.port", 3000,

            "options.timeout", 10000,
            "options.request_max_size", 1024 * 1024,
            "options.connect_timeout", 10000,
            "options.retries", 3,
            "options.debug", True
        )
        self._logger = CompositeLogger()
        self._counters = CompositeCounters()
        self._options = ConfigParams()
        self._headers = {}


    def set_references(self, references):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._connection_resolver.set_references(references)


    def configure(self, config):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        config = config.set_defaults(self._default_config)
        self._connection_resolver.configure(config)

        self._options.override(config.get_section("options"))
        self._retries = config.get_as_integer_with_default("options.retries", self._retries)
        self._connect_timeout = config.get_as_integer_with_default("options.connect_timeout", self._connect_timeout)
        self._timeout = config.get_as_integer_with_default("options.timeout", self._timeout)
        self._base_route = config.get_as_string_with_default("base_route", self._base_route)

    def _instrument(self, correlation_id, name):
        """
        Adds instrumentation to log calls and measure call time. It returns a Timing object that is used to end the time measurement.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param name: a method name.

        :return: Timing object to end the time measurement.
        """
        self._logger.trace(correlation_id, "Calling " + name + " method")
        return self._counters.begin_timing(name + ".call_time")

    def is_opened(self):
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self._client != None

    def open(self, correlation_id):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self.is_opened():
            return

        connection = self._connection_resolver.resolve(correlation_id)

        self._uri = connection.get_uri()
        if self._uri == None:
            protocol = connection.get_protocol("http")
            host = connection.get_host()
            port = connection.get_port()
            self._uri = protocol + "://" + host + ":" + str(port)

        self._client = requests

        self._logger.debug(correlation_id, "Connected via REST to " + self._uri)


    def close(self, correlation_id):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self._client != None:
            self._logger.debug(correlation_id, "Disconnected from " + self._uri)

        self._client = None
        self._uri = None


    def _to_json(self, obj):
        if obj == None:
            return None

        if isinstance(obj, set):
            obj = list(obj)
        if isinstance(obj, list):
            result = []
            for item in obj:
                item = self._to_json(item)
                result.append(item)
            return result

        if isinstance(obj, dict):
            result = {}
            for (k, v) in obj.items():
                v = self._to_json(v)
                result[k] = v
            return result
        
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        if hasattr(obj, '__dict__'):
            return self._to_json(obj.__dict__)
        return obj


    def call(self, method, route, correlation_id = None, params = None, data = None):
        """
        Calls a remote method via HTTP/REST protocol.

        :param method: HTTP method: "get", "head", "post", "put", "delete"

        :param route: a command route. Base route will be added to this route

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param params: (optional) query parameters.

        :param data: (optional) body object.

        :return: result object
        """
        method = method.upper()
                
        params = params or {}
        if correlation_id != None:
            params['correlation_id'] = correlation_id
        else:
            params['correlation_id'] = IdGenerator.next_short()

        route = self._uri + route
        response = None
        result = None
                    
        try:
            # Call the service
            data = self._to_json(data)
            response = requests.request(method, route, params=params, json=data, timeout=self._timeout)
        except Exception as ex:
            error = InvocationException(correlation_id, 'REST_ERROR', 'REST operation failed: ' + str(ex)).wrap(ex)
            raise error

        if response.status_code == 404 or response.status_code == 204:
            return None

        try:
            # Retrieve JSON data
            result = response.json()
        except:
            # Data is not in JSON
            if response.status_code < 400:
                raise UnknownException(correlation_id, 'FORMAT_ERROR', 'Failed to deserialize JSON data: ' + response.text) \
                    .with_details('response', response.text)
            else:
                raise UnknownException(correlation_id, 'UNKNOWN', 'Unknown error occured: ' + response.text) \
                    .with_details('response', response.text)

        # Return result
        if response.status_code < 400:
            return result

        # Raise error
        # Todo: We need to implement proper from_value method
        error = ErrorDescription.from_json(result)
        error.status = response.status_code

        raise ApplicationExceptionFactory.create(error)
