# pylint: disable=invalid-name,too-many-arguments
import json
import base64
from glob import glob
from os import path
import boto3
from invoke import task
from bs4 import BeautifulSoup
import yaml
from reliabilly.components.tools.data_monitoring_client import DataMonitoringClient
from reliabilly.components.tools.source_control_client import SourceControlClient
from reliabilly.components.tools.task_management_client import TaskManagementClient
from reliabilly.components.tools.version import check_versions
from reliabilly.components.web.http_requestor import HttpRequestor
from reliabilly.settings import Constants, Settings

GIT_CONTRIB_COMMAND = 'git log --pretty="%an"'
# The following is needed to avoid circular references.
BUILD_COMMAND = 'inv && inv int  && inv down'
# ----------------------------------------------------

ROLE_NAME = 'Developer'
ADD_SECRET_COMMAND = "aws secretsmanager create-secret --name '{secret_name}' --secret-string '{secret_value}' " \
                     "--kms-key-id '{kms_key}' --region '{aws_region}'"
UPDATE_SECRET_COMMAND = "aws secretsmanager update-secret --secret-id '{secret_name}' " \
                        "--secret-string '{secret_value}' --kms-key-id '{kms_key}' --region '{aws_region}'"
DELETE_SECRET_COMMAND = "aws secretsmanager delete-secret --secret-id '{secret_name}' --region '{aws_region}'"
CHECK_ROLE_COMMAND = f'aws iam get-role --role-name {ROLE_NAME}'
SECRET_PREFIX = 'reliabilly.'


@task
def build(ctx):
    """ Run the build command. """
    ctx.run(BUILD_COMMAND)


@task(pre=[build])
def pr(_):
    """ Submit a new pull request """


@task
def check_service_versions(_, version, sleep=Constants.DEFAULT_VERSION_TIMEOUT, target=Constants.DEFAULT_TARGET):
    """ Check the service endpoint versions. """
    match = check_versions(target, version, Settings.SERVICES, sleep)
    if not match:
        print('Version check failed!')
        exit(1)
    print('Version check succeeded!')


@task
def create_github_release(_, job_name, jira_num, jira_url, version, token):
    """ Create a new Github release """
    client = SourceControlClient(str(token))
    client.create_release(job_name, jira_num, jira_url, version)


@task
def create_release_event(_, release_number, release_status, release_environment, run_display_url, git_url, api_key):
    """ Create a new Release Event """
    client = DataMonitoringClient(api_key)
    client.create_event(release_number, release_status, release_environment, run_display_url, git_url)


@task
def close_work_ticket(_, base64auth, ticket_number):
    """ Close out a task management ticket """
    username, password = base64.b64decode(base64auth).decode(Constants.UTF8).split(Constants.COLON)
    client = TaskManagementClient(username, password)
    client.close_ticket(ticket_number)


@task
def add_secret(ctx, secret_id, secret_value, prod=False):
    """ Create a new secret in parameter store using our kms key. """
    run_secrets_command(ctx, ADD_SECRET_COMMAND, secret_id, secret_value, prod)


def encrypt_file(file_path, prod=False):
    kms_key = get_kms_key(prod)
    aws_region = get_env_region(prod)
    secrets = yaml.load(open(file_path))

    items = []
    for item in secrets['keys']:
        to_encrypt = item['value']
        encrypted = boto_encrypt(to_encrypt, kms_key, aws_region)
        item['value'] = encrypted
        items.append(item)

    secrets['keys'] = items

    with open(file_path, 'w') as outfile:
        yaml.dump(secrets, outfile, default_flow_style=False)


def toggle_secrets_in_file(file_path, prod=False, encrypt=True):
    aws_region = get_env_region(prod)
    kms_key = get_kms_key(prod)
    secrets = yaml.load(open(file_path))
    items = []
    for item in secrets['keys']:
        to_toggle = item['value']
        if encrypt:
            toggled = boto_encrypt(to_toggle, kms_key, aws_region)
        else:
            toggled = boto_decrypt(to_toggle, aws_region)
        item['value'] = toggled
        items.append(item)

    secrets['keys'] = items

    with open(file_path, 'w') as outfile:
        yaml.dump(secrets, outfile, default_flow_style=False)


def boto_encrypt(plaintext, kms_key, region):
    client = boto3.client('kms', region_name=region)
    response = client.encrypt(KeyId=kms_key, Plaintext=plaintext)
    output = response["CiphertextBlob"]
    return output


def boto_decrypt(encrypted, region):
    client = boto3.client('kms', region_name=region)
    response = client.decrypt(CiphertextBlob=encrypted)
    return response['Plaintext'].decode('UTF-8')


@task
def encrypt_secrets(ctx, service):
    """ Encrypt all yml files in the secrets directory and
    remove the non-encrypted versions for safety. """
    if not check_role_assumed(ctx):
        return
    for file in get_secrets_files(service):
        print(f'Encrypting file {file}...')
        prod = Constants.PROD in file
        toggle_secrets_in_file(file, prod, encrypt=True)


@task
def decrypt_secrets(ctx, service):
    """ Decrypt all yml files in the secrets directory to allow for edit. """
    if not check_role_assumed(ctx):
        return
    for file in get_secrets_files(service):
        print(f'Decrypting file {file}...')
        prod = Constants.PROD in file
        toggle_secrets_in_file(file, prod, encrypt=False)


def get_secrets_files(service):
    """Get the secrets files for a service or all"""
    current_dir = path.dirname(path.realpath(__file__))
    secrets_dir = path.join(current_dir, 'secrets')
    glob_dir = f'{secrets_dir}/*.yml'
    if service:
        glob_dir = f'{service}/secrets/*.yml'
    return glob(glob_dir, recursive=True)


@task
def update_secret(ctx, secret_id, secret_value, prod=False):
    """ Updates a secret in aws secrets manager. """
    if not check_role_assumed(ctx):
        return
    result = run_secrets_command(ctx, UPDATE_SECRET_COMMAND, secret_id, secret_value, prod, True)
    if not result:
        run_secrets_command(ctx, ADD_SECRET_COMMAND, secret_id, secret_value, prod)


@task
def update_service_secrets(ctx, service):
    if not check_role_assumed(ctx):
        return
    decrypt_secrets(ctx, service)
    for secret_file in get_secrets_files(service):
        if Constants.LOCAL in secret_file:
            # Skip local for now until we move to k8s
            continue
        prod = Constants.PROD in secret_file
        update_secrets_file(ctx, secret_file, prod)
    encrypt_secrets(ctx, service)


@task
def delete_secret(ctx, secret_id, prod=False):
    """ Deletes a secret from aws secrets manager. """
    region = get_env_region(prod)
    full_secret_id = get_secret_id(secret_id)
    command = DELETE_SECRET_COMMAND.format(aws_region=region, secret_name=full_secret_id)
    print(f'Deleting secret {full_secret_id}...')
    ctx.run(command)


@task
def wu(ctx):
    """ Generates the list of Wu-Tang names based on project contributors."""
    names = get_contributors(ctx)
    wu_list = list()
    for name in names:
        wu_name = get_wu_name(name)
        wu_list.append(wu_name)
    encoded_wu = get_encoded_wu_names(wu_list)
    print(json.dumps(encoded_wu))


@task
def wu_me(_, name):
    """ Find out what your wu-tang name and auth token will be. """
    wu_name = get_wu_name(name)
    wu_encoded = get_wu_encoded_name(wu_name)
    print(f'Your wu-tang name is: {wu_name}')
    print(f'Your auth token is: {wu_encoded}')


def update_secrets_file(ctx, secrets_file, prod=False):
    environment = Constants.UAT
    if prod:
        environment = Constants.PROD
    with open(secrets_file, Constants.READ_ONLY) as secret_file:
        secret_config = yaml.load(secret_file)
        print(f'Adding secrets from {secrets_file}...')
        for item in secret_config['keys']:
            print(f'Updating secret {item[Constants.NAME]} for {environment}')
            update_secret(ctx, item[Constants.NAME], item[Constants.VALUE], prod)


def check_role_assumed(ctx):
    try:
        ctx.run(CHECK_ROLE_COMMAND, hide=True)
        return True
    except Exception:  # pylint: disable=broad-except
        print('You must have an active assumed role to run this command!')
    return False


def get_secret_id(secret_id):
    full_secret_id = secret_id
    if SECRET_PREFIX not in secret_id:
        full_secret_id = f'{SECRET_PREFIX}{secret_id}'
    return full_secret_id


def run_secrets_command(ctx, command, secret_id, secret_value, prod=False, update=False):
    region = get_env_region(prod)
    kms_key = get_kms_key(prod)
    full_secret_id = get_secret_id(secret_id)
    command = command.format(aws_region=region, secret_name=full_secret_id, secret_value=secret_value, kms_key=kms_key)
    message = get_log_message(update, full_secret_id)
    print(message)
    return ctx.run(command, hide=True, warn=True).ok


def get_log_message(update, secret_id):
    message = f'Adding secret {secret_id}...'
    if update:
        message = f'Updating secret {secret_id}...'
    return message


def get_kms_key(prod=False):
    if prod:
        return Constants.KMS_KEYS[Constants.PROD_REGION]
    return Constants.KMS_KEYS[Constants.UAT_REGION]


def get_wu_name(name):
    wu_name = 'Unknown'
    url = f'https://wunameaas.herokuapp.com/wuami/{name}'
    web_client = HttpRequestor()
    result = web_client.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')
    for bold_item in soup.find_all('b'):
        wu_name = bold_item.get_text()
    return wu_name


def get_wu_encoded_name(name):
    return str(base64.b64encode(name.encode()), Constants.UTF8)


def get_encoded_wu_names(wu_names):
    encoded_list = list()
    for name in wu_names:
        encoded_list.append(get_wu_encoded_name(name))
    return encoded_list


def get_contributors(ctx):
    names = list()
    result = ctx.run(GIT_CONTRIB_COMMAND, hide=True).stdout
    for line in result.split(Constants.NEWLINE):
        name = line.lower().replace(Constants.HYPHEN, Constants.SPACE)
        if name:
            if name not in names:
                names.append(name)
    return names


def get_env_region(prod):
    if prod:
        return Constants.PROD_REGION
    return Constants.UAT_REGION


@task
def send_build_metrics(_, step, state, token, build_tag):
    return call_velocity_endpoint(step, state, token, build_tag)


def call_velocity_endpoint(step, state, token, build_tag, web_client=HttpRequestor()):
    url = build_velocity_url(step, state, token, build_tag)
    result = web_client.post(url)
    return result.status_code


def build_velocity_url(step, state, token, build_tag):
    """Builds a URL for Developer Velocity"""
    full_url = f'{Settings.DV_URL}{token}/{build_tag}/{state}/{step}'
    print(full_url)
    return full_url
