# pylint: disable=W0614
import os
import sys

root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, root)
# pylint: disable=no-name-in-module,import-error
from common import logger
from common.utils import *
from common.yamler import Yaml

class ContainerCfg(object):
    def __init__(self, name, **kwargs):
        self.name = name
        
        for key in kwargs.keys():
            setattr(self, key, kwargs.get(key))
        
        self.hostname = kwargs.get('hostname', '{}-nj'.format(self.name))
        self.image = kwargs.get('image')
        self.volumes = kwargs.get('volumes')
        self.ports = kwargs.get('ports')
        self.networks = kwargs.get('networks')
        self.network_mode = kwargs.get('network_mode')
        self.vnc_resolution = kwargs.get('vnc_resolution')
        
class ServicesCfg(object):
    def __init__(self, yaml_cfg):
        logger.debug("cfg: {}".format(yaml_cfg))
        self.cfg = Yaml(yaml_cfg).infos
        self.services = self.cfg['services']
        self.networks = self.cfg['networks']

        self._verify_data()

        for c in self.containers():
            container = self.services.get(c)
            container['networks'] = [(i, self.networks[i]) for i in container['networks']]

    '''
    Return containers name in list.
    '''
    def containers(self):
        return self.services.keys()
    
    '''
    Return a container configration by an object of ContainerCfg
    '''
    def infos(self, container_name):
        if not self.services.has_key(container_name):
            logger.error('Unknown container name {}.'.format(container_name))
            return None
        
        container = self.services.get(container_name)
        return ContainerCfg(container_name, **container)

    def _verify_data(self):
        containers = [container for container in self.services.keys() if len(container)>5]
        if len(containers) > 0:
            logger.error("The length of the container name > 5:{}".format(' '.join(containers)))
            sys.exit(1)
    