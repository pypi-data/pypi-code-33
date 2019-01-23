import json
import pickle
from datetime import datetime
from os import path, environ
from boto3 import client
from invoke import task

PROD_ENV = 'prod'
UAT_ENV = 'uat'
UAT_REGION = 'us-west-2'
PROD_REGION = 'us-east-1'
SESSION_FILE_NAME = '.assumed_session'
DEVELOPER_SVC_ROLE = 'arn:aws:iam::640077214053:role/Developer'
ASSUME_ROLE_CMD = f'aws sts assume-role --role-arn {DEVELOPER_SVC_ROLE} ' \
                  f'--role-session-name debug'
UAT_CLUSTER_ARN = f'arn:aws:ecs:{UAT_REGION}:640077214053:cluster/' \
                   'reliabilly-ecs-cluster-uat'
PROD_CLUSTER_ARN = f'arn:aws:ecs:{PROD_REGION}:640077214053:cluster/' \
                   'reliabilly-ecs-cluster'
AWS_CLI_DESCRIBE_CLUSTER_CMD = \
    'aws ecs list-container-instances --cluster ' \
    '{cluster} --region {region} '
AWS_CLI_DESCRIBE_INSTANCES_CMD = \
    'aws ecs describe-container-instances --cluster ' \
    '{cluster} --region {region} --container-instances {instance_ids}'
AWS_DESCRIBE_INSTANCES_CMD = 'aws ec2 describe-instances ' \
                             '--instance-ids {instance_ids} --region {region}'
AWS_SSM_SEND_CMD = 'aws ssm send-command ' \
                   '--document-name "AWS-RunShellScript" --region {region}' \
                   ' --instance-ids {instance_ids} --parameters ' \
                   'commands="{command}" ' \
                   '--output text --query "Command.CommandId"'
AWS_SSM_RESULTS_CMD = 'aws ssm list-command-invocations --command-id ' \
                      '"{command_id}" --details --region {region}'


def get_instance_ids(ctx, env):
    instances = list()
    cluster, region = get_cluster_details(env)
    result = ctx.run(AWS_CLI_DESCRIBE_CLUSTER_CMD.format(
        cluster=cluster, region=region), hide=True).stdout
    instance_arns = ' '.join(json.loads(result)['containerInstanceArns'])
    instance_command = AWS_CLI_DESCRIBE_INSTANCES_CMD.format(
        cluster=cluster, region=region, instance_ids=instance_arns)
    result = json.loads(ctx.run(instance_command,
                                hide=True).stdout)['containerInstances']
    for instance in result:
        instance_id = instance['ec2InstanceId']
        instances.append(instance_id)
    return instances


def get_cluster_details(env):
    cluster = UAT_CLUSTER_ARN
    region = UAT_REGION
    if env != UAT_ENV:
        cluster = PROD_CLUSTER_ARN
        region = PROD_REGION
    return cluster, region


def get_instance_ips(ctx, env):
    ip_addresses = dict()
    _, region = get_cluster_details(env)
    instances = ' '.join(get_instance_ids(ctx, env))
    instance_command = AWS_DESCRIBE_INSTANCES_CMD.format(
        instance_ids=instances, region=region)
    result = json.loads(ctx.run(
        instance_command,
        hide=True).stdout)['Reservations']
    for instance in result:
        instance_id = instance['Instances'][0]['InstanceId']
        ip_address = instance['Instances'][0]['PrivateIpAddress']
        ip_addresses[instance_id] = ip_address
    return ip_addresses


def run_ssm_command(ctx, command, env):
    instances = ' '.join(get_instance_ids(ctx, env))
    _, region = get_cluster_details(env)
    command = AWS_SSM_SEND_CMD.format(
        instance_ids=instances, command=command, region=region)
    command_id = ctx.run(command, hide=True).stdout.strip()
    print(f'Command ID: {command_id}')
    result = json.loads(ctx.run(
        AWS_SSM_RESULTS_CMD.format(command_id=command_id, region=region),
        hide=True).stdout)['CommandInvocations']
    for instance in result:
        print(f'Instance ID: {instance["InstanceId"]}')
        print(instance['CommandPlugins'][0]['Output'])


def get_env(prod=False):
    if prod:
        return PROD_ENV
    return UAT_ENV


def get_mfa_serial():
    config_path = path.expanduser('~') + '/.aws/config'
    with open(config_path, 'r') as file:
        for line in file:
            if line.startswith('mfa_serial'):
                return line.split('=')[1].strip()
    return None


def get_assumed_credentials(token, duration=3600):
    mfa_serial = get_mfa_serial()
    response = client('sts').assume_role(
        DurationSeconds=duration,
        RoleArn=DEVELOPER_SVC_ROLE,
        RoleSessionName='debug', SerialNumber=mfa_serial, TokenCode=token)
    return response


def get_existing_session(token, duration):
    session_file_name = SESSION_FILE_NAME
    if path.exists(session_file_name):
        with open(session_file_name, 'rb') as session_file:
            session = pickle.load(session_file)
            expiration = session['Credentials']['Expiration']
            if datetime.now(expiration.tzinfo) < expiration:
                return session
    if not token:
        print('You need to send your MFA token with the assume call.')
        exit(1)
    return get_assumed_credentials(token, duration)


def update_existing_session(session):
    with open(SESSION_FILE_NAME, 'wb') as session_file:
        pickle.dump(session, session_file, pickle.HIGHEST_PROTOCOL)


def assume(token=None, duration=3600):
    response = get_existing_session(token, duration)
    aws_key = response['Credentials']['AccessKeyId']
    aws_secret = response['Credentials']['SecretAccessKey']
    aws_session = response['Credentials']['SessionToken']
    environ['AWS_ACCESS_KEY_ID'] = aws_key
    environ['AWS_SECRET_ACCESS_KEY'] = aws_secret
    environ['AWS_SESSION_TOKEN'] = aws_session
    environ['AWS_SECURITY_TOKEN'] = aws_session
    update_existing_session(response)


@task
def list_instance_ids(ctx, prod=False):
    assume()
    print(get_instance_ids(ctx, get_env(prod)))


@task
def list_ips(ctx, prod=False):
    assume()
    print(get_instance_ips(ctx, get_env(prod)))


@task
def list_container(ctx, service, all_containers=False, prod=False):
    assume()
    if all_containers:
        run_ssm_command(ctx, 'docker ps -a | grep {0}'.format(
            service), get_env(prod))
        return
    run_ssm_command(ctx, 'docker ps | grep {0}'.format(
        service), get_env(prod))


@task
def list_containers(ctx, all_containers=False, prod=False):
    assume()
    if all_containers:
        run_ssm_command(ctx, 'docker ps -a', get_env(prod))
        return
    run_ssm_command(ctx, 'docker ps', get_env(prod))


@task
def list_images(ctx, prod=False):
    assume()
    run_ssm_command(ctx, 'docker images', get_env(prod))


@task
def logs(ctx, service, prod=False):
    assume()
    run_ssm_command(ctx, 'docker logs --tail 35 {0}'.format(
        service), get_env(prod))


@task
def disk(ctx, prod=False):
    assume()
    run_ssm_command(ctx, 'df -H', get_env(prod))


@task
def uptime(ctx, prod=False):
    assume()
    run_ssm_command(ctx, 'uptime', get_env(prod))
