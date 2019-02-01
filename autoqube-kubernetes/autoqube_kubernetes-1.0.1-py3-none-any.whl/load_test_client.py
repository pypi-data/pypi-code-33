from autoqube_kubernetes.tech_stack_handler import TechStackHandler
import time
import os
import logging

TEST_FILE_EXTENSIONS = ["jmx"]
DEFAULT_TIMEOUT = 10


class LoadTestClient:
    """
    This class handles complete setup of different types of stacks required for Load testing on already
    available Kubernetes cluster, running the load tests and destroying the objects set up after tests
    """
    def __init__(self, config, kubernetes_client=None):
        self._logger = logging.getLogger(self.__class__.__name__)
        if kubernetes_client is not None:
            self._kubernetes_client = kubernetes_client
        self._tech_stack_handler = TechStackHandler()
        self._test_type = config.get('test_type', None)
        self._templates_path = config.get('templates_path', './')
        self._test_template = None
        if self._test_type is not None:
            self._test_template = self._tech_stack_handler.get_stack(self._test_type)

    def get_supported_load_tests(self):
        """
        Gives a list of load tests which are supported. Currently only 'jmeter' is supported
        :return:
        """
        return self._tech_stack_handler.get_stack_list()

    def set_test(self, test_type):
        self._test_type = test_type

    def create_kubernetes_objects(self):
        """
        Creates all the objects required for a particular load testing on Kubernetes cluster
        """
        if self._test_template is None:
            if self._test_type is not None:
                self._test_template = self._tech_stack_handler.get_stack(self._test_type)
            else:
                raise Exception
        workload_templates = self._test_template['workload_templates']
        deployment_order = self._test_template['deployment_order']
        deployment_keys = sorted(deployment_order.keys())
        for key in deployment_keys:
            service = deployment_order[key]['service']
            timeout = deployment_order[key]['timeout']
            for workload, workload_value in workload_templates[service].items():
                yaml_file = "{0}{1}".format(self._templates_path, workload_value['yaml'])
                res = self._kubernetes_client.create_object(yaml_file)
                msg = "%s %s created" % (service, workload)
                self._logger.debug(msg)
            if timeout != 0:
                time.sleep(timeout)
        self._logger.debug("Completed Creating Objects")
        while not self._kubernetes_client.check_all_pods_status():
            self._logger.debug("Waiting for all the pods to come to 'Running' status")
            time.sleep(DEFAULT_TIMEOUT)
            self._logger.debug("All the pods are up and running")
        commands = self._test_template.get('commands', None)
        if commands is not None:
            self._execute_commands(commands)

    def destroy_kubernetes_objects(self):
        self._kubernetes_client.destroy_all_resources()
        while len(self._kubernetes_client.get_pod_list().items) != 0:
            self._logger.debug("Waiting for resources to be deleted")
            time.sleep(DEFAULT_TIMEOUT)

    def _execute_commands(self, commands_template, template_variables=None):
        """
        Executes commands on the kubernetes pods set up for load testing
        """
        if template_variables is not None:
            commands = {}
            for service_name in commands_template.keys():
                commands[service_name] = {"commands": []}
                for command_template in commands_template[service_name]['commands']:
                    for key, value in template_variables.items():
                        command_template = command_template.replace(key, value)
                    commands[service_name]['commands'].append(command_template)
        else:
            commands = commands_template
        pod_list = self._kubernetes_client.get_pod_list()
        pods_commands_keys = commands.keys()
        for pod in pod_list.items:
            for pod_key in pods_commands_keys:
                if pod_key in pod.metadata.name:
                    commands[pod_key]['name'] = pod.metadata.name
        for pod_key in pods_commands_keys:
            command_obj = commands[pod_key]
            self._logger.debug(command_obj['commands'])
            self._kubernetes_client.execute_commands(command_obj['name'], command_obj['commands'])

    def execute_tests(self, config):
        """
        Copies the test files to test execution pod and runs the load tests
        """
        test_files = self._test_template['test_files']
        input_files = config['test_files']
        template_variables = dict()
        for file in input_files:
            exists = os.path.isfile(file)
            if not exists:
                pass
            file_extension = file.split(".")[-1]
            if file_extension in TEST_FILE_EXTENSIONS:
                template_variables['{test_file}'] = file.split("/")[-1]
        pod_list = self._kubernetes_client.get_pod_list()
        for service in test_files.keys():
            destination_file_path = test_files[service]['destination_location']
            source_files = config['test_files']
            for pod in pod_list.items:
                if service in pod.metadata.name:
                    pod_name = pod.metadata.name
                    for source_file in source_files:
                        self._kubernetes_client.copy_file_to_pod(pod_name, source_file, destination_file_path)
        self._execute_commands(self._test_template['test_commands'], template_variables)
        if 'list_services' in self._test_template:
            service_list = self._kubernetes_client.get_service_list().items
            for service, value in self._test_template['list_services'].items():
                for svc in service_list:
                    if service in svc.metadata.name:
                        self._logger.info({
                            "spec": svc.spec,
                            "status": svc.status,
                            "message": value['message']
                        })

    def destroy_objects(self):
        pass
