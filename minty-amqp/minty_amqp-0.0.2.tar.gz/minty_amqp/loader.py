from minty import Base
from minty.config.parser.json_parser import JSONConfigParser
from minty.cqrs import CQRS
from minty.infrastructure import InfrastructureFactory

from .client import AMQPClient


class AMQPLoader(Base):
    """Loads the `AMQPClient` and inits with `CQRS` and `InfrastructureFactory`."""

    def __init__(
        self,
        domains: list,
        config_path: str,
        command_wrapper_middleware: list = None,
    ):
        """Parse config file and call setup method.

        :param Base: minty base class
        :type Base: class
        :param domains: domains to initialize in CQRS layer
        :type domains: list
        :param config_path: path to config_file.json
        :type config_path: str
        :param command_wrapper_middleware: middleware to initialize , defaults to None
        :param command_wrapper_middleware: list, optional
        """
        if command_wrapper_middleware is None:
            command_wrapper_middleware = []

        self.command_wrapper_middleware = command_wrapper_middleware
        self.domains = domains
        self.config = self._parse_application_config(config_path)

        self.setup()

    def setup(self):
        """"Initializes AMQPClient with `CQRS` and `InfrastructureFactory`."""
        infra_factory = InfrastructureFactory(
            config_file=self.config["config_file"],
            config_parser=JSONConfigParser,
        )

        self.cqrs = CQRS(
            domains=self.domains,
            infrastructure_factory=infra_factory,
            command_wrapper_middleware=self.command_wrapper_middleware,
        )

        self.amqp_client = AMQPClient(
            rabbitmq_url=self.config["url"], cqrs=self.cqrs
        )

        for consumer in self.config["consumers"]:
            self.amqp_client.register_consumer_from_config(consumer)

    def start_client(self):
        """Start amqp client."""

        self.amqp_client.start()

    def _parse_application_config(self, filename: str):
        """Parse JSON config file.

        :param filename: filename
        :type filename: str
        :return: config
        :rtype: dict
        """
        with open(filename, "r", encoding="utf-8") as config_file:
            content = config_file.read()
        return JSONConfigParser().parse(content)
