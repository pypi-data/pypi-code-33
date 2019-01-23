import datetime
import glob
import json
import os
import pickle
import shutil
from invoke import task

from reliabilly.components.data.mongo_client import MongoDataClient
from reliabilly.components.web.http_requestor import HttpRequestor
from reliabilly.settings import Constants, get_raw_service_url, get_production_service_url

MONGO_DROP_ALL_CMD = 'docker exec mongodb ' \
                     'mongo --quiet --eval ' \
                     '"db.getMongo().getDBNames().forEach(function(i)' \
                     '{db.getSiblingDB(i).dropDatabase()})"'
INFRASTRUCTURE = 'infrastructure'
ALERTS = 'alerts'
INCIDENTS = 'incidents'
TOPIARY = 'topiary'
SLOTH = 'sloth'
SLOS = 'slos'
USERS = 'users'


def dump_mongo_data():
    request = HttpRequestor()
    url = get_production_service_url(INFRASTRUCTURE, 0) + '&limit=90'
    result = request.get(url)
    infrastructure_list = result.json()[INFRASTRUCTURE]
    with open('./data/infrastructure.json', 'w+') as infra_file:
        infra_file.write(json.dumps(infrastructure_list, default=str))


def load_mongo_data():
    print("Loading initial data into mongo...")
    local_mongo = 'mongodb://localhost'
    for filename in glob.glob('./data/fixtures/*.json'):
        with open(filename) as test_file:
            collection = os.path.basename(test_file.name).split('.')[0]
            client = MongoDataClient(host=local_mongo, table=collection)
            item_list = json.load(test_file)
            for item in item_list:
                client.create(item)


@task
def dump(_):
    """ This dumps our data store into json files. """
    dump_mongo_data()


@task(aliases=['ltd'])
def load_test_data(_):
    """ Loads data into the data store. """
    load_mongo_data()


@task
def clean_data(ctx):
    """ Drop all mongo db"""
    print("Dropping all mongo DBs...")
    ctx.run(MONGO_DROP_ALL_CMD)


@task
def backup(ctx):
    """ Take a copy of services data and push to S3 bucket"""
    print("Backing up services data...")
    create_folder('backup')
    collect(ctx)
    filename = push_to_s3(ctx)
    tidy_up_backup_resources(f'{filename}.zip')


def create_folder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print(f'Error: Creating directory {directory}')


@task
def collect(_):
    """ Collect all data using our service apis and save the data
    in pickle files for consumption and testing. """
    collect_service_data(SLOS)
    collect_service_endpoint_data(SLOS, Constants.DEBUG_ROUTE)
    collect_service_data(INCIDENTS)
    collect_service_data(TOPIARY)
    collect_service_data(ALERTS)
    collect_service_data(USERS)
    collect_service_data(SLOTH)
    collect_service_data(INFRASTRUCTURE)


def collect_service_endpoint_data(service, endpoint, log=True):
    requestor = HttpRequestor()
    if log:
        print(f'Collecting {service}/{endpoint}...')
    requestor.save_data_items(service, endpoint, False)


def collect_service_data(service, log=True):
    requestor = HttpRequestor()
    if log:
        print(f'Collecting {service}...')
    requestor.save_data_items(service)


def tidy_up_backup_resources(filename):
    if os.path.isfile(filename):
        os.remove(filename)
    else:
        print(f'Error: {filename} not found')

    try:
        shutil.rmtree('backup')
    except OSError as error:
        print(f'Error: {error.filename}, {error.strerror}')


def push_to_s3(ctx):
    date = datetime.date.today()
    filename = f'platformbackup-{date}'
    shutil.make_archive(filename, 'zip', None, 'backup')
    command = f'aws s3 cp {filename}.zip {Constants.BACKUPS_BUCKET}/'
    ctx.run(command)
    return filename


def get_s3_file_names(ctx):
    file_names = list()
    list_command = f'aws s3 ls {Constants.BACKUPS_BUCKET}'
    result = ctx.run(list_command, hide=True)
    if result.ok:
        lines = result.stdout.split(Constants.NEWLINE)
        for line in lines:
            split_line = line.split(Constants.SPACE)
            if len(split_line) > 1:
                file_names.append(split_line[len(split_line) - 1])
    return file_names


def get_latest_backup(ctx):
    files = get_s3_file_names(ctx)
    files.sort(reverse=True)
    return files[0]


def pull_from_s3(ctx):
    print('Pulling data from S3...')
    latest_backup = get_latest_backup(ctx)
    print(f'Downloading backup file {latest_backup}...')
    command = f'aws s3 cp {Constants.BACKUPS_BUCKET}/{latest_backup} ' \
              f'{latest_backup}'
    ctx.run(command, hide=True)
    return latest_backup


def unzip_backup_file(file_name):
    print(f'Unzipping backup {file_name}...')
    shutil.unpack_archive(file_name)


def pickle_data_exists(service_name):
    test_path = f'{service_name}.pickle'
    if os.path.exists(test_path):
        return True
    return False


def get_pickle_data(service_name, log=True):
    data_list = None
    test_path = f'{service_name}.pickle'
    if os.path.exists(test_path):
        if log:
            print(f'Reading pickle file for {service_name}...')
        with open(test_path, 'rb') as handle:
            data_list = pickle.load(handle)
    return data_list


def restore_service_data(service, endpoint=Constants.EMPTY):
    requestor = HttpRequestor()
    url = get_raw_service_url(service) + Constants.RESTORE_ROUTE
    if endpoint:
        url = get_raw_service_url(service) + endpoint
    print(f'Restoring data for service {url}...')
    file_path = \
        f'backup/{service}{endpoint.strip(Constants.FORWARD_SLASH)}.json'
    if os.path.exists(file_path):
        with open(file_path) as data_file:
            json_data = json.load(data_file)
            result = requestor.post(
                url, data=json.dumps(json_data),
                headers=requestor.get_request_headers())
            if result.status_code != Constants.CREATED_SUCCESS_CODE:
                print(f'Restore of {url} failed!')
                return
            print(f'Restore of {url} succeeded!')


@task
def restore(ctx):
    """ Restore data from our s3 backup location. """
    backup_file = pull_from_s3(ctx)
    unzip_backup_file(backup_file)
    restore_service_data(SLOS)
    restore_service_data(SLOS, Constants.DEBUG_ROUTE)
