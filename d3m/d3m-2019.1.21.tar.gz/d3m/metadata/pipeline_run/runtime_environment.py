import json
import logging
import os
import typing
import uuid

import git  # type: ignore

import d3m
from d3m import utils
from d3m.environment_variables import (
    D3M_BASE_IMAGE_NAME, D3M_BASE_IMAGE_DIGEST, D3M_IMAGE_NAME, D3M_IMAGE_DIGEST
)

from .compute_resources import ComputeResources

__all__ = ('RuntimeEnvironment',)

logger = logging.getLogger(__name__)

DOCKER_MAC_ADDRESS_MASK = 0x0242ac110000


class RuntimeEnvironment:
    """
    A description of the environment in which a pipeline was run.
    Generates the JSON structure of the environment in the pipeline_run schema.

    Warning: API of this class will be changed in the future.

    Attributes
    ----------
    resources : typing.Optional[ComputeResources]
        A description of the compute resources available in this environment.
    reference_benchmarks : typing.Optional[typing.Sequence[str]]
        A list of ids of standard and optional additional benchmarks which were run in the same or
        equivalent RuntimeEnvironment. The timing characteristics of these benchmarks can be
        expected to be the same as anything timed in this RuntimeEnvironment.
    reference_engine_version : typing.Optional[str]
        A git commit hash or version number for the reference engine used. If subclassing the
        reference engine, list it here.
    engine_version : typing.Optional[str]
        A git commit hash or version number for the engine used. This is primarily useful for the
        author. If using the reference engine directly, list its git commit hash or version number
        here as well as in the reference_engine_version.
    base_docker_image : typing.Optional[typing.Dict[str, str]]
        If the engine was run in a public or known docker container, specify the base docker image
        here.
    docker_image : typing.Optional[typing.Dict[str, str]]
        If the engine was run in a public or known docker container, specify the actual docker
        image here. This is primarily useful for the author.

    Parameters
    ----------
    worker_id: typing.Optional[str]
        A globally unique identifier for the machine on which the runtime is running.
        The idea is that multiple runs on the same system can be grouped together.
        If not provided, `uuid.getnode()` is used to obtain an identifier.
    resources : typing.Optional[ComputeResources]
        A description of the compute resources available in this environment.
    reference_benchmarks : typing.Optional[typing.Sequence[str]]
        A list of ids of standard and optional additional benchmarks which were run in the same or
        equivalent RuntimeEnvironment. The timing characteristics of these benchmarks can be
        expected to be the same as anything timed in this RuntimeEnvironment.
    reference_engine_version : typing.Optional[str]
        A git commit hash or version number for the reference engine used. If subclassing the
        reference engine, list it here.
    engine_version : typing.Optional[str]
        A git commit hash or version number for the engine used. This is primarily useful for the
        author. If using the reference engine directly, list its git commit hash or version number
        here as well as in the reference_engine_version.
    base_docker_image : typing.Optional[typing.Dict[str, str]]
        If the engine was run in a public or known docker container, specify the base docker image
        here.
    docker_image : typing.Optional[typing.Dict[str, str]]
        If the engine was run in a public or known docker container, specify the actual docker
        image here. This is primarily useful for the author.
    """

    def __init__(
        self, *, worker_id: typing.Optional[str] = None,
        resources: typing.Optional[ComputeResources] = None,
        reference_benchmarks: typing.Optional[typing.Sequence[str]] = None,
        reference_engine_version: typing.Optional[str] = None,
        engine_version: typing.Optional[str] = None,
        base_docker_image: typing.Optional[typing.Dict[str, str]] = None,
        docker_image: typing.Optional[typing.Dict[str, str]] = None
    ) -> None:
        self.worker_id = worker_id
        if self.worker_id is None:
            self.worker_id = self._get_worker_id()

        self.resources = resources
        if self.resources is None:
            self.resources = ComputeResources()

        self.reference_benchmarks = reference_benchmarks

        self.reference_engine_version = reference_engine_version
        if self.reference_engine_version is None:
            self.reference_engine_version = self._get_reference_engine_version()

        self.engine_version = engine_version
        if self.engine_version is None:
            self.engine_version = self.reference_engine_version

        self.base_docker_image = base_docker_image
        if self.base_docker_image is None:
            self.base_docker_image = self.get_base_docker_image()

        self.docker_image = docker_image
        if self.docker_image is None:
            self.docker_image = self.get_docker_image()

    def to_json_structure(self) -> typing.Optional[typing.Dict[str, typing.Any]]:
        json_structure: typing.Dict[str, typing.Any] = {}

        json_structure['worker_id'] = self.worker_id

        if self.resources is not None:
            resources_json_structure = self.resources.to_json_structure()
            if resources_json_structure is not None:
                json_structure['resources'] = resources_json_structure

        if self.reference_benchmarks is not None:
            json_structure['reference_benchmarks'] = self.reference_benchmarks

        if self.reference_engine_version is not None:
            json_structure['reference_engine_version'] = self.reference_engine_version

        if self.engine_version is not None:
            json_structure['engine_version'] = self.engine_version

        if self.base_docker_image is not None:
                json_structure['base_docker_image'] = self.base_docker_image

        if self.docker_image is not None:
            json_structure['docker_image'] = self.docker_image

        json_structure['id'] = utils.compute_hash_id(json_structure)

        return json_structure

    def _get_reference_engine_version(self) -> typing.Optional[str]:
        reference_engine_version = None
        try:
            # get the git commit hash of the d3m repo
            path = os.path.abspath(d3m.__file__).rsplit('d3m', 1)[0]
            reference_engine_version = utils.current_git_commit(
                path=path, search_parent_directories=False
            )
        except git.exc.InvalidGitRepositoryError as e:
            reference_engine_version = d3m.__version__
        return reference_engine_version

    @classmethod
    def _get_docker_image(
        cls, image_name_env_var: str, image_digest_env_var: str
    ) -> typing.Optional[typing.Dict]:
        docker_image = {}

        if image_name_env_var not in os.environ:
            logger.warning('Docker image environment variable not set: %(variable_name)s', {
                'variable_name': image_name_env_var,
            })
        elif os.environ['image_name_env_var']:
            docker_image['image_name'] = os.environ['image_name_env_var']

        if image_digest_env_var not in os.environ:
            logger.warning('Docker image environment variable not set: %(variable_name)s', {
                'variable_name': image_digest_env_var,
            })
        elif os.environ['image_digest_env_var']:
            docker_image['image_digest'] = os.environ['image_digest_env_var']

        if docker_image:
            return docker_image
        else:
            return None

        return docker_image

    @classmethod
    def get_base_docker_image(cls) -> typing.Optional[typing.Dict]:
        return cls._get_docker_image(D3M_BASE_IMAGE_NAME, D3M_BASE_IMAGE_DIGEST)

    @classmethod
    def get_docker_image(cls) -> typing.Optional[typing.Dict]:
        return cls._get_docker_image(D3M_IMAGE_NAME, D3M_IMAGE_DIGEST)

    def _get_worker_id(self) -> str:
        mac_address = uuid.getnode()
        if mac_address >> 16 == DOCKER_MAC_ADDRESS_MASK >> 16:
            # Docker generates MAC addresses in the range 02:42:ac:11:00:00 to 02:42:ac:11:ff:ff
            # if one is not provided in the configuration
            logger.warning(
                "'worker_id' was generated using the MAC address inside Docker "
                "container and is not a reliable compute resource identifier."
            )
        elif (mac_address >> 40) % 2 == 1:
            # uuid.getnode docs state:
            # If all attempts to obtain the hardware address fail, we choose a
            # random 48-bit number with its eighth bit set to 1 as recommended
            # in RFC 4122.
            logger.warning(
                "'worker_id' was generated using a random number because the "
                "MAC address could not be determined."
            )
        return str(uuid.uuid5(utils.HASH_ID_NAMESPACE, json.dumps(mac_address, sort_keys=True)))
