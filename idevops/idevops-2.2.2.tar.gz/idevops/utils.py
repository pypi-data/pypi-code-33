#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 jack <jack@iOSTdeMacBook-Pro.local>
#
# Distributed under terms of the MIT license.

"""
utils
"""

import click
import json
import os.path
import prettytable
import re
import shutil
import yaml

_W_DIR, _ = os.path.split(__file__)
ENV = os.environ
ENV['ANSIBLE_CONFIG'] = os.path.join(_W_DIR, 'ansible.cfg')

CONF_DIR = '.idevops'
SEED_NAME = 'node-0'
ISERVER_KEYPAIR_GENERATOR = 'gen_keypair.go'
ISERVER_KEYPAIR_OF_MASTER = 'keypairs_master'
ISERVER_KEYPAIR_OF_SLAVE = 'keypairs_slave'
ISERVER_GENESIS = 'genesis.yml'
SHEADER = [u'name', u'type', u'region', u'instance_type', u'image']
DHEADER = [u'eip']
AWS_EBS_DEFAULT_SIZE = 20

class ErrMsg():
    def __init__(self, msg):
        self.msg = msg
        self.ctx = click.get_current_context()

def get_path(name, filename, expand_home=True):
    """Return absolute path of the file in network config dir."""
    if expand_home:
        return os.path.join(os.path.expanduser('~'), CONF_DIR, name, filename)
    else:
        return os.path.join('~', CONF_DIR, name, filename)

def get_config_by_name(name, bak=False, check_valid=True, allow_none=False):
    """Return config of the network.

    Parameters
    ---
    bak : bool
        If true, read config backup file instead of real config file
    check_valid : bool
        Pass to `release_address`; if true, only release no-ec-binding eip

    """
    config = []

    filename = get_path(name, 'config.yml' if not bak else 'config.yml.bak')
    assert os.path.exists(filename), ErrMsg('Missing config for network `{0}`.'.format(name,))

    with open(filename) as f:
        config = yaml.safe_load(f)

    assert u'network' in config, ErrMsg('Missing `network` section in config')
    config = config[u'network']

    if check_valid:
        config = list(filter(check_config_keys, config))
    if not allow_none:
        assert len(config) > 0, ErrMsg('Not enough valid nodes found in config')

    assert SEED_NAME in [ec['name'] if 'name' in ec else None for ec in config], 'Missing seed node `' + SEED_NAME + '` in config'

    return config

def check_config_keys(ec):
    for key in SHEADER:
        if not key in ec:
            return False
    return True

def show_missing_key_in_config(ec):
    error = []
    for key in SHEADER:
        if not key in ec:
            error.append('`' + key + '`')
    msg = 'Missing ' + ', '.join(error) + ' in ' + json.dumps(ec, indent=2)
    return msg

def create_post(name, config):
    write_config_to_file(name, config)
    gen_inventory(name, config)
    gen_ssh_config(name, config)

def write_config_to_file(name, config, is_backup=True):
    """Write ec2 info to local config.
    If `is_backup` is false, do not backup.
    """
    filename = get_path(name, 'config.yml')
    if is_backup:
        shutil.copy2(filename, get_path(name, 'config.yml.bak'))
    config = { 'network': config }
    with open(filename, 'w+') as f:
        yaml.safe_dump(config, f, default_flow_style=False)

def delete_post(name):
    clean_config(name)
    for filename in [
            get_path(name, name),           # priv key
            get_path(name, name + '.pub'),  # pub key
            get_path(name, 'inventory'),    # ansible inventory
            get_path(name, 'ssh'),          # ssh config
            get_path(name, 'config/' + ISERVER_KEYPAIR_OF_MASTER),  # iserver config
            get_path(name, 'config/' + ISERVER_KEYPAIR_OF_SLAVE),   # iserver config
            ]:
        if os.path.exists(filename):
            if os.path.isdir(filename):
                shutil.rmtree(filename)
            else:
                os.remove(filename)

def clean_config(name):
    """Restore network config without aws dynamic info."""
    config = get_config_by_name(name)
    for ec in config:
        for key in [u'eip', u'id']:
            if key in ec:
                del(ec[key])

    assert len(config) > 0, ErrMsg('Empty config to write')

    write_config_to_file(name, config)

def print_table(data):
    """Print a table of dic."""
    x = prettytable.PrettyTable()
    header = SHEADER + DHEADER
    if not u'eip' in data[0].keys():
        header.remove(u'eip')
    x.field_names = header
    for item in data:
        x.add_row([item[key] for key in header])
    x.align[u'eip'] = 'r'
    print(x)

def get_ssh_user(name, ec, data=None):
    if not data:
        data = read_data(field=u'image')
    user = next((image for image in data if image['name'].startswith(ec[u'image'])),
            {u'user': ec[u'user'] if u'user' in ec else 'root'})[u'user']
    return user

def read_data(all=False, field=u'image'):
    filename = os.path.join(_W_DIR, "data.yml")
    with open(filename) as f:
        data = yaml.safe_load(f)
        if all:
            return data
        else:
            return data[field]

def get_ami(ec):
    if u'image_id' in ec:
        return ec[u'image_id']
    else:
        data = read_data(field=u'image')
        ami = next((image for image in data if image['name'].startswith(ec[u'image'])), None)
        assert ami, 'Image `' + ec[u'image'] + '` not found'
        assert ec[u'region'] in ami[u'ami'], 'Image `' + ec[u'image'] + '` not found in ' + ec[u'region']

        return ami[u'ami'][ec[u'region']]

def gen_inventory(name, config):
    inventory_dir = get_path(name, 'inventory')

    if not os.path.isdir(inventory_dir):
        os.mkdir(inventory_dir)

    with open(get_path(name, 'inventory/hosts'), 'w+') as f:
        ec_type = []
        for ec in config:

            assert u'eip' in ec, ErrMsg('Missing ip address. Maybe `create` or `sync` first ?')

            ec_type.append(ec[u'type'])
            f.write('\t'.join([
                ec[u'name'],
                'ansible_host=' + ec[u'eip'],
                'ansible_ssh_user=' + get_ssh_user(name, ec),
                ]))
            f.write('\n')

        f.write('\n')

        # hotfix `'dict object' has no attribute 'slave'`
        ec_type = ['master', 'slave']

        for e_type in set(ec_type):
            f.write('[' + e_type + ']\n')
            for ec in filter(lambda e: e['type'] == e_type, config):
                f.write(ec[u'name'])
                f.write('\n')
            f.write('\n')

        f.write('[all:vars]\n')
        f.write('cluster_name = ' + name + '\n')
        f.write('ansible_ssh_private_key_file = ' + get_path(name, name, expand_home=False) + '\n')

def gen_ssh_config(name, config):
    with open(get_path(name, 'ssh'), 'w+') as f:
        f.write('StrictHostKeyChecking no\n')
        f.write('UserKnownHostsFile /dev/null\n')
        f.write('IdentityFile ' + get_path(name, name, expand_home=False) + '\n')

        data = read_data(field=u'image')
        for ec in config:
            assert u'eip' in ec, ErrMsg('Missing ip address. Maybe `create` or `sync` first ?')

            f.write('Host ' + ec[u'name'] + '\n')
            f.write('\tUser ' + get_ssh_user(name, ec, data) + '\n')
            f.write('\tHostname ' + ec[u'eip'] + '\n')

def find_playbook(playbook):
    if not os.path.exists(playbook):
        filename = os.path.join(_W_DIR, 'playbooks', playbook + ".yml")
        assert os.path.exists(filename), ErrMsg('Playbook `' + playbook + '` not found.')
        playbook = filename
    return playbook

def list_playbooks(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Available playbook:')
    for file in os.listdir(os.path.join(_W_DIR, 'playbooks')):
        click.secho('\t' + file.split('.yml')[0], bold=True)
    ctx.exit()

def check_config_aws_valid(config):
    """Check config if aws thought it valid.

    Return
    ---
    config_err : [ { data: config, msg: message } ... ]
        If true, read config backup file instead of real config file
    config_valid : [ config ... ]
        Pass to `release_address`; if true, only release no-ec-binding eip

    """
    config_err = []
    config_valid = []
    data = read_data(all=True)
    data_instance_type = [ins['name'] for ins in data['instance_type']]
    data_type = data['type']
    data_region = data['region'].keys()
    for ec in config:
        try:
            if ec['instance_type'] not in data_instance_type:
                config_err.append({'data': ec, 'msg': 'Instance type `' + ec['instance_type'] + '` not found in ' + json.dumps(ec, indent=2) })
                continue

            if ec['type'] not in data_type:
                config_err.append({'data': ec, 'msg': 'Invalid type `' + ec['type'] + '` in ' + json.dumps(ec, indent=2) })
                continue

            if ec['region'] not in data_region:
                config_err.append({'data': ec, 'msg': 'Invalid region `' + ec['region'] + '` in ' + json.dumps(ec, indent=2) })
                continue

            get_ami(ec)
            config_valid.append(ec)
        except AssertionError as e:
            config_err.append({'data': ec, 'msg': str(e) + ' in ' + json.dumps(ec, indent=2) })
    return config_err, config_valid

# [human sort](https://stackoverflow.com/questions/2545532/python-analog-of-natsort-function-sort-a-list-using-a-natural-order-algorithm)
def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]
