#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 jack <jack@iOSTdeMacBook-Pro.local>
#
# Distributed under terms of the MIT license.

"""
aws
"""

import boto3
import click
import warnings

from botocore.exceptions import ClientError
from idevops.utils import *
from idevops.shell_wrapper import gen_key_pair

def create(name, is_overwrite=False, fast=False):
    """Create network.

    1. generate keypair
    2. do stuff before creating
    3. create each ec2
    4. update config
    """

    ecs_config_read = get_config_by_name(name)

    gen_key_pair(name, is_overwrite)

    regions = get_regions_by_name(name) if fast else get_all_regions()
    with click.progressbar(regions, label='Creating material:'.ljust(25)) as bar:
        for region in bar:
            create_init_aws(name, region)

    ecs = []            # list of ec created
    ecs_config = []     # list of ec config updated
    with click.progressbar(ecs_config_read, label='Creating ec2 instances:'.ljust(25)) as bar:
        for ec_config in bar:
            ec = create_with_eip(name, ec_config)
            ecs = ecs + [ec]

    with click.progressbar(ecs_config_read, label='Waiting to bind eip:'.ljust(25)) as bar:
        for ec_config in bar:
            ec = filter_one_by_tag(ecs, 'Name', ec_config[u'name'])
            allocation = allocate_address(name, ec_config)
            ec.wait_until_running()
            resp = associate_address(ec_config, ec, allocation)
            ec.eip = allocation[u'PublicIp']
            ec_config[u'eip'] = ec.eip
            ec_config[u'id'] = ec.id
            ecs_config = ecs_config + [ec_config]

    click.echo('Syncing info ...')
    create_post(name, ecs_config)

def create_with_eip(name, ec_config, cnt=1, bind_eip=False):
    """Create ec2 instance with config, and bind eip.

    The default number is 1.
    """

    ec2 = boto3.resource('ec2', region_name=ec_config[u'region'])
    ec = ec2.create_instances(
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/xvda',
                    'Ebs': {
                        'VolumeSize': ec_config[u'ebs'] if u'ebs' in ec_config else AWS_EBS_DEFAULT_SIZE
                        }
                    },
                {
                    'DeviceName': '/dev/xvdb',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': 1000,
                        'VolumeType': 'sc1',
                        }
                    },
                ],
            ImageId=get_ami(ec_config),
            MinCount=cnt,
            MaxCount=cnt,
            InstanceType=ec_config['instance_type'],
            KeyName=name,
            SecurityGroups=[
                name
                ],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': ec_config['name']
                            },
                        {
                            'Key': 'Type',
                            'Value': ec_config['type']
                            },
                        {
                            'Key': 'Network',
                            'Value': name
                            }
                        ]
                    }
                ]
            )

    assert len(ec) == cnt, ErrMsg('Created ec2 less than expected')

    if bind_eip:
        for ec_instance in ec:
            allocation = allocate_address(name, ec_config)
            ec_instance.wait_until_running()
            resp = associate_address(ec_config, ec_instance, allocation)
            ec_instance.eip = allocation[u'PublicIp']

    return ec[cnt - 1]

def create_init_aws(name, region):
    """Do stuff before creating ec2."""
    upload_key_pair(name, region)
    create_security_group(name, region)

def delete_clean_aws(name, region, eip_only=False):
    """Do stuff after deleting ec2.

    Parameters
    ---
    eip_only : bool
        Pass to `release_address`; if true, only release no-ec-binding eip

    """
    try:
        release_address(name, region, eip_only=eip_only)
        if not eip_only:
            delete_key_pair(name, region)
            delete_security_group(name, region)
    except ClientError as e:
        if 'does not exist' not in str(e):
            raise e
        warnings.warn(click.style('Resources not found in region ' + region, fg='yellow'), stacklevel=2)

def release_address(name, region, ec_config=None, eip_only=False):
    """Release all eip with tag of network.

    Parameters
    ---
    ec_config : dict
        Release eip with tag of name in `ec_config`
    eip_only : bool
        If true, only release no-ec-binding eip

    """
    client = boto3.client('ec2', region_name=region)

    eip_filter = [
        {
            'Name': 'tag:Name',
            'Values': [ec_config[u'name']]
        }
    ] if ec_config else []

    network_filter = [
        {
            'Name': 'tag:Network',
            'Values': [name]
        }
    ]

    resp = client.describe_addresses(Filters=eip_filter + network_filter)
    if eip_only:
        eips = list(filter(lambda x: u'InstanceId' not in x, resp['Addresses']))
        for eip_id in [r['AllocationId'] for r in eips]:
            client.release_address(AllocationId=eip_id)
    else:
        for eip_id in [r['AllocationId'] for r in resp['Addresses']]:
            client.release_address(AllocationId=eip_id)

def allocate_address(name, ec_config):
    client = boto3.client('ec2', region_name=ec_config[u'region'])
    allocation = client.allocate_address(Domain='vpc')
    client.create_tags(Resources=[allocation['AllocationId']],
            Tags=[
                {
                    'Key': 'Name',
                    'Value': ec_config['name']
                    },
                {
                    'Key': 'Type',
                    'Value': ec_config['type']
                    },
                {
                    'Key': 'Network',
                    'Value': name
                    }
                ]
            )
    return allocation

def associate_address(ec_config, ec, allocation):
    client = boto3.client('ec2', region_name=ec_config[u'region'])
    return client.associate_address(AllocationId=allocation['AllocationId'],
            InstanceId=ec.id)

def filter_one_by_tag(ecs, key, value):
    for ec in ecs:
        tag = next((tag for tag in ec.tags if tag[u'Key'] == key), None)
        if tag and tag[u'Value'] == value:
            return ec
    return None

def list_print(name=None, force_sync=False):
    config = get_config_by_name(name)
    if force_sync or not next((ec for ec in config if u'eip' in ec), None):
        sync(name)
        config = get_config_by_name(name)
    print_table(config)

def sync(name, prune_local=False):
    """Fetch network info from aws, update local config if necessary.
    Warns are shown once there is dismatch between online info and local config.
    If set `prune_local`, local config is pruned according to online info.
    """
    ecs = get_all(name, all_region=True)
    ecs_config = []
    is_changed = False
    for ec_config in get_config_by_name(name):

        ec = filter_one_by_tag(ecs, 'Name', ec_config[u'name'])

        if not ec:
            warnings.warn(click.style('Node not running\n' +
                    # It means that local config has more nodes than aws.
                        'name: ' + ec_config[u'name'], fg='yellow'), stacklevel=2)
            if prune_local:
                is_changed = True
            continue

        if not u'eip' in ec_config or ec_config[u'eip'] != ec.public_ip_address:
            ec_config[u'eip'] = ec.public_ip_address
            is_changed = True
        if not u'id' in ec_config or ec_config[u'id'] != ec.id:
            ec_config[u'id'] = ec.id
            is_changed = True

        ecs_config = ecs_config + [ec_config]
        ecs.remove(ec)

    if len(ecs) > 0:
        warnings.warn(click.style('Redundant online node(s) detected !\n' +
                # It means that local config has less nodes than aws.
                '\n'.join(
                    ['id: ' + ec.id + ', ip: ' + ec.public_ip_address for ec in ecs]
                    ), fg='yellow'), stacklevel=2)

    if is_changed:
        create_post(name, ecs_config)

def get_regions_by_name(name):
    regions = [ec[u'region'] for ec in get_config_by_name(name)]
    return list(set(regions))

def get_all(name, all_region=False, list_all=False):
    """Get all ec2 with tag of network.

    Parameters
    ---
    all_region : bool
        If true, scan all regions instead of regions shown in local config
    list_all : bool
        If true, include all ec2 no matter its state, otherwise running ones only

    """
    ecs = []
    regions = []
    if all_region:
        regions = get_all_regions()
    else:
        regions = get_regions_by_name(name)

    with click.progressbar(regions, label='Gathering info:'.ljust(25)) as bar:
        for region in bar:
            ec2 = boto3.resource('ec2', region_name=region)

            state_filter = [] if list_all else [
                {
                    'Name': 'instance-state-name',
                    'Values': ['running']
                }
            ]

            network_filter = [
                {
                    'Name': 'tag:Network',
                    'Values': [name]
                }
            ]

            instances = ec2.instances.filter(Filters=network_filter + state_filter)

            # add region, because ec2.Instance has no region field
            for ec in instances:
                ec.region = region
                ecs.append(ec)

    return ecs

def delete(name, nodes=None, fast=False):
    """Delete network.

    1. get all running ec2 with tag of network, terminate each one
    2. wait the termination
    3. do stuff after deleting ec2
    4. delete local key pair
    5. restore the config
    """
    ecs = get_all(name, list_all=True)
    with click.progressbar(ecs, label='Shutdown ec2:'.ljust(25)) as bar:
        for ec in bar:
            ec.terminate()

    with click.progressbar(ecs, label='Waiting termination:'.ljust(25)) as bar:
        for ec in bar:
            ec.wait_until_terminated()

    regions = get_regions_by_name(name) if fast else get_all_regions()
    with click.progressbar(regions, label='Cleaning regions:'.ljust(25)) as bar:
        for region in bar:
            delete_clean_aws(name, region)

    click.echo('Deleting temp files ...')
    delete_post(name)

def upload_key_pair(name, region):
    client = boto3.client('ec2', region_name=region)
    with open(get_path(name, name + '.pub')) as f:
        resp = client.import_key_pair(KeyName=name, PublicKeyMaterial=f.read())

def delete_key_pair(name, region):
    client = boto3.client('ec2', region_name=region)
    client.delete_key_pair(KeyName=name)

def create_security_group(name, region):
    client = boto3.client('ec2', region_name=region)
    client.create_security_group(Description='For ' + name, GroupName=name)
    client.authorize_security_group_ingress(
            GroupName=name,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{
                        'CidrIp': '0.0.0.0/0'
                        }]
                    },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 30000,
                    'ToPort': 30005,
                    'IpRanges': [{
                        'CidrIp': '0.0.0.0/0'
                        }]
                    },
                {
                    'IpProtocol': 'udp',
                    'FromPort': 30005,
                    'ToPort': 30005,
                    'IpRanges': [{
                        'CidrIp': '0.0.0.0/0'
                        }]
                    }
                ]
            )

def delete_security_group(name, region):
    client = boto3.client('ec2', region_name=region)
    client.delete_security_group(GroupName=name)

def get_icmp_ip_permission():
    return [
        {
            'IpProtocol': 'icmp',
            'FromPort': -1,
            'ToPort': -1,
            'IpRanges': [{
                'CidrIp': '0.0.0.0/0'
            }]
        },
    ]

def insert_icmp_to_security_group(name, region):
    client = boto3.client('ec2', region_name=region)
    try:
        client.authorize_security_group_ingress(
                GroupName=name,
                IpPermissions=get_icmp_ip_permission(),
        )
    except ClientError as e:
        if u'already exists' not in str(e):
            raise e

def revoke_icmp_to_security_group(name, region):
    client = boto3.client('ec2', region_name=region)
    client.revoke_security_group_ingress(
            GroupName=name,
            IpPermissions=get_icmp_ip_permission(),
    )

def open_icmp(name):
    with click.progressbar(get_regions_by_name(name), label='Open ICMP:'.ljust(25)) as bar:
    # with click.progressbar(get_all_regions(), label='Open ICMP:'.ljust(25)) as bar:
        for region in bar:
            insert_icmp_to_security_group(name, region)

def close_icmp(name):
    with click.progressbar(get_regions_by_name(name), label='Close ICMP:'.ljust(25)) as bar:
    # with click.progressbar(get_all_regions(), label='Close ICMP:'.ljust(25)) as bar:
        for region in bar:
            revoke_icmp_to_security_group(name, region)

def get_all_regions(online=False):
    """Get all aws regions."""

    regions = []
    if online:
        client = boto3.client('ec2')
        for r in client.describe_regions()[u'Regions']:
            regions.append(r[u'RegionName'])
        return regions
    else:
        data = read_data(field=u'region')
        return data.keys()

def need_upgrade(config, ec):
    """Calculate if ec matches config

    Returns
    ---
    (instance_type, ebs):   Upgrade is needed
    (None, None):           Match; no need to upgrade

    """
    instance_type = None
    ebs = None

    # compare instance_type
    if ec.instance_type != config['instance_type']:
        instance_type = config['instance_type']

    # compare ebs size
    config_ebs = config[u'ebs'] if u'ebs' in config else AWS_EBS_DEFAULT_SIZE
    ec_ebs = next(v for v in list(ec.volumes.all()) if v.volume_type in ['standard', 'gp2'])
    if ec_ebs and config_ebs != ec_ebs.size:
        ebs = config_ebs

    # force upgrade
    if 'upgrade' in config and config['upgrade']:
        del(config['upgrade'])
        if not instance_type:
            instance_type = config['instance_type']

    return instance_type, ebs

def need_retag(config, ec):
    tags = []
    for tag in ec.tags:
        if tag['Key'] == 'Network':
            continue
        val = config[tag['Key'].lower()]
        if tag['Value'] != val:
            tags.append({
                'Key': tag['Key'],
                'Value': val
            })
    return tags

def need_recreate(config, ec):
    return ec.region != config['region']

def scale(name, dry_run=False):
    ecs = get_all(name, all_region=True)
    ecs_config = get_config_by_name(name)

    click.echo('Calculating difference ... ', nl=False)
    to_delete = list(ecs)
    to_create = []
    to_upgrade = []
    to_retag = []
    for ec in ecs_config:                                       # LOOP THROUGH local ec config
        ec_unchange = None
        if 'id' in ec:                                          # find eci via id
            ec_unchange = next((e for e in ecs if e.id == ec['id']), None)
        else:                                                   # if no id, using name
            ec_unchange = filter_one_by_tag(ecs, 'Name', ec['name'])

        if ec_unchange:                                         # IF eci exists
            tags = need_retag(ec, ec_unchange)
            instance_type, ebs = need_upgrade(ec, ec_unchange)
            if need_recreate(ec, ec_unchange):                  #   if need recreate
                to_create.append(ec)                            #     delete, create
            elif instance_type or ebs:                          #   IF need upgrade
                to_upgrade.append((ec, ec_unchange, instance_type, ebs))
                to_delete.remove(ec_unchange)                   #     upgrade
            elif tags:                                          #   if need retag
                to_retag.append((ec, ec_unchange, tags))        #     retag
                to_delete.remove(ec_unchange)                   #
            else:                                               #   else nothing to do
                to_delete.remove(ec_unchange)                   #     stay
        else:                                                   # IF eci not exists
            to_create.append(ec)                                #   create eci

    click.echo('Result:')
    click.echo('  To be create:'.ljust(20) + str([ec['name'] for ec in to_create]))
    click.echo('  To be delete:'.ljust(20) + str([ec.id for ec in to_delete]))
    click.echo('  To be upgrade:'.ljust(20) + str(['('+c['name']+','+e.id+')' for c,e,_,_ in to_upgrade]))
    click.echo('  To be retag:'.ljust(20) + str(['('+c['name']+','+e.id+')' for c,e,_ in to_retag]))

    if dry_run:
        return

    ecs = list(set(ecs) - set(to_delete))

    if to_delete:
        with click.progressbar(to_delete, label='Shutdown ec2 instances:'.ljust(25)) as bar:
            for ec in bar:
                ec.terminate()

        with click.progressbar(to_delete, label='Waiting termination:'.ljust(25)) as bar:
            for ec in bar:
                ec.wait_until_terminated()

        # with click.progressbar(get_regions_by_name(name), label='Cleaning eip:'.ljust(25)) as bar:
        with click.progressbar(get_all_regions(), label='Cleaning eip:'.ljust(25)) as bar:
            for region in bar:
                delete_clean_aws(name, region, eip_only=True)

    if to_create:
        with click.progressbar(to_create, label='Creating ec2 instances:'.ljust(25)) as bar:
            for ec_config in bar:
                ec = create_with_eip(name, ec_config)
                ecs = ecs + [ec]

        with click.progressbar(to_create, label='Waiting to bind eip:'.ljust(25)) as bar:
            for ec_config in bar:
                ec = filter_one_by_tag(ecs, 'Name', ec_config[u'name'])
                allocation = allocate_address(name, ec_config)
                ec.wait_until_running()
                resp = associate_address(ec_config, ec, allocation)
                ec.eip = allocation[u'PublicIp']

                ec_config_new = next(ec for ec in ecs_config if ec['name'] == ec_config['name'])
                ec_config_new[u'eip'] = ec.eip
                ec_config_new[u'id'] = ec.id

    if to_upgrade:
        with click.progressbar(to_upgrade, label='Upgrading ec2:'.ljust(25)) as bar:
            for config, ec, instance_type, ebs in bar:

                # upgrade instance type
                if instance_type:
                    ec.stop()     # need stop to upgrade
                    ec.wait_until_stopped()
                    ec.modify_attribute(Attribute='instanceType', Value=config['instance_type'])
                    ec.start()
                    ec.wait_until_running()

                # enlarge ebs
                if ebs:
                    try:
                        vol = next(v for v in list(ec.volumes.all()) if v.volume_type in ['standard', 'gp2'])
                        client = boto3.client('ec2', region_name=ec.region)
                        resp = client.modify_volume(VolumeId=vol.volume_id, Size=ebs)
                    except ClientError as e:
                        click.secho(str(e), fg='red')

    if to_retag:
        with click.progressbar(to_retag, label='Re-taging ec2:'.ljust(25)) as bar:
            for _, ec, tags in bar:
                ec.create_tags(Tags=tags)

    click.echo('Syncing info ...')
    create_post(name, ecs_config)

def reboot(name, nodes, dry_run=False):
    """Reboot nodes, which splited by comma"""
    config = get_config_by_name(name)
    nodes = nodes.split(',')
    wait_list = []
    for node in nodes:
        ec = next((ec for ec in config if ec['name'] == node), None)
        if ec and 'id' in ec:
            client = boto3.client('ec2', region_name=ec['region'])
            client.reboot_instances(InstanceIds=[ec['id']], DryRun=dry_run)
            wait_list.append(ec['id'])
        else:
            warnings.warn(click.style('Node not found: ' + node, fg='yellow'), stacklevel=2)

