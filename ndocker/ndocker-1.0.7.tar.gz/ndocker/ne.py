# pylint: disable=W0614
import time
from abc import ABCMeta, abstractmethod
from networks import DockerNetworking
from common.yamler import Yaml
from common import logger
from docker.docker_cmd import *
from necfg import *


class NE(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.networking = DockerNetworking()

    @abstractmethod
    def create_networks(self, **kwargs):
        raise NotImplementedError()


class Host(NE):
    def __init__(self, ymal_cfg):
        super(Host, self).__init__()

        self.infos = Yaml(ymal_cfg).infos

    def create_networks(self, **kwargs):
        vswitches = self.infos.get('vswitches')
        for vswitch in vswitches:
            self.networking.create_bridge(vswitch.get(
                'bridge'), vswitch.get('physicalport'))

    def reset_networks(self):
        vswitches = self.infos.get('vswitches')
        logger.debug(vswitches)
        for vswitch in vswitches:
            self.networking.del_bridge(vswitch.get('bridge'))


class Container(NE):
    def __init__(self, yaml_cfg):
        super(Container, self).__init__()
        self.cfg = ServicesCfg(yaml_cfg)

    def create_networks(self, **kwargs):
        for container in self.cfg.containers():
            infos = self.cfg.infos(container)
            i = 0 if infos.network_mode == 'none' else 1
            for br_name, network in infos.networks:
                for info in network:
                    ip = info.get('ip')
                    tag = info.get('vtag', 0)
                    gw = info.get('gw', False)
                    veth_name = "eth{}".format(i)
                    logger.debug("eth{}".format(i))
                    i += 1
                    self.networking.attach_container(
                        container, br_name, veth_name, ip, tag, gw, txoff=(br_name == 'br-s1'))

    def start_service(self):
        docker = DockerCmd()
        for container in self.cfg.containers():
            if not docker.isExist(container):
                logger.debug('Container {} does not exist.'.format(container))
                self._create_service(container)

            docker.restart(container)
            time.sleep(1)

            if not docker.isHealth(container):
                logger.error('Create {} failed.'.format(container))
                raise DockerCmdExecError()

            infos = self.cfg.infos(container)
            cmd = "exec -u root -it {} sh -c \"echo '127.0.0.1  {}'>>/etc/hosts\"".format(
                container, infos.hostname)
            docker.execute(cmd)

        self.create_networks()

    def stop_service(self):
        docker = DockerCmd()
        for container in self.cfg.containers():
            docker.stop(container)
            infos = self.cfg.infos(container)
            i = 0 if infos.network_mode == 'none' else 1
            for br_name, network in infos.networks:
                for _ in network:
                    self.networking.dettach_container(
                        container, br_name, "eth{}".format(i))
                    i += 1

    def restart_service(self):
        self.stop_service()
        self.start_service()

    def rm_service(self):
        self.stop_service()

        docker = DockerCmd()
        for container in self.cfg.containers():
            docker.rm(container)

    def _create_service(self, container):
        docker = DockerCmd()

        infos = self.cfg.infos(container)
        docker.pull(infos.image)

        logger.debug("container infos: {}".format(infos.__dict__))
        cmd = "--name {} --hostname {} --net='{}' -p {} --init --restart=always -e VNC_RESOLUTION={} -v {} --privileged -d {}".format(
            container, infos.hostname, infos.network_mode, ' -p '.join(
                infos.ports),
            infos.vnc_resolution, ' -v '.join(infos.volumes), infos.image)
        docker.run(cmd)
        time.sleep(3)

        if not docker.isHealth(container):
            logger.error('Create {} failed.'.format(container))
            raise DockerCmdExecError()
