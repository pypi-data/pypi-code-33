from functools import reduce
from pydash import set_
from dotenv import dotenv_values
from airmail.utils.files import read_yml,determine_project_path
from airmail.utils.config import build_config

class TaskConfig():
    def __init__(self, get_prop, get_top_level_prop, get_with_prefix):
        # Getters passed in to read from the config file
        # TODO: cleanup later? Pass in a different away
        self.get_prop = get_prop
        self.get_top_level_prop = get_top_level_prop
        self.get_with_prefix = get_with_prefix

        # The list of functions to reduce through
        self.transforms = [
            self.assign_task_info,
            self.assignTaskRoles,
            self.assign_logging,
            self.assign_env_vars
        ]

    def build(self, version, env):
        # The config that will be sent to AWS client
        config = read_yml(determine_project_path() + '/../data/task.yml')
        # Assign the image version to use
        self.image_version = version
        # Assign the environment we're running in
        self.env = env
        # Run throught the config builder reduce
        return build_config(self.transforms, config)

    def assignTaskRoles(self, config):
        account_id = self.get_top_level_prop('accountID')
        config['taskRoleArn'] = 'arn:aws:iam::' + account_id + ':role/' + self.get_prop('taskRole')
        config['executionRoleArn'] = 'arn:aws:iam::' + account_id + ':role/' + self.get_prop('executionRole')
        return config

    def set_into_container_definition(self, config, prop, value):
        path = 'containerDefinitions[0].' + prop
        return set_(config, path, value)

    # Adds the desired count to the config
    def assign_task_info(self, config):
        config['family'] = self.get_top_level_prop('family')

        self.set_into_container_definition(config, 'name', self.get_top_level_prop('name'))
        self.set_into_container_definition(config, 'image', self.get_top_level_prop('imageID') + ':' + self.image_version)
        self.set_into_container_definition(config, 'command', self.get_prop('deployment.command'))
        self.set_into_container_definition(config, 'cpu', self.get_prop('deployment.cpu'))
        self.set_into_container_definition(config, 'memory', self.get_prop('deployment.memory'))
        self.set_into_container_definition(config, 'portMappings[0].containerPort', self.get_prop('deployment.port'))
        return config

    def assign_logging(self, config):
        """ Assign the logging configuration options to the task definition """
        self.set_into_container_definition(config, 'logConfiguration.logDriver', self.get_prop('logging.logDriver'))
        self.set_into_container_definition(config, 'logConfiguration.options', self.get_prop('logging.options'))
        return config

    def assign_env_vars(self, config):
        """ Read from the environment env file and turn the values into environment variables for the task definition """
        env_vars = []
        env_dict=dotenv_values(dotenv_path='./.deploy/' + self.env + '.env')

        for name, value in env_dict.items():
            env_vars.append({
                'name': name,
                'value': value
            })

        self.set_into_container_definition(config, 'environment', env_vars)
        return config
