from . import Base
from .infrastructure import InfrastructureFactory


class RepositoryFactory(Base):
    """Create context-specific "repository" instances for domains
    """

    __slots__ = ["infrastructure_factory", "repositories"]

    def __init__(self, infra_factory: InfrastructureFactory):
        """Initialize the repository factory with an infrastructure factory

        :param infra_factory: Infrastructure factory
        :type infra_factory: InfrastructureFactory
        """
        self.infrastructure_factory = infra_factory
        self.repositories = {}

    def register_repository(self, name: str, repository: object):
        """Register a repository class with the repository factory.

        :param repository: repository class; will be instantiated when the
            domain code asks for it by name.
        :type repository: object
        """
        self.repositories[name] = repository

    def get_repository(self, name: str, context=None):
        """Retrieve a repository, given a name and optionally a context.

        :param name: name of repository to instantiate
        :type repository: str
        :param context: Context for which to retrieve the repository.
        :type context: object, optional
        :return: An instance of the configured repository, for the specified
            context.
        :rtype: object
        """
        repo_class = self.repositories[name]

        self.logger.debug(
            f"Creating repository of type '{name}' with context "
            + f"'{context}'"
        )

        with self.statsd.get_timer("get_repository").time(name):
            repo = repo_class(
                context=context,
                infrastructure_factory=self.infrastructure_factory,
            )

        return repo
