import dependency_injector.containers as containers
import dependency_injector.providers as providers

from .aaa_app_client import AAAAppClient


class DependencyContainer(containers.DeclarativeContainer):
    aaa = providers.Factory(AAAAppClient)
