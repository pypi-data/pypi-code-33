# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.client.DirectClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Direct client implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_commons.run import IOpenable
from pip_services3_commons.config import ConfigParams, IConfigurable
from pip_services3_commons.refer import Descriptor, IReferences, IReferenceable, DependencyResolver
from pip_services3_components.log import CompositeLogger
from pip_services3_components.count import CompositeCounters
from pip_services3_commons.errors import ConnectionException

class DirectClient(IConfigurable, IReferenceable, IOpenable):
    """
    Abstract client that calls controller directly in the same memory space. It is used when multiple microservices are deployed in a single container (monolyth) and communication between them can be done by direct calls rather then through the network.

    ### Configuration parameters ###

    - dependencies:
        - controller:            override controller descriptor

    ### References ###

    - *:logger:*:*:1.0         (optional) ILogger components to pass log messages
    - *:counters:*:*:1.0         (optional) ICounters components to pass collected measurements
    - *:controller:*:*:1.0     controller to call business methods

    Example:
        class MyDirectClient(DirectClient, IMyClient):
            def __init__(self):
                super(MyDirectClient, self).__init__()
                self._dependencyResolver.put('controller', Descriptor("mygroup", "controller", "*", "*", "*"))

            ...

            def get_data(self, correlation_id, id):
                timing = self.instrument(correlationId, 'myclient.get_data')
                result = self._controller.get_data(correlationId, id)
                timing.end_timing()
                return result

            client = MyDirectClient()
            client.set_references(References.from_tuples(Descriptor("mygroup","controller","default","default","1.0"), controller))
            data = client.get_data("123", "1")
            ...
    """
    _controller = None
    _opened = True
    _logger = None
    _counters = None
    _dependency_resolver = None

    def __init__(self):
        """
        Creates a new instance of the client.
        """
        self._logger = CompositeLogger()
        self._counters = CompositeCounters()
        self._dependency_resolver = DependencyResolver()
        self._dependency_resolver.put('controller', 'none')

    def configure(self, config):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        self._dependency_resolver.configure(config)

    def set_references(self, references):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._dependency_resolver.set_references(references)
        self._controller = self._dependency_resolver.get_one_required('controller')

    def _instrument(self, correlation_id, name):
        """
        Adds instrumentation to log calls and measure call time. It returns a Timing object that is used to end the time measurement.

        :param correlation_id: (optional) transaction id to trace execution through call chain.

        :param name: a method name.

        :return: Timing object to end the time measurement.
        """
        self._logger.trace(correlation_id, "Executing " + name + " method")
        return self._counters.begin_timing(name + ".call_time")

    def is_opened(self):
        """
        Checks if the component is opened.

        :return: true if the component has been opened and false otherwise.
        """
        return self._opened

    def open(self, correlation_id):
        """
        Opens the component.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self._opened:
            return
        
        if self._controller == None:
            raise ConnectionException(correlation_id, 'NO_CONTROLLER', 'Controller references is missing')

        self._opened = True
        self._logger.info(correlation_id, 'Opened direct client')

    def close(self, correlation_id):
        """
        Closes component and frees used resources.

        :param correlation_id: (optional) transaction id to trace execution through call chain.
        """
        if self._opened:
            self._logger.info(correlation_id, 'Closed direct client')

        self._opened = False

