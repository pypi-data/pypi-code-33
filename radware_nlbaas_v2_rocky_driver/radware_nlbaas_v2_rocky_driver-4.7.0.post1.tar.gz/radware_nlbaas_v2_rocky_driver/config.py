# Copyright 2018, Radware LTD. All rights reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy
import os
from oslo_config import cfg
from oslo_log import log as logging

OSLO_FUNC = 0
DIRECT_FUNC = 1
DEFAULT_VALUE = 2
VALUE = 3

def bull(str):
    return str.lower() == 'true'


CONFIG_TEMPLATE = {
    'vdirect_address': [cfg.StrOpt, str, None, None],
    'ha_secondary_address': [cfg.StrOpt, str, None, None],
    'vdirect_user': [cfg.StrOpt, str, 'vDirect', 'vDirect'],
    'vdirect_password': [cfg.StrOpt, str, 'radware', 'radware'],
    'port': [cfg.IntOpt, int, 2189, 2189],
    'ssl': [cfg.BoolOpt, bull, True, True],
    'ssl_verify_context': [cfg.BoolOpt, bull, True, True],
    'timeout': [cfg.IntOpt, int, 5000, 5000],
    'base_uri': [cfg.StrOpt, str, '', ''],
    'service_adc_type': [cfg.StrOpt, str, 'VA', 'VA'],
    'service_adc_version': [cfg.StrOpt, str, '', ''],
    'service_ha_pair': [cfg.BoolOpt, bull, False, False],
    'configure_allowed_address_pairs': [cfg.BoolOpt, bool, False, False],
    'service_throughput': [cfg.IntOpt, int, 100, 100],
    'service_ssl_throughput': [cfg.IntOpt, int, 100, 100],
    'service_compression_throughput': [cfg.IntOpt, int, 100, 100],
    'service_cache': [cfg.IntOpt, int, 20, 20],
    'service_resource_pool_ids': [cfg.ListOpt, list, [], []],
    'service_isl_vlan': [cfg.IntOpt, int, -1, -1],
    'service_session_mirroring_enabled': [cfg.BoolOpt, bull, False, False],
    'workflow_template_name': [cfg.StrOpt, str, 'openstack_LBaaS', 'openstack_LBaaS'],
    'child_workflow_template_names': [cfg.ListOpt, list, ['manage_l3'], ['manage_l3']],
    'workflow_params': [cfg.DictOpt, dict, {"twoleg_enabled": "_REPLACE_",
                         "ha_network_name": "HA-Network",
                         "ha_ip_pool_name": "default",
                         "allocate_ha_vrrp": True,
                         "allocate_ha_ips": True,
                         "data_port": 1,
                         "data_ip_address": "192.168.200.99",
                         "data_ip_mask": "255.255.255.0",
                         "gateway": "192.168.200.1",
                         "ha_port": 2},
                        {"twoleg_enabled": "_REPLACE_",
                         "ha_network_name": "HA-Network",
                         "ha_ip_pool_name": "default",
                         "allocate_ha_vrrp": True,
                         "allocate_ha_ips": True,
                         "data_port": 1,
                         "data_ip_address": "192.168.200.99",
                         "data_ip_mask": "255.255.255.0",
                         "gateway": "192.168.200.1",
                         "ha_port": 2}],
    'workflow_action_name': [cfg.StrOpt, str, 'apply', 'apply'],
    'stats_action_name': [cfg.StrOpt, str, 'stats', 'stats'],
    'status_action_name': [cfg.StrOpt, str, 'status', 'status'],
    'monitoring_pace': [cfg.IntOpt, int, 180, 180],
    'provision_service': [cfg.BoolOpt, bull, True, True],
    'configure_l3': [cfg.BoolOpt, bull, True, True],
    'configure_l4': [cfg.BoolOpt, bull, True, True]
}

LOG = logging.getLogger(__name__)


class RadwareConfig (object):

    def __init__(self, provider_name):
        self.provider_name = provider_name
        self.CONFIG = copy.deepcopy(CONFIG_TEMPLATE)
        self.load()

    def __getattr__(self, key):
        if not self.missing():
            return self.CONFIG[key][VALUE]
        return None

    def missing(self):
        return self.CONFIG['vdirect_address'][VALUE] == \
               self.CONFIG['vdirect_address'][DEFAULT_VALUE]

    def load(self):
        pass


class RadwareOsloConfig (RadwareConfig):

    def load(self):
        driver_opts = [
            self.CONFIG[key][OSLO_FUNC](
                key,
                default=self.CONFIG[key][DEFAULT_VALUE]
            ) for key in self.CONFIG.keys()
        ]

        cfg.CONF.register_opts(driver_opts, self.provider_name)
        conf = cfg.CONF.__getattr__(self.provider_name)
        for key in self.CONFIG.keys():
            self.CONFIG[key][VALUE] = conf.__getattr__(key)
        LOG.info('Service provider configuration was found in neutron configuration files')
        LOG.debug('Oslo Config Service provider configuration:  ' + repr(self.CONFIG))


class RadwareDirectConfig (RadwareConfig):

    def load(self):
        config = {}
        for loc in '/etc/radware', '/etc/neutron':
            try:
                file_name = os.path.join(loc, self.provider_name + '.conf')
                cfg.ConfigParser(file_name, config).parse()
                for k, v in config['DEFAULT'].iteritems():
                    if self.CONFIG[k]:
                        self.CONFIG[k][VALUE] = self.CONFIG[k][DIRECT_FUNC](v[0])
                LOG.info('Service provider configuration was found in ' + file_name)
                LOG.debug('Proprietary Service provider configuration:  ' + repr(self.CONFIG))
                return
            except EnvironmentError:
                pass

        LOG.info('No configuration for ' + self.provider_name +
                 ' provider was found in proprietary service provider configuration files')
