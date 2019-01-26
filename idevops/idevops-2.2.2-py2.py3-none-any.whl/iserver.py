#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 jack <jack@iOSTdeMacBook-Pro.local>
#
# Distributed under terms of the MIT license.

"""
generate iserver config, adapt to [github.com/iost-official/go-iost/account](https://github.com/iost-official/go-iost/blob/develop/account/account.go)
"""

import subprocess

from jinja2 import Template
from idevops.utils import *

def gen_iserver_config(name, skip=False, default_balance=0, nproducer=17):

    # preprocess config
    config = get_config_by_name(name)

    # calculate mem limit
    data = read_data(field=u'instance_type')
    mem = next((item['mem'] for item in data if item['name'] == config[0][u'instance_type']), 3)
    mem_limit = str(int(mem * 0.9)) + 'G'

    seed_node = next(ec for ec in config if ec['name'] == SEED_NAME)
    assert 'eip' in seed_node, 'Mission ip address for seed node. Maybe `create` or `sync` first ?'
    seed_ip = seed_node['eip']

    master = list(filter(lambda x: x['type'] == 'master', config))
    slave = list(filter(lambda x: x['type'] == 'slave', config))

    # generate iserver keypair
    if not skip:
        gen_iserver_key_pair(name, m=len(master), s=len(slave))
    assert os.path.exists(get_path(name, 'config/' + ISERVER_KEYPAIR_OF_MASTER)), 'Internal error: key pair is not generated as expected'
    assert os.path.exists(get_path(name, 'config/' + ISERVER_KEYPAIR_OF_SLAVE)), 'Internal error: key pair is not generated as expected'

    # generate ansible hostvars
    host_vars_dir = get_path(name, 'inventory/host_vars')
    group_vars_dir = get_path(name, 'inventory/group_vars')
    for d in [host_vars_dir, group_vars_dir]:
        if not os.path.isdir(d):
            os.mkdir(d)

    configs = [
            {
                'type': 'master',
                'config': master,
                'keypair': ISERVER_KEYPAIR_OF_MASTER,
                },
            {
                'type': 'slave',
                'config': slave,
                'keypair': ISERVER_KEYPAIR_OF_SLAVE,
                }
            ]

    witnessinfo = []
    for config in configs:

        keypairs = []
        with open(get_path(name, 'config/' + config['keypair'])) as f:
            keypairs = f.read().strip()
            if keypairs:
                keypairs = keypairs.split('\n')
        assert len(keypairs) == len(config['config']), 'Number of keypairs does not match (type: ' + config['type'] + ')'

        for i, ec, kp in zip(range(0, len(keypairs)), config['config'], keypairs):
            pubk, privk = kp.split(',')
            data = {
                'id': 'producer{:03d}'.format(i),
                'privkey': privk,
                'pubkey': pubk,
                'seed_ip': seed_ip,
                'type': config['type'],
                'trytx': 'false' if config['type'] == 'master' else 'true'
            }
            with open(get_path(name, 'inventory/host_vars/' + ec['name']), 'w+') as f:
                yaml.safe_dump(data, f, default_flow_style=False)

            if config['type'] == 'master':
                witnessinfo.append({
                    'id': data['id'],
                    'active': data['pubkey'],
                    'owner': data['pubkey'],
                    'signatureblock': data['pubkey'],
                    'balance': default_balance,
                })

    # generate genesis config
    with open(get_path(name, 'inventory/group_vars/all'), 'w+') as f:
        yaml.safe_dump({ 'witnessinfo': witnessinfo[:nproducer], 'mem_limit': mem_limit }, f, default_flow_style=False)

def gen_iserver_key_pair(name, **kargs):
    """Generate iserver keypair using go"""
    path = get_path(name, 'config')
    os.chdir(path)

    assert { 'm', 's' } <= set(kargs.keys()), 'Missing node type; check your config'
    assert os.path.exists(ISERVER_KEYPAIR_GENERATOR), 'Missing source file: ' + ISERVER_KEYPAIR_GENERATOR

    cmd = ['go', 'run', ISERVER_KEYPAIR_GENERATOR,
            '-m', str(kargs['m']), '-s', str(kargs['s'])]
    ret = subprocess.call(cmd)
    assert ret == 0, 'Generating keypair failed. You may exec `' + ' '.join(cmd) + '` in `' + path + '` handly'

