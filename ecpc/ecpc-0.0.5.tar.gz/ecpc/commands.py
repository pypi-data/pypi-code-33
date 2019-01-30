'''
commands.py: Defines the ecpc commands.
'''
import subprocess
from datetime import datetime
import pytz
from botocore.exceptions import ClientError
import uuid

from ecpc import utilities
from ecpc.configuration import ECPC_DIR, config
from ecpc.data import database

def create_instance(region=None, instance_type=None, tag=None):
    '''
    Create and launch an instance
    '''
    if region is None:
        region = config['region']
    if instance_type is None:
        instance_type = config['instance_type']

    try:
        utilities.valid_selection(region, instance_type)
    except ValueError as e:
        print(e)
        exit(1)
    if tag is not None:
        if tag in database.ids():
            print('Error: name {} is already in use'.format(tag))
            exit(1)
        uid = tag
    else:
        uid = str(uuid.uuid4())[:8]
    database.add_entry(uid)
    data = {}
    data['uid'] = uid
    data['region'] = region
    data['instance_type'] = instance_type
    data['pem_file'] = None
    data['security_group_id'] = None
    data['image_id'] = None
    data['security_group_id'] = None
    data['instance_id'] = None
    database.update(uid, data)
    print('creating a {instance_type} instance in region {region} with ID {uid}'.format(**data))

    key_material = utilities.create_key_pair(region, uid)
    pem_file = utilities.create_pem_file(ECPC_DIR, uid, key_material)
    data['pem_file'] = pem_file
    database.update(uid, data)
    print('key pair created')

    security_group_id = utilities.create_security_group(region, uid)
    data['security_group_id'] = security_group_id
    database.update(uid, data)
    print('security group created')

    image_id = utilities.ami_from_source(region, config['source'])
    data['image_id'] = image_id
    database.update(uid, data)
    print('required ami identified')

    print('launching instance')
    try:
        instance_id = utilities.launch(ECPC_DIR, region, uid, image_id, instance_type)
        data['instance_id'] = instance_id
        database.update(uid, data)
        print('instance {instance_id} launched'.format(**data))
    except ClientError as e:
        print(e)
        terminate_instance(uid)
        
def list_instances():
    '''
    List running instances.
    '''
    ids = database.ids()
    rows = []
    row = ['ID', 'region', 'type', 'up_time', 'state', 'cost($)']
    rows.append(row)
    for uid in ids:
        data = database.get(uid)
        region = data['region']
        instance = utilities.get_instance(region, uid)
        if instance is None:
            data['up_time'] = '********'
            data['state'] = 'FAILED'
            data['cost'] = 0.0
        else: 
            state = utilities.get_instance_state(region, uid)
            data['instance_type'] = instance.instance_type
            utc = pytz.UTC
            up = datetime.now(utc) - instance.launch_time
            hours, remainder = divmod(int(up.total_seconds()), 3600)
            minutes, remainder = divmod(remainder, 60)
            seconds, remainder = divmod(remainder, 60)
            data['up_time'] = '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
            data['state'] = state
            data['cost'] = utilities.get_instance_cost(region, uid)
        row = '{uid} {region} {instance_type} {up_time} {state} {cost:3.2f}'.format(**data).split()
        rows.append(row)
    widths = [max(map(len, col)) for col in zip(*rows)]
    if len(rows) == 1:
        return
    for row in rows:
        print("  ".join((val.ljust(width) for val, width in zip(row, widths))))

def login_instance(uid):
    '''
    Log in to an instance
    '''
    try:
        entry = database.get(uid)
    except IndexError as e:
        print(e)
        exit(1)
    command = utilities.get_login_string(ECPC_DIR, entry['region'], uid)
    state = utilities.get_instance_state(entry['region'], uid)
    if state is not 'ready':
        print('Instance is not ready, in state {}'.format(state))
    else:
        exit(subprocess.call(command, shell=True))

def terminate_instance(uid):
    entry = database.get(uid)
    region = entry['region']
    utilities.terminate(region, uid)
    print('instance terminated')
    utilities.delete_security_group(region, uid)
    print('security group deleted')
    utilities.delete_key_pair(region, uid)
    print('key pair deleted')
    utilities.delete_pem_file(ECPC_DIR, uid)
    print('.pem file deleted')
    database.remove_entry(uid)
