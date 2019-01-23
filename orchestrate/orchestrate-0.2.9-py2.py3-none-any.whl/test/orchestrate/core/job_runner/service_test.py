import pytest
from mock import Mock

from orchestrate.core.job_runner.service import JobRunnerService

class TestJobRunnerService(object):
  @pytest.fixture
  def services(self):
    return Mock()

  @pytest.fixture
  def job_runner_service(self, services):
    return JobRunnerService(services)

  def test_job_name(self, job_runner_service):
    experiment_id = '234234'
    assert job_runner_service.experiment_id(job_runner_service.job_name(experiment_id)) == experiment_id

  def test_experiment_id(self, job_runner_service):
    job_name = 'orchestrate-o3u42-owskj'
    assert job_runner_service.job_name(job_runner_service.experiment_id(job_name)) == job_name

  def test_old_job_name(self, job_runner_service):
    job_name = 'galileo-o3u42-owskj'
    assert job_runner_service.experiment_id(job_name) is None

  def test_render_job_spec_file(self, job_runner_service):
    job_runner_service.render_job_spec_file(1, {}, "test_i", dict(
      gpus=3,
      requests={'cpu': 4, 'memory': '2Gi'},
      limits={'cpu': 55, 'memory': '20Gi'},
    ))

  @pytest.mark.parametrize('resources,output', [
      (
        dict(
          requests={'cpu': 5}
        ),
        dict(
          requests=[{'key': 'cpu', 'value': 5}],
          limits=[],
        ),
      ),
      (
        dict(
          requests={'cpu': '300m'},
          gpus=1,
        ),
        dict(
          requests=[{'key': 'cpu', 'value': '300m'}],
          limits=[{'key': 'nvidia.com/gpu', 'value': 1}]
        ),
      ),
      (
        dict(
          requests={'cpu': '1'},
          limits={'memory': '2Gi', 'cpu': 2},
          gpus=1,
        ),
        dict(
          requests=[{'key': 'cpu', 'value': '1'}],
          limits=[{'key': 'memory', 'value': '2Gi'}, {'key': 'cpu', 'value': 2}, {'key': 'nvidia.com/gpu', 'value': 1}],
        )
      ),
  ])
  def test_format_resources(self, job_runner_service, resources, output):
    formated_resources = job_runner_service.format_resources(resources)
    sorted_resources_requests = sorted(formated_resources.get('requests', []), key=lambda k: k['key'])
    sorted_output_requests = sorted(output.get('requests', []), key=lambda k: k['key'])
    sorted_resources_limits = sorted(formated_resources.get('limits', []), key=lambda k: k['key'])
    sorted_output_limits = sorted(output.get('limits', []), key=lambda k: k['key'])
    assert sorted_resources_requests == sorted_output_requests and sorted_resources_limits == sorted_output_limits
