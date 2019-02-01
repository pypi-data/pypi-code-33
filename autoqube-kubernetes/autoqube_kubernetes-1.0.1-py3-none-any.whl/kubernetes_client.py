from kubernetes import config, client
from kubernetes.client import configuration
from kubernetes.stream import stream
import yaml
import os
import shlex
import subprocess
import logging

APIClientsDict = {
    "extensions/v1beta1": "ExtensionsV1beta1Api",
    "apps/v1beta2": "AppsV1beta2Api",
    "v1": "CoreV1Api"
}

ObjectsKindDict = {
    "Deployment": "deployment",
    "ConfigMap": "config_map",
    "Service": "service"
}


class KubernetesClient:

    def __init__(self, config_file):
        self._logger = logging.getLogger(self.__class__.__name__)
        config.load_kube_config(config_file)
        configuration.assert_hostname = False
        self._client_list = {}
        self._set_env_config(config_file)

    def _set_env_config(self, config_file):
        os_env = os.environ.copy()
        os_env.update({
            'KUBECONFIG': config_file
        })
        self._env = os_env

    def set_config_file(self, config_file):
        """
        Sets up the environment variable `KUBECONFIG` pointed to kubeconfig file
        """
        config.load_kube_config(config_file)
        self._set_env_config(config_file)

    def _get_client(self, api_version):
        """
        Get Kubernetes client object for a given api_version
        """
        client_name = APIClientsDict.get(api_version, None)
        if client_name in self._client_list:
            return self._client_list.get(client_name)
        else:
            api_client = getattr(client, client_name)()
            self._client_list[client_name] = api_client
            return api_client

    def _create_object(self, kind, api_client, yaml_obj, namespace):
        object_kind_name = ObjectsKindDict.get(kind)
        object_kind_name = "create_namespaced_{0}".format(object_kind_name)
        object_kind_method = getattr(api_client, object_kind_name)
        return object_kind_method(body=yaml_obj, namespace=namespace)

    def create_object(self, yaml_file, namespace=None):
        """
        Create a Kubernetes object from yaml file
        """
        if namespace is None:
            namespace = 'default'
        yaml_file_obj = open(yaml_file)
        yaml_obj = yaml.load(yaml_file_obj)
        api_version = yaml_obj.get('apiVersion')
        object_kind = yaml_obj.get('kind')
        api_client = self._get_client(api_version)
        return self._create_object(object_kind, api_client, yaml_obj, namespace)

    def destroy_all_resources(self, namespace=None):
        if namespace is None:
            namespace = 'default'
        delete_command = "kubectl delete configmaps,daemonsets,replicasets,services,deployments,pods,rc --all " \
                         "--namespace={0}".format(namespace)
        process = subprocess.Popen(shlex.split(delete_command), stdout=subprocess.PIPE, env=self._env)
        stdout = process.communicate()[0]
        self._logger.debug(stdout)

    def create_object_from_yaml_data(self, yaml_data, namespace=None):
        if namespace is None:
            namespace = 'default'
        api_version = yaml_data.get('apiVersion')
        object_kind = yaml_data.get('kind')
        api_client = self._get_client(api_version)
        return self._create_object(object_kind, api_client, yaml_data, namespace)

    def execute_commands(self, pod_name, commands_list, namespace=None, exec_command=None):
        """
        Executes list of specific commands on a given pod
        """
        if namespace is None:
            namespace = 'default'
        if not len(commands_list) < 1:
            api_client = self._get_client("v1")
            if exec_command is None:
                exec_command = ['/bin/sh']
            resp = stream(api_client.connect_get_namespaced_pod_exec, pod_name, namespace,
                          command=exec_command,
                          stderr=True, stdin=True,
                          stdout=True, tty=False,
                          _preload_content=False)
            while resp.is_open():
                resp.update(timeout=1)
                if commands_list:
                    c = commands_list.pop(0)
                    self._logger.debug("Running command... %s\n" % c)
                    resp.write_stdin(c + "\n")
                    line = resp.readline_stdout(timeout=3)
                    while line is not None:
                        self._logger.debug(line)
                        line = resp.readline_stdout(timeout=3)
                else:
                    break
            resp.close()

    def copy_file_to_pod(self, pod_name, source_file, destination_path, namespace=None):
        """
        Copies different files to a given pod. It uses `kubectl cp` as the implementation in python is not possible
        """
        if namespace is None:
            namespace = 'default'
        copy_command = "kubectl cp {0} {1}/{2}:{3}".format(source_file, namespace, pod_name, destination_path)
        process = subprocess.Popen(shlex.split(copy_command), stdout=subprocess.PIPE, env=self._env)
        stdout = process.communicate()[0]
        self._logger.debug(stdout)

    def get_pod_list(self, namespace=None):
        """
        Lists all the pods in the given namespace
        """
        if namespace is None:
            namespace = 'default'
        v1_client = self._get_client("v1")
        return v1_client.list_namespaced_pod(namespace)

    def get_service_list(self, namespace=None):
        """
        Lists all the services in the given namespace
        """
        if namespace is None:
            namespace = 'default'
        v1_client =self._get_client("v1")
        return v1_client.list_namespaced_service(namespace)

    def check_all_pods_status(self, namespace=None):
        """
        Checks for the running status of all pods in a given namespace
        """
        pod_list = self.get_pod_list(namespace=namespace)
        for pod in pod_list.items:
            if not (pod.status.phase == 'Running'):
                return False
        return True
