import pytest
from mock import Mock

from orchestrate.core.ecr.service import AwsEcrService

class TestAwsEcrService(object):
  @pytest.fixture
  def services(self):
    return Mock()

  def test_constructor(self, services):
    ecr_service = AwsEcrService(services)
    assert ecr_service.client is not None
