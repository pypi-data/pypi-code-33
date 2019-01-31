from __future__ import print_function
import yaml

from orchestrate.common import safe_format
from orchestrate.core.lib.types import is_mapping
from orchestrate.core.services.base import Service


class JobRunnerService(Service):
  def env_vars(self, experiment_id):
    return {
      'ORCHESTRATE_EXPERIMENT_ID': experiment_id,
      'SIGOPT_API_TOKEN': self.services.sigopt_service.api_token,
    }

  def format_resources(self, resource_options):
    resources = {'limits': [], 'requests': []}

    for resource in ('requests', 'limits'):
      if is_mapping(resource_options.get(resource)):
        resources[resource] = [{'key': key, 'value': val} for key, val in resource_options.get(resource, {}).items()]

    if resource_options.get('gpus'):
      resources['limits'].append({'key': 'nvidia.com/gpu', 'value': resource_options.get('gpus')})

    return resources

  def render_job_spec_file(self, experiment_id, optimization_options, image_name, resource_options):
    parallel_bandwidth = optimization_options.get('parallel_bandwidth', 1)
    formated_resources = self.format_resources(resource_options)

    template_args = dict(
      environment_variables=[
        {'name': key, 'value': value}
        for key, value in self.env_vars(experiment_id).items()
      ],
      image_name=image_name,
      job_name=self.job_name(experiment_id),
      parallel_bandwidth=parallel_bandwidth,
      resource_limits=formated_resources['limits'],
      resource_requests=formated_resources['requests'],
    )

    return self.services.template_service.render_template_from_file(
      'job_runner/job-spec.yml.ms',
      template_args,
    )

  def job_name(self, experiment_id):
    return safe_format('orchestrate-{}', experiment_id)

  def experiment_id(self, job_name):
    if job_name.startswith('orchestrate-'):
      return job_name[len('orchestrate-'):]
    return None

  def create_sigopt_experiment(self, name, optimization_options):
    data = optimization_options.copy()
    data.pop('sigopt', dict())

    try:
      metadata = data.pop('metadata')
    except KeyError:
      metadata = dict()

    # Note: We could concatenate this string with a uuid to further reduce the possibility of collision
    if 'orchestrate_experiment' not in metadata:
      metadata['orchestrate_experiment'] = "True"

    experiment = self.services.sigopt_service.create_experiment(name=name, metadata=metadata, **data)
    return experiment.id

  def run_job(self, image_name, name, optimization_options, resource_options):
    self.services.kubernetes_service.check_nodes_are_ready()

    experiment_id = self.create_sigopt_experiment(name, optimization_options)
    rendered_job_spec = self.render_job_spec_file(
      experiment_id,
      optimization_options,
      image_name,
      resource_options,
    )

    self.services.kubernetes_service.start_job(yaml.load(rendered_job_spec))
    return experiment_id

  def run_local_job(self, image_name, name, optimization_options):
    experiment_id = self.create_sigopt_experiment(name, optimization_options)

    self.services.docker_service.run(
      image_name,
      env=self.env_vars(experiment_id),
    )

    return experiment_id
