from __future__ import print_function
from collections import namedtuple
import json
import requests
import sys
from tempfile import NamedTemporaryFile
import urllib3

import docker
from six import raise_from

from orchestrate.common import safe_format
from orchestrate.core.exceptions import CheckConnectionError, ModelPackingError
from orchestrate.core.services.base import Service
from orchestrate.version import DOCKER_IMAGE_VERSION


DockerLoginCredentials = namedtuple('DockerLoginCredentials', [
  'username',
  'password',
  'registry',
])


class DockerService(Service):
  def __init__(self, services):
    super(DockerService, self).__init__(services)
    self._client = docker.from_env()

  @property
  def client(self):
    return self._client

  def check_connection(self):
    try:
      self.client.images.list()
    except (docker.errors.DockerException, requests.exceptions.ConnectionError) as e:
      raise_from(
        CheckConnectionError(safe_format('An error occurred while checking your docker connection: {}', str(e))),
        e,
      )

  def print_logs(self, logs):
    for log in logs:
      sys.stdout.write(log)
      sys.stdout.flush()

  def stream_build_log(self, logs, dockerfile, show_all_logs):
    downloading = False
    for log_line in logs:
      for json_log in log_line.decode('utf-8').splitlines():
        parsed_log = json.loads(json_log)
        if 'error' in parsed_log:
          if show_all_logs:
            print(parsed_log['error'], file=sys.stderr)
          raise ModelPackingError(parsed_log['error'], dockerfile)
        elif 'status' in parsed_log:
          if not downloading and parsed_log['status'] == 'Downloading':
            yield 'Downloading the framework...\n'
            downloading = True
        elif 'stream' in parsed_log:
          if show_all_logs:
            yield parsed_log['stream']
          downloading = False

  def build(
    self,
    tag=None,
    dockerfile_name=None,
    dockerfile_contents=None,
    directory=None,
    quiet=True,
    build_args=None,
    show_all_logs=False,
  ):
    if dockerfile_contents:
      assert not dockerfile_name, \
        "only one of dockerfile_name, dockerfile_contents can be provided"
      with NamedTemporaryFile(mode='w', delete=False) as dockerfile_fp:
        dockerfile_fp.write(dockerfile_contents)
        dockerfile = dockerfile_fp.name
    else:
      dockerfile = dockerfile_name
    try:
      if quiet:
        return self.client.images.build(
          tag=tag,
          dockerfile=dockerfile,
          path=directory,
          quiet=quiet,
          buildargs=build_args,
          rm=True,
        )[0]
      else:
        assert tag is not None, \
          "tag must be specified when quiet=False in order to return the appropriate image"
        raw_logs = self.client.api.build(
          tag=tag,
          dockerfile=dockerfile,
          path=directory,
          quiet=quiet,
          buildargs=build_args,
          rm=True,
        )
        self.print_logs(self.stream_build_log(raw_logs, dockerfile, show_all_logs))
        return self.client.images.get(tag)
    except docker.errors.BuildError as e:
      raise_from(ModelPackingError(str(e), dockerfile), e)

  def push(self, repository, tag=None, retries=1, quiet=True):
    for try_number in range(retries + 1):
      try:
        for line in self.client.images.push(repository=repository, tag=tag, stream=True):
          for l in line.decode('utf-8').splitlines():
            obj = json.loads(l)
            if 'error' in obj:
              raise Exception(obj['error'])
      except urllib3.exceptions.ReadTimeoutError:
        if try_number >= retries:
          raise
        elif not quiet:
          print("Docker push failed, retrying...")

  def login(self, docker_login_credentials):
    creds = docker_login_credentials
    response = self.client.login(
      username=creds.username,
      password=creds.password,
      registry=creds.registry,
    )
    assert response.get('Status') == 'Login Succeeded', safe_format(
      'Docker failed logging into registry {} with username {}',
      creds.registry,
      creds.username,
    )

  def run(self, image, command=None, env=None, quiet=False):
    env = env or {}
    if quiet:
      self.client.containers.run(
        image,
        command=command,
        environment=env,
        remove=True,
      )
    else:
      container = self.client.containers.run(
        image,
        command=command,
        detach=True,
        environment=env,
        remove=True,
        stdout=True,
        stderr=True,
      )
      try:
        self.print_logs(log.decode('utf-8') for log in container.logs(stream=True))
      finally:
        try:
          container.kill()
        except (docker.errors.NotFound, docker.errors.APIError):
          pass

  def untag(self, image):
    for tag in image.tags:
      self.client.images.remove(tag)

  def untag_all(self, label):
    for image in self.client.images.list(filters={'label': label}):
      self.untag(image)

  def clean(self, remove_current_frameworks=False):
    if remove_current_frameworks:
      self.untag_all(label='orchestrate-docker-image-version')
    else:
      self.untag_all(label='orchestrate-user-created')
      versions = {
        image.labels['orchestrate-docker-image-version']
        for image in self.client.images.list(filters={'label': 'orchestrate-docker-image-version'})
      }
      versions.discard(DOCKER_IMAGE_VERSION)
      for version in versions:
        self.untag_all(label=safe_format('orchestrate-docker-image-version={}', version))
    self.client.images.prune(filters={'label': 'orchestrate-docker-image-version'})
