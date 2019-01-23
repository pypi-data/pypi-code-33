import pytest
from mock import Mock

from orchestrate.core.provider.constants import (
  Provider,
  string_to_provider,
)
from orchestrate.core.provider.broker import ProviderBroker

class TestProviderBroker(object):
  @pytest.fixture
  def services(self):
    return Mock()

  @pytest.fixture
  def provider_broker(self, services):
    return ProviderBroker(services)

  def test_get_provider_service(self, provider_broker, services):
    assert provider_broker.get_provider_service(string_to_provider('aws')) == services.aws_service
    assert provider_broker.get_provider_service(string_to_provider('AWS')) == services.aws_service
    assert provider_broker.get_provider_service(Provider.AWS) == services.aws_service

  def test_custom_provider(self, provider_broker, services):
    assert provider_broker.get_provider_service(string_to_provider('custom')) == services.custom_cluster_service
    assert provider_broker.get_provider_service(Provider.CUSTOM) == services.custom_cluster_service

  def test_unknown_provider(self, provider_broker):
    with pytest.raises(NotImplementedError):
      provider_broker.get_provider_service(0)
