import boto3

from orchestrate.core.services.base import Service


class AwsEcrService(Service):
  def __init__(self, services, **kwargs):
    super(AwsEcrService, self).__init__(services)
    self._client = boto3.client('ecr', **kwargs)

  @property
  def client(self):
    return self._client

  def create_repository(self, repository_name):
    return self.client.create_repository(repositoryName=repository_name)

  def describe_repositories(self, repository_names):
    return self.client.describe_repositories(repositoryNames=repository_names)

  def ensure_repositories(self, repository_names):
    for name in repository_names:
      try:
        self.create_repository(repository_name=name)
      except self.client.exceptions.RepositoryAlreadyExistsException:
        pass

    return self.describe_repositories(repository_names)

  def get_authorization_token(self, registry_ids):
    return self.client.get_authorization_token(registryIds=registry_ids)
