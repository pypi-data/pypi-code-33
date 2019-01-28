# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import os
import requests
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback
import uuid
import docker
from pkg_resources import resource_string
from azure.storage.common.storageclient import logger
from azureml.exceptions import WebserviceException
from azureml._model_management._constants import MMS_SYNC_TIMEOUT_SECONDS
from azureml._model_management._constants import MAX_HEALTH_CHECK_TRIES
from azureml._model_management._constants import HEALTH_CHECK_INTERVAL_SECONDS
from azureml._restclient.artifacts_client import ArtifactsClient

try:
    # python 3
    from urllib.parse import urlparse
except ImportError:
    # python 2
    from urlparse import urlparse


model_payload_template = json.loads(resource_string(__name__, 'data/mms_model_payload_template.json').decode('ascii'))
image_payload_template = json.loads(resource_string(__name__,
                                                    'data/mms_workspace_image_payload_template.json').decode('ascii'))
aks_service_payload_template = json.loads(resource_string(__name__,
                                                          'data/aks_service_payload_template.json').decode('ascii'))
aci_service_payload_template = json.loads(resource_string(__name__,
                                                          'data/aci_service_payload_template.json').decode('ascii'))


logger.setLevel(logging.CRITICAL)


def add_sdk_to_requirements():
    """
    Inject the SDK as a requirement for created images, since we use the SDK for schema and exception handling.
    :return: Path to the created pip-requirements file.
    :rtype: str
    """
    # always pass sdk as dependency to mms/ICE.
    generated_requirements = tempfile.mkstemp(suffix='.txt', prefix='requirements')[1]
    sdk_requirements_string = 'azureml-model-management-sdk==1.0.1b6.post1'
    with open(generated_requirements, 'w') as generated_requirements_file:
        generated_requirements_file.write(sdk_requirements_string)

    return generated_requirements


def upload_dependency(workspace, dependency, create_tar=False):
    """
    :param workspace:
    :type workspace: workspace: azureml.core.workspace.Workspace
    :param dependency: path (local, http[s], or wasb[s]) to dependency
    :type dependency: str
    :param create_tar:
    :type create_tar: bool
    :return: (str, str): uploaded_location, dependency_name
    """
    artifact_client = ArtifactsClient.create(workspace)
    if dependency.startswith('http') or dependency.startswith('wasb'):
        return dependency, urlparse(dependency).path.split('/')[-1]
    if not os.path.exists(dependency):
        raise WebserviceException('Error resolving dependency: '
                                  'no such file or directory {}'.format(dependency))

    dependency = dependency.rstrip(os.sep)
    dependency_name = os.path.basename(dependency)
    dependency_path = dependency

    if create_tar:
        dependency_name = str(uuid.uuid4())[:8] + '.tar.gz'
        tmpdir = tempfile.mkdtemp()
        dependency_path = os.path.join(tmpdir, dependency_name)
        dependency_tar = tarfile.open(dependency_path, 'w:gz')
        dependency_tar.add(dependency)
        dependency_tar.close()

    origin = 'LocalUpload'
    container = '{}'.format(str(uuid.uuid4())[:8])
    result = artifact_client.upload_artifact_from_path(dependency_path, origin, container, dependency_name)
    artifact_content = result.artifacts[dependency_name]
    dependency_name = artifact_content.path
    uploaded_location = "aml://artifact/" + artifact_content.artifact_id
    return uploaded_location, dependency_name


def wrap_execution_script(execution_script, schema_file, dependencies, log_aml_debug):
    """
    Wrap the user's execution script in our own in order to provide schema validation.
    :param execution_script: str path to execution script
    :param schema_file: str path to schema file
    :param dependencies: list of str paths to dependencies
    :return: str path to wrapped execution script
    """
    new_script_loc = tempfile.mkstemp(suffix='.py')[1]
    dependencies.append(execution_script)
    if not os.path.exists(execution_script):
        raise WebserviceException('Path to execution script {} does not exist.'.format(execution_script))
    if not schema_file:
        schema_file = ''
    else:
        # Fix path references in schema file,
        # since the container it will run in is a Linux container
        path_components = schema_file.split(os.sep)
        schema_file = "/".join(path_components)
    return generate_main(execution_script, schema_file, new_script_loc, log_aml_debug)


def generate_main(user_file, schema_file, main_file_name, log_aml_debug):
    """

    :param user_file: str path to user file with init() and run()
    :param schema_file: str path to user schema file
    :param main_file_name: str full path of file to create
    :return: str filepath to generated file
    """

    data_directory = os.path.join(os.path.dirname(__file__), 'data')
    main_template_path = os.path.join(data_directory, 'main_template.txt')

    with open(main_template_path) as template_file:
        main_src = template_file.read()

    main_src = main_src.replace('<user_script>', user_file)\
        .replace('<schema_file>', schema_file)\
        .replace('<log_debug_statements>', str(log_aml_debug))
    with open(main_file_name, 'w') as main_file:
        main_file.write(main_src)
    return main_file_name


def _validate_schema_version(schema_file):
    with open(schema_file, 'r') as outfile:
        schema_json = json.load(outfile)

    if "input" in schema_json:
        for key in schema_json["input"]:
            _check_inout_item_schema_version(schema_json["input"][key])
            break
    elif "output" in schema_json:
        for key in schema_json["input"]:
            _check_inout_item_schema_version(schema_json["output"][key])
            break


def _check_inout_item_schema_version(item_schema):
    _pup_version = "0.1.0a11"
    _schema_version_error_format = "The given schema cannot be loaded because it was generated on a SDK version - " \
                                   "{} that is not compatible with the one used to create the ML service - {}. " \
                                   "Please either update the SDK to the version for which the schema was generated, " \
                                   "or regenerate the schema file with the currently installed version of the SDK.\n" \
                                   "You can install the latest SDK with:\n" \
                                   "\t pip install azureml-model-management-sdk --upgrade\n " \
                                   "or upgrade to an earlier version with:\n" \
                                   "\t pip install azureml-model-management-sdk=<version>"
    if "version" not in item_schema:
        schema_version = _pup_version
    else:
        schema_version = item_schema["version"]

    # Check here if the schema version matches the current running SDK version (major version match)
    # and error out if not, since we do not support cross major version backwards compatibility.
    # Exception is given if schema is assumed to be _pup_version since the move from that to 1.0 was
    # not considered a major version release, and we should not fail for all PUP customers.
    sdk_version = '1.0.1b6'
    current_major = int(sdk_version.split('.')[0])
    deserialized_schema_major = int(schema_version.split('.')[0])
    if schema_version != _pup_version and current_major != deserialized_schema_major:
        error_msg = _schema_version_error_format.format(schema_version, sdk_version)
        raise ValueError(error_msg)

    return schema_version


def get_paginated_results(payload, headers):
    if 'value' not in payload:
        raise WebserviceException('Error, invalid paginated response payload, missing "value":\n'
                                  '{}'.format(payload))
    items = payload['value']
    while 'nextLink' in payload:
        next_link = payload['nextLink']

        try:
            resp = requests.get(next_link, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
        except requests.Timeout:
            raise WebserviceException('Error, request to Model Management Service timed out to URL:\n'
                                      '{}'.format(next_link))
        if resp.status_code == 200:
            content = resp.content
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            payload = json.loads(content)
        else:
            raise WebserviceException('Received bad response from Model Management Service while retrieving paginated'
                                      'results:\n'
                                      'Response Code: {}\n'
                                      'Headers: {}\n'
                                      'Content: {}'.format(resp.status_code, resp.headers, resp.content))
        if 'value' not in payload:
            raise WebserviceException('Error, invalid paginated response payload, missing "value":\n'
                                      '{}'.format(payload))
        items += payload['value']

    return items


def _get_mms_url(workspace):
    from azureml._restclient.assets_client import AssetsClient
    assets_client = AssetsClient.create(workspace)
    mms_url = assets_client.get_cluster_url()
    uri = '/api/subscriptions/{}/resourceGroups/{}/providers/' \
          'Microsoft.MachineLearningServices/workspaces/{}'.format(workspace.subscription_id,
                                                                   workspace.resource_group,
                                                                   workspace.name)
    return mms_url + uri


def get_docker_client(username, password, image_location):
    """
    Retrieves the docker client for performing docker operations
    :return:
    :rtype: docker.DockerClient
    """
    try:
        client = docker.from_env(version='auto')
    except docker.errors.DockerException as exc:
        raise WebserviceException('Failed to create Docker client: {}'.format(exc))
    try:
        client.version()
    except Exception:
        raise WebserviceException('Unable to communicate with Docker daemon. Is Docker running/installed?\n'
                                  '\n\nDocker Client {}'.format(traceback.format_exc()))
    try:
        client.login(username=username, password=password, registry=image_location)
    except Exception:
        raise WebserviceException('Unable to login to docker. {}'. format(traceback.format_exc()))
    return client


def pull_docker_image(docker_client, image_location, username, password):
    """
    Pulls the docker image from the ACR
    :param docker_client:
    :type docker_client: docker.DockerClient
    :param image_location:
    :type image_location: str
    :param username:
    :type username: str
    :param password:
    :type password: str
    :return:
    :rtype: None
    """
    try:
        print('Pulling image from ACR (this may take a few minutes depending on image size)...\n')
        for outer_line in docker_client.api.pull(image_location, stream=True, auth_config={
            'username': username,
            'password': password
        }):
            sys.stdout.write(outer_line.decode("utf-8"))
    except docker.errors.APIError as e:
        raise WebserviceException('Error: docker image pull has failed:\n{}'.format(e))
    except Exception as exc:
        raise WebserviceException('Error with docker pull {}'.format(exc))


def start_docker_container(docker_client, image_location, container_name):
    """
    Starts the docker container given the image location and container name
    :param docker_client:
    :type docker_client: docker.DockerClient
    :param image_location:
    :type image_location: str
    :param container_name:
    :type container_name: str
    :return:
    :rtype: docker.Container
    """
    try:
        print("Starting Docker container...")
        container_labels = {'containerName': container_name}
        return docker_client.containers.run(image_location, detach=True, publish_all_ports=True,
                                            labels=container_labels)
    except docker.errors.APIError as exc:
        raise WebserviceException('Docker container run has failed: \n{}'.format(exc))


def get_docker_port(docker_client, container_name, container):
    """
    Starts the docker container given the image location and container name and returns the docker port
    :param docker_client:
    :type docker_client: docker.DockerClient
    :param container_name:
    :type container_name: str
    :param container:
    :type container: docker.Container
    :return:
    :rtype: str
    """
    try:
        containers = docker_client.containers.list(filters={'label': 'containerName={}'.format(container_name)})
    except docker.errors.DockerException as exc:
        print('\nContainer Logs:')
        print(container.logs().decode())
        cleanup_container(container)
        raise WebserviceException('Failed to get Docker container for scoring: \n{}'.format(exc))

    if len(containers) == 1:
        container = containers[0]
        port_info_dict = container.attrs['NetworkSettings']['Ports']
        for key in port_info_dict:
            if '5001' in key and len(port_info_dict[key]) == 1:
                port = port_info_dict[key][0]['HostPort']
                return port

        print('\nContainer Logs:')
        print(container.logs().decode())
        cleanup_container(container)
        raise WebserviceException('Error: Container port (5001) is unreachable.')
    else:
        print('\nContainer Logs:')
        print(container.logs().decode())
        cleanup_container(container)
        raise WebserviceException('Error: Multiple containers with container name {}'.format(container_name))


def container_health_check(docker_port, container):
    """
    Sends a post request to check the health of the new container
    :param docker_client:
    :type docker_client: docker.DockerClient
    :param container:
    :type container: docker.Container
    :return:
    :rtype: str
    """
    print("Checking container health...")
    health_url = 'http://127.0.0.1:{}/'.format(docker_port)

    health_check_iteration = 0
    while health_check_iteration < MAX_HEALTH_CHECK_TRIES:
        try:
            result = requests.get(health_url, verify=False)
        except requests.ConnectionError:
            time.sleep(HEALTH_CHECK_INTERVAL_SECONDS)
            health_check_iteration += 1
            if health_check_iteration >= MAX_HEALTH_CHECK_TRIES and 'http://127.0.0.1' == health_url[:16]:
                print("Container health check failed on localhost. Checking container health using container IP...")
                process = subprocess.Popen(['docker', 'inspect', '--format', "\'{{ .NetworkSettings.IPAddress }}\'",
                                            container.id], stdout=subprocess.PIPE)
                stdout = process.communicate()[0]
                container_ip = stdout.decode().rstrip().replace("'", "")
                if not container_ip:
                    print('\nContainer Logs:')
                    print(container.logs().decode())
                    raise WebserviceException('Error: Connection to container has failed. Did your init method fail?')
                health_url = 'http://{}:5001/'.format(container_ip)
                health_check_iteration = 0
            continue
        except requests.Timeout:
            time.sleep(HEALTH_CHECK_INTERVAL_SECONDS)
            health_check_iteration += 1
            continue

        if result.status_code == 200:
            return health_url
        elif result.status_code == 502:
            time.sleep(HEALTH_CHECK_INTERVAL_SECONDS)
            health_check_iteration += 1
            continue
        else:
            if 'http://127.0.0.1' == health_url[:16]:
                print("Container health check failed on localhost. Checking container health using container IP...")
                process = subprocess.Popen(['docker', 'inspect', '--format', "\'{{ .NetworkSettings.IPAddress }}\'",
                                            container.id], stdout=subprocess.PIPE)
                stdout = process.communicate()[0]
                container_ip = stdout.decode().rstrip().replace("'", "")
                if not container_ip:
                    print('\nContainer Logs:')
                    print(container.logs().decode())
                    raise WebserviceException('Error: Connection to container has failed. Did your init method fail?')
                health_url = 'http://{}:5001/'.format(container_ip)
                health_check_iteration = 0
                continue
            else:
                print('\nContainer Logs:')
                print(container.logs().decode())
                cleanup_container(container)
                raise WebserviceException('Error: Connection to container has failed. Did your init method fail?')
    if health_check_iteration >= MAX_HEALTH_CHECK_TRIES:
        print('\nContainer Logs:')
        print(container.logs().decode())
        cleanup_container(container)
        raise WebserviceException('Error: Connection to container has failed. Did your init method fail?')


def container_scoring_call(docker_port, input_data, container, health_url):
    """
    Sends a scoring call to the given container with the given input data
    :param docker_client:
    :type docker_client: docker.DockerClient
    :param input_data:
    :type input_data: str
    :param container:
    :type container: docker.Container
    :return:
    :rtype: str
    """
    print("Making a scoring call...")
    scoring_url = '{}score'.format(health_url)
    headers = {'Content-Type': 'application/json'}
    try:
        result = requests.post(scoring_url, headers=headers, data=input_data, verify=False)
    except requests.exceptions.HTTPError:
        print('\nContainer Logs:')
        print(container.logs().decode())
        cleanup_container(container)
        raise WebserviceException('Error: Connection with container for scoring has failed.')

    if result.status_code == 200:
        result_object = result.json()
        print('Scoring result:')
        print(result_object)
        return result_object
    else:
        content = result.content.decode('utf-8')
        if content == "ehostunreach":
            print('\nContainer Logs:')
            print(container.logs().decode())
            cleanup_container(container)
            raise WebserviceException('Error: Scoring was unsuccessful. Unable to reach the requested host.')
        print("Scoring response content:\n", content)
        cleanup_container(container)
        raise WebserviceException('Error: Scoring was unsuccessful.')


def cleanup_container(container):
    """
    Tries to kill and remove the container
    :param container:
    :type container: docker.Container
    :return:
    :rtype: None
    """
    try:
        container.kill()
    except Exception as exc:
        print('Container (name:{}, id:{}) cannot be killed.'.format(container.name, container.id))
    try:
        container.remove()
        print('Resources have been successfully cleaned up.')
    except Exception as exc:
        print('Container (name:{}, id:{}) cannot be removed.'.format(container.name, container.id))


def validate_path_exists_or_throw(member, name):
    if not os.path.exists(member):
        raise WebserviceException("{0} {1} doesn't exist".format(name, member))
