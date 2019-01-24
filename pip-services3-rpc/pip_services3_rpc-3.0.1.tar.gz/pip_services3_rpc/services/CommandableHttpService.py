# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.CommandableHttpService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Commandable HTTP service implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.refer import IReferences
from pip_services3_commons.commands import ICommandable, CommandSet
from pip_services3_commons.run import Parameters

from .RestService import RestService

class CommandableHttpService(RestService):
    """
    Abstract service that receives remove calls via HTTP/REST protocol to operations automatically generated for commands defined in ICommandable components. Each command is exposed as POST operation that receives all parameters in body object. Commandable services require only 3 lines of code to implement a robust external HTTP-based remote interface.

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
          class MyCommandableHttpService(CommandableHttpService):
              def __init__(self):
                  super(MyCommandableHttpService, self).__init__()
                  self._dependencyResolver.put("controller", Descriptor("mygroup","controller","*","*","1.0"))

              ...

          service = MyCommandableHttpService()
          service.configure(ConfigParams.from_tuples("connection.protocol", "http",
                                                    "connection.host", "localhost",
                                                    "connection.port", 8080))
          service.set_references(References.from_tuples(Descriptor("mygroup","controller","default","default","1.0"), controller))
          service.open("123")
          ...
    """
    _name = None
    _command_set = None

    def __init__(self, name):
        """
        Creates a new instance of the service.

        :param name: a service base route.
        """
        super(CommandableHttpService, self).__init__()
        self._name = name
        self._dependency_resolver.put('controller', 'none')

    def _get_handler(self, command):
        def handler():
            params = self.get_data()
            correlation_id = params['correlation_id'] if 'correlation_id' in params else None
            args = Parameters.from_value(params)
            timing = self._instrument(correlation_id, self._name + '.' + command.get_name())
            try:
                result = command.execute(correlation_id, args)
                return self.send_result(result)
            finally:
                timing.end_timing()

        return handler

    def add_route(self):
        controller = self._dependency_resolver.get_one_required('controller')
        if not isinstance(controller, ICommandable):
            raise Exception("Controller has to implement ICommandable interface")
        self._command_set = controller.get_command_set()

        for command in self._command_set.get_commands():
            route = '/' + self._name + '/' + command.get_name()
            self.register_route('POST', route, None, self._get_handler(command))