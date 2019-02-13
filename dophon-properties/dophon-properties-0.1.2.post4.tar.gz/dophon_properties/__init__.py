# encoding:utf-8
import sys
import re
from dophon_properties import tools

__version__ = '0.1.0'

LOGGER_ROOT = 'dophon_properties.'

PROP_FUN = '.properties'

MQ = {
    'name': 'mq',
    'modules': [
        'dophon_mq.properties',
        'dophon_mq.properties.properties',
        'dophon.mq.properties',
        'dophon.mq.properties.properties'
    ]
}

DOPHON = {
    'name': 'dophon',
    'modules': [
        'properties',
        'dophon.properties'
    ]
}

DB = {
    'name': 'database',
    'modules': [
        'dophon_db.properties',
        'dophon_db.properties.properties',
        'dophon.db.properties.properties',
        'dophon.db.properties'
    ]
}

CLOUD_CLIENT = {
    'name': 'cloud.client',
    'modules': [
        'dophon.cloud.client.properties',
        'dophon.cloud_client_properties',
        'dophon_cloud.client.properties',
        'dophon.cloud_client.properties',
        'dophon_cloud_client.properties',
    ]
}


@tools.module_edge_print('properties module')
def get_properties(prop_type: object, debug: bool = False):
    result = [get_property(per_prop_type,debug) for per_prop_type in prop_type] if isinstance(prop_type,list) else \
    get_property(prop_type,debug) if isinstance(prop_type,dict) else None


def get_property(prop_type: dict, debug: bool = False):
    m = __import__(LOGGER_ROOT + prop_type['name'] + PROP_FUN, fromlist=True)
    init_result = eval('m.init_properties()')
    for module_alias in prop_type['modules']:
        sys.modules[module_alias] = init_result
    if debug:
        # 打印模块信息
        for name in dir(init_result):
            if not re.match('^__.+__$', name):
                print(name, '---', getattr(init_result, name))
