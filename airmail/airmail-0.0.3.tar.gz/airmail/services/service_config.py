from functools import reduce
from airmail.utils.files import read_yml,determine_project_path
from airmail.utils.config import build_config


class ServiceConfig():
    def __init__(self, get_prop, get_top_level_prop, get_with_prefix):
        # Getters passed in to read from the config file
        # TODO: cleanup later? Pass in a different away?
        self.get_prop = get_prop
        self.get_top_level_prop = get_top_level_prop
        self.get_with_prefix = get_with_prefix

        # The list of functions to reduce through
        self.transforms = [
            self.assign_load_balancer,
            self.assign_service_info,
            self.assign_deployment_configuration
        ]

    #
    def build(self, file):
        # The config that will be sent to AWS client
        config = read_yml(determine_project_path() + '/../data/' + file + '.yml')
        # Run throught the config builder reduce
        return build_config(self.transforms, config)

    # Adds the desired count to the config
    def assign_service_info(self, config):
        # update_service uses `service` and create_service uses `serviceName`
        service_prop = 'service' if 'service' in config else 'serviceName'

        config['cluster'] = self.get_top_level_prop('cluster')
        config['taskDefinition'] = self.get_top_level_prop('family')
        config['desiredCount'] = self.get_prop('deployment.desiredCount')
        config[service_prop] = self.get_top_level_prop('service')
        return config

    def assign_deployment_configuration(self, config):
        config['deploymentConfiguration']['maximumPercent'] = self.get_prop('deployment.maxHealthyPercent', 200)
        config['deploymentConfiguration']['minimumHealthyPercent'] = self.get_prop('deployment.minHealthyPercent', 80)
        return config

    # Adds load balancer information to the config
    def assign_load_balancer(self, config):
        # Add if there is a `loadBalancers` prop in the dictionary
        if 'loadBalancers' in config:
            config['loadBalancers'][0]['targetGroupArn'] = self.get_prop('loadBalancer.targetGroupArn')
            config['loadBalancers'][0]['containerName'] = self.get_top_level_prop('name')
            config['loadBalancers'][0]['containerPort'] = self.get_prop('deployment.port')
        return config

    # TODO: Add some retriever/setter/validation functions
