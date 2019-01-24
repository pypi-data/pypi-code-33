# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.StatusRestService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Status rest service implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import datetime

from pip_services3_commons.convert import StringConverter
from pip_services3_commons.refer import Descriptor
from pip_services3_commons.run import Parameters

from .RestService import RestService

class StatusRestService(RestService):
    """
    Service that returns microservice status information via HTTP/REST protocol. The service responds on /status route (can be changed) with a JSON object:

    {
        - "id":            unique container id (usually hostname)
        - "name":          container name (from ContextInfo)
        - "description":   container description (from ContextInfo)
        - "start_time":    time when container was started
        - "current_time":  current time in UTC
        - "uptime":        duration since container start time in milliseconds
        - "properties":    additional container properties (from ContextInfo)
        - "components":    descriptors of components registered in the container
    }

    ### Configuration parameters ###

    - base_route:              base route for remote URI
    - dependencies:
        - endpoint:              override for HTTP Endpoint dependency
        - controller:            override for Controller dependency
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
          service = StatusService()
          service.configure(ConfigParams.from_tuples("connection.protocol", "http",
                                                     "connection.host", "localhost",
                                                     "connection.port", 8080))
          service.open("123")
          ...
    """
    _start_time = datetime.datetime.now()
    _references_ = None
    _context_info = None
    _route = "status"

    def __init__(self):
        """
        Creates a new instance of this service.
        """
        super(StatusRestService, self).__init__()
        self._dependency_resolver.put("context-info", Descriptor("pip-services", "context-info", "default", "*", "1.0"))

    def configure(self, config):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        super(StatusRestService, self).configure(config)

        self._route = config.get_as_string_with_default("route", self._route)

    def set_references(self, references):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._references_ = references

        super(StatusRestService, self).set_references(references)

        self._context_info = self._dependency_resolver.get_one_optional("context-info")

    def register(self):
        """
        Registers all service routes in HTTP endpoint.
        """
        self.register_route("GET", self._route, self.status())

    def status(self):
        id = self._context_info.get_context_id() if self._context_info != None else ""
        name = self._context_info.get_name() if self._context_info != None else "unknown"
        description = self._context_info.get_description() if self._context_info != None else ""
        uptime = datetime.datetime.now().time() - self._start_time.time()
        properties = self._context_info.get_properties() if self._context_info != None else ""

        components = []
        if self._references_ != None:
            for locator in self._references_.get_all_locators():
                components.append(locator.__str__)

        status = Parameters.from_tuples("id", id,
                                        "name", name,
                                        "description", description,
                                        "start_time", StringConverter.to_string(self._start_time),
                                        "current_time", StringConverter.to_string(datetime.datetime.now()),
                                        "uptime", uptime,
                                        "properties", properties,
                                        "components", components)
        self.send_result(status)

