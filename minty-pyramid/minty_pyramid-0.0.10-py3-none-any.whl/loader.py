from minty import Base
from minty.cqrs import CQRS
from minty.infrastructure import InfrastructureFactory
from pyramid.config import Configurator

from .session_manager import SessionRetriever, session_manager_factory


class Engine(Base):
    """Pyramid configurator."""

    __slots__ = ["config", "domains", "command_wrapper_middleware"]

    def __init__(self, domains: list, command_wrapper_middleware: list = None):
        if command_wrapper_middleware is None:
            command_wrapper_middleware = []
        self.command_wrapper_middleware = command_wrapper_middleware
        self.domains = domains
        self.config = None

    def setup(self, global_config: dict, **settings) -> object:
        """Set up the application by loading the injecting the CQRS layer.

        :param global_config: Global configuration
        :type global_config: dict
        :return: Returns the Configurator from Pyramid
        :rtype: object
        """
        infra_factory = InfrastructureFactory(
            settings["minty_service.infrastructure.config_file"]
        )
        config = Configurator(settings=settings)

        cqrs = CQRS(
            domains=self.domains,
            infrastructure_factory=infra_factory,
            command_wrapper_middleware=self.command_wrapper_middleware,
        )
        config.include(_build_cqrs_setup(cqrs))

        if settings.get("session_manager", False):
            session_manager = session_manager_factory(
                infra_factory=infra_factory
            )
            config.include(_build_http_session_manager(session_manager))

        # TODO 400/404/500 handlers (JSON Output)

        config.add_tween("minty_pyramid.loader.RequestTimer")

        config.scan()
        self.config = config
        return config

    def main(self) -> object:
        """Run the application by calling the wsgi_app function of Pyramid.

        :raises ValueError: When setup is forgotten
        :return: wsgi app
        :rtype: object
        """
        if self.config is None:
            raise ValueError("Make sure you run setup before 'main'")

        self.logger.info("Creating WSGI application")
        return self.config.make_wsgi_app()


def _build_cqrs_setup(cqrs):
    """Create a callable for setting up the "CQRS" methods request objects.

    :param cqrs: A configured CQRS object
    :type cqrs: CQRS
    :return: A function, callable by Pyramid, to register the CQRS
        method(s)
    :rtype: callable
    """

    def setup_cqrs_request(config):
        """Add the CQRS accessors to the Pyramid request objects.

        :param config: Pyramid configurator instance
        :type config: Configurator
        :return: Nothing
        :rtype: None
        """

        def get_query_instance(request, domain: str):
            return cqrs.get_query_instance(domain, context=request.host)

        config.add_request_method(get_query_instance, "get_query_instance")

        def get_command_instance(request, domain: str):
            return cqrs.get_command_instance(domain, context=request.host)

        config.add_request_method(get_command_instance, "get_command_instance")

    return setup_cqrs_request


def _build_http_session_manager(session_manager: SessionRetriever):
    """Create a callable to set up the `retrieve_session` method on request objects.
    :param session_manager: A configured SessionRetriever object

    :type session_manager: SessionRetriever
    :return: A function, callable by Pyramid, to register the session_manager
        method(s)
    :rtype: callable
    """

    def setup_session_request(config):
        """Add the SessionRetriver accessors to the Pyramid request objects.

        :param config: Pyramid configurator instance
        :type config: Configurator
        :return: Nothing
        :rtype: None
        """

        def retrieve_session(request, session_id: str):
            session = session_manager.retrieve(session_id)
            return session

        config.add_request_method(retrieve_session, "retrieve_session")

    return setup_session_request


class RequestTimer(Base):
    """Middleware / tween to log request time and count to statsd."""

    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        """Log time and count to statsd before and after execution of handler.

        :param request: request
        :type request: class
        :return: response
        :rtype: class
        """
        timer = self.statsd.get_timer()
        timer.start()

        response = self.handler(request)

        try:
            req_name = request.matched_route.name
        except AttributeError:
            req_name = "unknown"

        timer.stop(f"{req_name}.time")

        self.statsd.get_counter().increment(
            f"{req_name}.{response.status_int}.count"
        )

        return response
