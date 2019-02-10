import os, subprocess
import boto3
import click
from botocore.exceptions import ClientError
from .utils import err_log
from .service_config import ServiceConfig
from .deploy_file import DeployFile
from .task_config import TaskConfig
from airmail.utils.bash import run_script
from airmail.utils.files import read_package_json_version

class ECSService(DeployFile):
    def __init__(self, env=None, profile=None):
        # ECS client
        if profile is None:
            self.client = boto3.client('ecs')
        else:
            self.session = boto3.session.Session(profile_name=profile)
            self.client = self.session.client('ecs')
        # The env
        self.env = env
        self.profile = profile

        # Init the Deploy File class
        DeployFile.__init__(self, self.env)

        self.ServiceConfigBuilder = ServiceConfig(self.get_prop, self.get_top_level_prop, self.get_with_prefix)
        self.TaskConfigBuilder = TaskConfig(self.get_prop, self.get_top_level_prop, self.get_with_prefix)

    def get_env(self):
        """Return the env passed in"""
        return self.env

    # Check if a service exists
    def service_exists(self):
        """Given the config.yml file, check if the service exists in the target cluster"""

        cluster = self.get_top_level_prop('cluster')
        service_name = self.get_top_level_prop('service')

        try:
            # Make the request
            response = self.client.describe_services(
                cluster=cluster,
                services=[ service_name ]
            )

            # Grab the failures
            failures = response['failures']

            if len(failures) >= 1:
                return False
            else:
                return True

        except ClientError as e:
            if e.response['Error']['Code'] == 'ClusterNotFoundException':
                # If hitting this, the cluster does not exist
                err_log('Cluster not found!')
            else:
                click.echo('Unexpected error: ' + e)

    def create_service(self):
        """Create a service using the config.yml and default config (data/service.yml)"""
        # Build the config object
        config = self.ServiceConfigBuilder.build('service')
        response = self.client.create_service(**config)
        self.log_status(
            boto_response = response,
            success_msg='Service created!',
            err_msg='Service creation failed!'
        )

    def update_service(self):
        config = self.ServiceConfigBuilder.build('service_update')
        response = self.client.update_service(**config)
        self.log_status(
            boto_response = response,
            success_msg='Updated service!',
            err_msg='Service update failed!'
        )

    def create_task_definition(self):
        """Return the JSON for a task definition"""

        image_version = self.find_image_version()
        return self.TaskConfigBuilder.build(image_version, self.env)

    def build_container_image(self):
        """Build Container Image

        Executes a bash script to build an image with the
        Docker CLI and push that image to ECT
        """

        ecr_repo  = self.get_with_prefix('name', '/')
        version   = self.find_image_version()
        image_tag = self.get_top_level_prop('imageID') + ':' + version
        app_dir   = self.get_top_level_prop('projectDirectory')
        env_dict  = {
            'VERSION': version,
            'ECR_REPO': ecr_repo,
            'TASK_IMAGE_TAG': image_tag,
            'APP_DIR': app_dir
        }

        if not self.profile is None:
            env_dict['AWS_PROFILE'] = self.profile

        val = run_script('ecr_push', env_dict) # Returns the exit code from bash

        if (val == 0): # If a good run, return the tag
            return image_tag
        else: # TODO: Handle error
            print('The image build went poorly')

    def find_image_version(self):
        """Grabs the version of the image to build from the config file
        or pulls from the package.json file in the project directory
        """

        package_version = read_package_json_version(self.get_top_level_prop('projectDirectory'))
        config_version = self.get_prop('deployment.version')

        if config_version is not None:
            return config_version
        else:
            return package_version

    def register_task_definition(self, task):
        """Given task definition JSON, make the container and create a task definition"""

        response = self.client.register_task_definition(**task)
        self.log_status(
            boto_response = response,
            success_msg='Registered new task definition!',
            err_msg='Task definition registration failed!'
        )

    def log_status(self, boto_response, success_msg = "", err_msg = ""):
        if boto_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            click.echo(click.style('Info: ', fg='green', bold=True) + success_msg)
        else:
            click.echo(click.style('Error: ', fg='red', bold=True) + err_msg)
