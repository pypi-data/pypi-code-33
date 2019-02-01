from autoqube_kubernetes.kubernetes_client import KubernetesClient
from autoqube_kubernetes.aws_kube_cluster_client import AWSKubeClusterClient
from autoqube_kubernetes.load_test_client import LoadTestClient
import time
import logging

UPDATE_TIMEOUT = 200

class KubernetesHandler:
    """
    This class handles complete responsibility of creating, deleting Kubernetes cluster on various cloud platforms.
    Deployment of different stacks on kubernetes cluster.
    """
    def __init__(self, config):
        self._logger = logging.getLogger(self.__class__.__name__)
        if 'cluster_config' not in config.keys():
            self._logger.error("Required cluster credentials are missing. Please add 'cluster_config' in configuration")
            exit()
        self.cluster_config = config['cluster_config']
        self.kube_cluster_client = self._get_kube_cluster_client(config)
        self.kubernetes_client = None
        self.load_test_client = None
        self._cluster_up = self._is_cluster_up()

    def _get_kube_cluster_client(self, config):
        """
        Provides appropriate cloud platform client for Kubernetes cluster creation based on config
        """
        if config['cloud_provider'] == 'AWS':
            if 'env_config' not in config.keys():
                self._logger.error("Required AWS Credentials are missing. Please add 'env_config' in configuration")
                exit()
            return AWSKubeClusterClient(config['env_config'])
        else:
            self._logger.error( config['cloud_provider'] + " platform is neither non-existent or not supported")
            exit()
        """
        elif config['cloud_provider'] == 'GCP':
            return GCPKubeClusterClient(config['env_config'])
        """

    def _is_cluster_up(self):
        """
        Checks the status of Kubernetes cluster based on the config
        """
        return self.kube_cluster_client.is_cluster_up()

    def _set_kubernetes_client(self, kubeconfig):
        """
        Sets up kubernetes client based on the provided kubeconfig
        """
        self.kubernetes_client = KubernetesClient(kubeconfig)

    def create_cluster(self):
        """
        Creates a new Kubernetes cluster and sets up kubernetes client with the kubeconfig
        """
        if not self._cluster_up:
            self.kube_cluster_client.create_cluster(self.cluster_config)
            self._logger.debug("Cluster created")
            self.kube_cluster_client.update_cluster(self.cluster_config['name'])
            time.sleep(UPDATE_TIMEOUT)
            self._logger.debug("Updated cluster")
            self._cluster_up = True
            kubeconfig = self.kube_cluster_client.get_kube_config()
            self._set_kubernetes_client(kubeconfig)
        else:
            self._logger.warning(self.cluster_config['name'] + " cluster is already running")

    def delete_cluster(self):
        """
        Deletes the Kubernetes cluster if already present
        """
        if self._cluster_up:
            self.kube_cluster_client.delete_cluster(self.cluster_config['name'])
        else:
            self._logger.warning("No cluster is running")

    def _set_load_test_client(self, load_config):
        if self.kubernetes_client is None:
            kubeconfig = self.kube_cluster_client.get_kube_config()
            self._set_kubernetes_client(kubeconfig)
        self.load_test_client = LoadTestClient(load_config, self.kubernetes_client)

    def create_load_test(self, load_config):
        """
        Creates the resources required for running load test on already available Kubernetes cluster based on config
        """
        self._set_load_test_client(load_config)
        self._logger.debug("Loaded Test Client")
        self.load_test_client.create_kubernetes_objects()
        self._logger.debug("Created Kubernetes objects")

    def destroy_load_test(self, load_config):
        """
        Deletes all the resources setup for running load test
        """
        self._set_load_test_client(load_config)
        self._logger.debug("Loaded Test Client")
        self.load_test_client.destroy_kubernetes_objects()
        self._logger.debug("Deleted Kubernetes objects")

    def run_load_test(self, config):
        """
        Executes Load tests on the Kubernetes cluster setup with load test resources
        """
        self.load_test_client.execute_tests(config)
        self._logger.debug("Executed Test commands")
