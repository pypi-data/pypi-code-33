import pytest
from mock import Mock
import re

from orchestrate.core.template.service import TemplateService
from orchestrate.core.resource.service import ResourceService

class TestTemplateService(object):
  @pytest.fixture
  def template_service(self):
    services = Mock()
    services.resource_service = ResourceService(services)
    return TemplateService(services)

  def test_job_spec(self, template_service):
    template_args = dict(
      environment_variables=[
        {'name': 'test_env_name', 'value': 'test_env_value'}
      ],
      image_name="test_image_name",
      job_name="test_job_name",
      parallel_bandwidth=1,
      resource_limits=[
        {'key': 'nvidia.com/gpu', 'value': 1},
        {'key': 'cpu', 'value': 2},
        {'key': 'memory', 'value': '5Gi'}
      ],
      resource_requests=[{'key': 'cpu', 'value': 1}, {'key': 'memory', 'value': '2Gi'}]
    )
    job_spec_template = template_service.render_template_from_file('job_runner/job-spec.yml.ms', template_args)
    assert re.search('[ \t]+cpu: 1\n', job_spec_template)
    assert re.search('[ \t]+cpu: 2\n', job_spec_template)
    assert re.search('[ \t]+nvidia.com/gpu: 1\n', job_spec_template)
    assert re.search('[ \t]+memory: 2Gi\n', job_spec_template)
    assert re.search('[ \t]+memory: 5Gi\n', job_spec_template)
