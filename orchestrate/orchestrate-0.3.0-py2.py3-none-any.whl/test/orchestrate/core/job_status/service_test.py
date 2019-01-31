import pytest
from mock import Mock, MagicMock

from orchestrate.core.job_status.service import JobStatusService

class TestJobStatusService(object):
  @pytest.fixture
  def services(self):
    return Mock()

  @pytest.fixture
  def job_status_service(self, services):
    return JobStatusService(services)

  def test_parse_job_no_conditions(self, job_status_service):
    mock_job = self.get_job_mock()
    job_status_service.parse_job(mock_job)

  @pytest.mark.parametrize('conditions,expected_status', [
    ([], 'Not Complete'),
    ([dict(status='True', type='Complete')], 'Complete'),
    ([dict(status='False', type='Complete')], 'Not Complete'),
    ([dict(status='Unknown', type='Complete')], 'Maybe Complete'),
    ([
      dict(status='True', type='Foo'),
      dict(status='False', type='Bar'),
      dict(status='Unknown', type='Baz'),
    ], 'Foo, Not Bar, Maybe Baz'),
  ])
  def test_parse_job_conditions(self, job_status_service, conditions, expected_status):
    condition_mocks = []
    for c in conditions:
      condition_mocks.append(self.get_condition_mock(c['status'], c['type']))
    job_mock = self.get_job_mock(condition_mocks)

    assert job_status_service.parse_job(job_mock)['status'] == expected_status

  def get_condition_mock(self, status, cond_type):
    mock = Mock()
    mock.status = status
    mock.type = cond_type
    return mock

  def get_job_mock(self, condition_mocks=None):
    mock = MagicMock()
    mock.metadata.name = 'job'
    if condition_mocks:
      mock.status.conditions = condition_mocks
    else:
      mock.status.conditions = None
    return mock
