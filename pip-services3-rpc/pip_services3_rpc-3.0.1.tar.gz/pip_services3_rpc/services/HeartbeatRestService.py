# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.HeartbeatRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Heartbeat rest service implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import datetime

from pip_services3_commons.convert import StringConverter

from .RestService import RestService

class HeartbeatRestService(RestService):
    """
    Service returns heartbeat via HTTP/REST protocol.The service responds on /heartbeat route (can be changed) with a string with the current time in UTC. This service route can be used to health checks by loadbalancers and container orchestrators.

    ### Configuration parameters ###

    - base_route:              base route for remote URI (default: "")
    - route:                   route to heartbeat operation (default: "heartbeat")
    - dependencies:
        - endpoint:              override for HTTP Endpoint dependency
    - connection(s):
    - discovery_key:         (optional) a key to retrieve the connection from IDiscovery
    - protocol:              connection protocol: http or https
    - host:                  host name or IP address
    - port:                  port number
    - uri:                   resource URI or connection string with all parameters in it

    ### References ###

    - *:logger:*:*:1.0         (optional) ILogger components to pass log messages
    - *:counters:*:*:1.0         (optional) ICounters components to pass collected measurements
    - *:discovery:*:*:1.0        (optional) IDiscovery services to resolve connection
    - *:endpoint:http:*:1.0          (optional) HttpEndpoint reference

    Example:
          service = HeartbeatService()
          service.configure(ConfigParams.from_tuples("route", "ping",
                                                     "connection.protocol", "http",
                                                     "connection.host", "localhost",
                                                     "connection.port", 8080))

          service.open("123")
          ...
    """
    _route = "heartbeat"

    def __init__(self):
        """
        Creates a new instance of this service.
        """
        super(HeartbeatRestService, self).__init__()

    def configure(self, config):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        super(HeartbeatRestService, self).configure(config)
        self._route = config.get_as_string_with_default("route", self._route)

    def register(self):
        """
        Registers all service routes in HTTP endpoint.
        """
        self.register_route("GET", self._route, self.heartbeat())

    def heartbeat(self):
        """
        Handles heartbeat requests

        :return: http response to the request.
        """
        result = StringConverter.to_string(datetime.datetime.now())
        return self.send_result(result)


