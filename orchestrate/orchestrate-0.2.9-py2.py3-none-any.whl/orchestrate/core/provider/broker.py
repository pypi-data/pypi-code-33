from orchestrate.core.services.base import Service
from orchestrate.core.provider.constants import (
  Provider,
)


class ProviderBroker(Service):
  def get_provider_service(self, provider):
    if provider == Provider.AWS:
      return self.services.aws_service
    elif provider == Provider.CUSTOM:
      return self.services.custom_cluster_service
    else:
      raise NotImplementedError()
