from autoqube_kubernetes.kube_cluster_client import KubeClusterClient
import os
import shlex
import subprocess
import yaml
import logging


class AWSKubeClusterClient(KubeClusterClient):

    def __init__(self, env_config):
        """
        Check config and set the defaults if not provided.
        If any required parameters are missing the throw an error
        :param env_config:
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        KubeClusterClient.__init__(self, config=env_config)
        self._cloud = 'aws'
        self._env = self._get_env_config(env_config)

    def _get_env_config(self, config):
        env = dict()
        required_env_keys = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
                             'AWS_REGION', 'KUBECONFIG', 'KOPS_STATE_STORE']
        for key in required_env_keys:
            val = config.get(key, None)
            if val is None:
                self._logger.error("Required Key Missing : {0}".format(key))
                exit()
            env[key] = val

        os_env = os.environ.copy()
        os_env.update(env)
        return os_env

    def _get_cluster_config(self, config):
        conf = dict()
        conf['name'] = config.get('name', 'DefaultName')
        conf['node_count'] = config.get('node-count', 2)
        conf['master_size'] = config.get('master-size', 't2.small')

        master_zones = config.get('master-zones', None)
        if master_zones is None:
            self._logger.error("Required Config missing : master-zones")
        conf['master_zones'] = master_zones

        zones = config.get('zones', None)
        if zones is None:
            self._logger.error("Required Config missing : zones")
        conf['zones'] = zones

        conf['node_size'] = config.get('node-size', 't2.small')

        ssh_key = config.get('ssh-public-key')
        if ssh_key is None:
            self._logger.error("Required Config missing : ssh-public-key")
        conf['ssh_key'] = ssh_key

        dns_zone = config.get('dns-zone')
        if dns_zone is None:
            self._logger.error("Required Config missing : dns-zone")
        conf['dns_zone'] = dns_zone

        return conf

    def get_kube_config(self):
        return self._env['KUBECONFIG']

    def get_running_clusters(self):
        lines = list()
        cluster_list = list()
        cluster_command = "kops get cluster"
        process = subprocess.Popen(shlex.split(cluster_command), stdout=subprocess.PIPE, env=self._env)
        stdout = process.communicate()[0]
        line = ''
        for char in stdout.decode():
            if char == '\t':
                line = line + ' '
                continue
            if char == '\n':
                lines.append(line)
                line = ''
                continue
            line = line + char
        for line in lines[1:]:
            line_array = line.split(" ")
            cluster_list.append(line_array[0].strip())
        return cluster_list

    def is_cluster_up(self):
        kubeconfig = self.get_kube_config()
        cluster_list = self.get_running_clusters()
        if os.path.isfile(kubeconfig):
            kubeconfig_obj = yaml.load(open(kubeconfig))
            if len(kubeconfig_obj['clusters']) == 0:
                return False
            for cluster in kubeconfig_obj['clusters']:
                if cluster['name'] not in cluster_list:
                    return False
            return True
        return False

    def create_cluster(self, cluster_conf):
        """
        Creates a cluster
        :return:
        """
        conf = self._get_cluster_config(cluster_conf)
        create_command = "kops create cluster --v=0 \
          --cloud={0} \
          --node-count {1} \
          --master-size={2} \
          --master-zones={3} \
          --zones  {4} \
          --name={5} \
          --node-size={6} \
          --ssh-public-key={7} \
          --dns-zone {8}".format(self._cloud, conf['node_count'], conf['master_size'],
                                 conf['master_zones'], conf['zones'], conf['name'],
                                 conf['node_size'], conf['ssh_key'], conf['dns_zone'])
        process = subprocess.Popen(shlex.split(create_command), stdout=subprocess.PIPE, env=self._env)
        stdout = process.communicate()[0]
        self._logger.debug(stdout)

    def update_cluster(self, name):
        """
        Updates a cluster
        :return:
        """
        update_command = "kops update cluster {0} --yes".format(name)
        process = subprocess.Popen(shlex.split(update_command), stdout=subprocess.PIPE, env=self._env)
        stdout = process.communicate()[0]
        self._logger.debug(stdout)

    def delete_cluster(self, name):
        """
        Deletes a cluster
        :return:
        """
        delete_command = "kops delete cluster {0} --yes".format(name)
        process = subprocess.Popen(shlex.split(delete_command), stdout=subprocess.PIPE, env=self._env)
        stdout = process.communicate()[0]
        self._logger.debug(stdout)