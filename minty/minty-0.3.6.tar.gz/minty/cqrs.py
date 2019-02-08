import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from functools import partial

from . import Base
from .infrastructure import InfrastructureFactory
from .repository import RepositoryFactory


def event(name: str):
    def register_event(f):
        f.minty_event_name = name
        return f

    return register_event


class Event(Base):
    __slots__ = [
        "context",
        "user_uuid",
        "domain",
        "event_name",
        "parameters",
        "uuid",
        "created_date",
    ]

    def __init__(
        self,
        context: str,
        user_uuid: str,
        domain: str,
        event_name: str,
        parameters: dict,
    ):
        self.context = context
        self.user_uuid = user_uuid
        self.domain = domain
        self.event_name = event_name
        self.parameters = parameters
        self.uuid = uuid.uuid4()
        self.created_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(
            f"Event created. Context = '{context}, '"
            + f"user = '{user_uuid}', "
            + f"domain = '{domain}', "
            + f"event = '{event_name}', "
            + f"uuid = '{self.uuid}', "
            + f"created_date = '{self.created_date}', "
            + f"parameters = '{parameters}'"
        )


class MiddlewareBase(Base, ABC):
    __slots__ = ["infrastructure_factory", "context"]

    def __init__(self, infrastructure_factory=None):
        """Initialize class with infrastructure_factory and context.

        :param infrastructure_factory: infra structure factory, defaults to None
        :type infrastructure_factory: InfrastructureFactory, optional
        :param context: context the current query/command runs in
        :type context: str
        :param user_uuid: UUID of the user executing the query or command
        :type user_uuid: uuid
        """
        self.infrastructure_factory = infrastructure_factory

    @abstractmethod
    def __call__(self, func, event: Event):
        """Call instantiated class.

        Override this method (including the defined params) in your middleware
        class. The logic or functionality you want to implement should go
        before and after your call to `func()`.

        :param func: function to execute
        :type func: partial function
        :param event: event
        :type event: Event
        """
        pass


class InfrastructureStateManager(MiddlewareBase):
    """Set current event in infrastructure factory and clear it after the event is finished.

    Set the event in the infrastructure_factory so different layers can
    retrieve the cached infrastructure session(s)

    :param MiddlewareBase: middleware base class
    :type MiddlewareBase: MiddlewareBase
    """

    def __call__(self, func, event: Event):
        func()
        self.infrastructure_factory.flush_local_storage()


class TimeFunctionCall(MiddlewareBase):
    """Time and log function call to statsd.

    :param MiddlewareBase: middleware base class
    :type MiddlewareBase: MiddlewareBase
    """

    def __call__(self, func, event: Event):
        """Execute, time and log function call."""
        timer = self.statsd.get_timer(event.domain)
        with timer.time(f"{event.event_name}.execute"):
            func()


class CommandWrapper(Base):
    """Wrapper class for command instances. Handles creation of Events."""

    def __init__(self, domain, command_instance, context, user_uuid):
        self.domain = domain
        self.command_instance = command_instance
        self.middlewares = []
        self.context = context
        self.user_uuid = user_uuid

    def register_middleware(self, middleware: MiddlewareBase):
        """Register middleware to be wrapped around command.

        From inner to outer layer, the last middleware class to get registered will be
        the outer shell and will be executed first and last.

        :param middleware: middleware to register
        :type middleware: MiddlewareBase
        """
        self.middlewares.append(middleware)

    def __getattr__(self, attr):
        """Get an attribute on the wrapped class, wrapped by "event" code.

        This event code ensures the command can't return anything, and creates
        an Event instance.

        :param attr: attribute to retrieve
        :type attr: str
        :return: wrapped method
        :rtype: callable
        """
        orig_attr = self.command_instance.__getattribute__(attr)
        if callable(orig_attr):

            def wrapped(*args, **kwargs):
                """Return attribute wrapped in middlewares."""
                event_name = orig_attr.minty_event_name
                event = Event(
                    self.context,
                    self.user_uuid,
                    self.domain,
                    event_name,
                    kwargs,
                )

                wrapped_func = partial(orig_attr, **kwargs)
                for middleware in self.middlewares:
                    wrapped_func = partial(
                        middleware, func=wrapped_func, event=event
                    )

                wrapped_func()
                return

            return wrapped
        else:
            return orig_attr


class CQRS(Base):
    """Keep commands and queries separated.

    CQRS: Command Query Responsibility Separation
    """

    __slots__ = [
        "domains",
        "infrastructure_factory",
        "command_wrapper_middleware",
    ]

    def __init__(
        self,
        domains,
        infrastructure_factory: InfrastructureFactory,
        command_wrapper_middleware=None,
    ):
        """Create a new CQRS instance from a list of domains.

        :param domains: iterable returning domains. Domains are classes or
            packages with at least a "REQUIRED_REPOSITORIES" variable defining
            which repositories are necessary to use the domain.
        :type domains: object
        :param infrastructure_factory: Infrastructure factory, created with
            the required configuration, that the repositories can use to
            create infrastructure instances.
        :type infrastructure_factory: InfrastructureFactory
        :param command_wrapper_middleware: Middlewares to be wrapped around command
        :type command_wrapper_middleware: list of MiddlewareBase
        """
        self.domains = {}

        if command_wrapper_middleware is None:
            command_wrapper_middleware = []
        self.command_wrapper_middleware = command_wrapper_middleware

        self.infrastructure_factory = infrastructure_factory

        for domain in domains:
            repo_factory = RepositoryFactory(infrastructure_factory)

            for name, repo in domain.REQUIRED_REPOSITORIES.items():
                repo_factory.register_repository(name=name, repository=repo)

                for name, infra in repo.REQUIRED_INFRASTRUCTURE.items():
                    infrastructure_factory.register_infrastructure(
                        name=name, infrastructure=infra
                    )

            self.domains[domain.__name__] = {
                "module": domain,
                "repository_factory": repo_factory,
            }

    def get_query_instance(self, domain: str, context, user_uuid):
        """Instantiate and return the "query" part of the specified domain.

        :param domain: name of the domain to get the query instance for
        :type domain: str
        :param context: context for this query instance
        :type context: str
        :param user_uuid: UUID of the user that's going to execute commands
        :type user_uuid: uuid
        """
        # This can probably be cached (per context = host)

        self.logger.debug(
            f"Creating query instance for domain '{domain}' with context "
            + f"'{context}' for user '{user_uuid}'"
        )

        with self.statsd.get_timer(domain).time("get_query_instance"):
            query_instance = self.domains[domain]["module"].get_query_instance(
                self.domains[domain]["repository_factory"],
                context=context,
                user_uuid=user_uuid,
            )

        return query_instance

    def get_command_instance(self, domain: str, context, user_uuid):
        """Instantiate and return the "command" instance of the specified domain.

        Command instance is instantiated with optional layers of middleware to handle
        various functions when executing a command. `InfrastructureStateManager` is
        always registerd as the outermost layer & `TimeFunctionCall` is always
        registered as the innermost layer.

        :param domain: name of the domain to get the query instance for
        :type domain: str
        :param context: context for this command instance
        :type context: str
        :param user_uuid: UUID of the user that's going to execute commands
        :type user_uuid: uuid
        """
        self.logger.debug(
            f"Creating command instance for domain '{domain}' with context "
            + f"'{context}' for user '{user_uuid}'"
        )
        with self.statsd.get_timer(domain).time("get_command_instance"):
            cmd_instance = self.domains[domain]["module"].get_command_instance(
                self.domains[domain]["repository_factory"],
                context=context,
                user_uuid=user_uuid,
            )
            cmd_wrapped = CommandWrapper(
                domain, cmd_instance, context=context, user_uuid=user_uuid
            )

            # Innermost layer to time and do method call
            cmd_wrapped.register_middleware(TimeFunctionCall())

            for middleware in self.command_wrapper_middleware:
                middleware_init = middleware(self.infrastructure_factory)
                cmd_wrapped.register_middleware(middleware_init)

            # Outermost layer to manage infrastructure state
            cmd_wrapped.register_middleware(
                InfrastructureStateManager(self.infrastructure_factory)
            )
        return cmd_wrapped
