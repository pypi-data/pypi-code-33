import json
from invoke import task
from reliabilly.tasks.debug import get_cluster_details, get_env
from reliabilly.settings import Settings, Constants, get_compose_environment

EMPTY = ''
ACCOUNT_NUMBER = '777777777777'
IMAGE_PREFIX = 'reliabilly/'
DEFAULT_ECR_REGION = 'us-west-2'
DEFAULT_ECR_REPO = f'{ACCOUNT_NUMBER}.dkr.ecr.us-west-2.amazonaws.com'
DEFAULT_TASK_ROLE_ARN = f'arn:aws:iam::{ACCOUNT_NUMBER}:role/task-role'
DOCKER_ECR_LOGIN_CMD = 'aws ecr get-login --no-include-email --region us-west-2'
DOCKER_TEST_CMD = 'docker ps | grep CONTAINER'
DOCKER_MESSAGE = 'Docker is required and needs to be running.'
DOCKER_COMPOSE_UP_CMD = f'docker-compose {Settings.COMPOSE_FLAGS} up -d'
DOCKER_COMPOSE_DOWN_CMD = f'docker-compose {Settings.COMPOSE_FLAGS}  down --remove-orphans'
DOCKER_COMPOSE_LOGS_CMD = f'docker-compose {Settings.COMPOSE_FLAGS} logs'
DOCKER_COMPOSE_LOGS_TAIL_CMD = f'docker-compose {Settings.COMPOSE_FLAGS} logs -f'
DOCKER_COMPOSE_SERVICE_LOGS_CMD = '{command} {service}'
DOCKER_BUILD_CMD = 'docker build {3} {1} -t {0}{1}:{2}'
DOCKER_BUILD_AGENT_CMD = 'docker build {0} -t {1} .'
DOCKER_TAG_CMD = 'docker tag {0} {1}'
CREATE_ECR_REPO_CMD = 'aws ecr create-repository --repository-name {repo_name} --region {region}'
ECR_EXISTS_CMD = 'aws ecr describe-repositories --repository-names {repo_name} --region {region}'
DOCKER_PUSH_CMD = 'docker push {0}'
DOCKER_EXEC_CMD = 'docker exec -it {0} sh'
DOCKER_GET_ID_BY_NAME = 'docker ps -q -f name={0}'
DOCKER_PS_CMD = 'docker ps'
DOCKER_PSA_CMD = 'docker ps -a'
DOCKER_LIST_CMD = 'docker ps -q'
DOCKER_LIST_ALL_CMD = 'docker ps -a -q'
DOCKER_IMAGES_CMD = 'docker images'
DOCKER_IMAGES_LIST_ALL_CMD = 'docker images -q'
DOCKER_IMAGES_LIST_CMD = 'docker images -q'
DOCKER_STOP_CMD = 'docker stop {0}'
DOCKER_RM_CMD = 'docker rm {0}'
DOCKER_RMI_CMD = 'docker rmi --force {0}'
DOCKER_VOLUME_PRUNE_CMD = 'docker volume prune -f'
DOCKER_NETWORK_PRUNE_CMD = 'docker network prune -f'
DOCKER_LIST_DANGLING = 'docker images -f "dangling=true" -q'
DOCKER_BUILD_ARGS = ''
DEFAULT_ECS_FAMILY = '{service}'
ECS_REGISTER_TASK_CMD = 'aws ecs register-task-definition --family {family} -task-role-arn {task_role} ' \
                        "--container-definitions '{task_def}'"
ECS_RUN_TASK_CMD = 'aws ecs run-task --cluster {cluster} --task-definition {task_def} --count {count}'
COMMON_TAG_LOCAL = f'{IMAGE_PREFIX}reliabilly:latest'
COMMON_TAG_LOCAL_VERSION = f'{IMAGE_PREFIX}reliabilly:latest'
COMMON_IMAGE = f'{DEFAULT_ECR_REPO}/{COMMON_TAG_LOCAL}'
COMMON_IMAGE_VERSION = f'{DEFAULT_ECR_REPO}/{COMMON_TAG_LOCAL_VERSION}'
DOCKER_PULL_COMMON_CMD = f'docker pull {COMMON_IMAGE}'
DOCKER_PULL_COMMON_VERSION_CMD = f'docker pull {COMMON_IMAGE_VERSION}'
DOCKER_TAG_COMMON_CMD = f'docker tag {COMMON_IMAGE} {COMMON_TAG_LOCAL}'
DOCKER_TAG_COMMON_VERSION_CMD = f'docker tag {COMMON_IMAGE} {COMMON_TAG_LOCAL_VERSION}'
DOCKER_BUILD_COMMON_CMD = f'docker build . -t {COMMON_TAG_LOCAL}'
DOCKER_BUILD_IMAGE_CMD = 'docker build {0} -t {1}'
DOCKER_TAG_ECR_COMMON_CMD = f'docker tag {COMMON_TAG_LOCAL} {COMMON_IMAGE}'
DOCKER_TAG_ECR_COMMON_VERSION_CMD = f'docker tag {COMMON_TAG_LOCAL} {COMMON_IMAGE_VERSION}'
DOCKER_PUSH_COMMON_CMD = f'docker push {COMMON_IMAGE}'
DOCKER_HEALTH_CMD = 'docker inspect --format "{{json .State.Health }}"'
DOCKER_PUSH_COMMON_VERSION_CMD = f'docker push {COMMON_IMAGE_VERSION}'


@task(aliases=['dangling'])
def rmd(ctx):
    """ Remove dangling images from builds with NONE names. """
    print('Removing dangling docker images...')
    run_docker_batch(ctx, DOCKER_LIST_DANGLING, DOCKER_RMI_CMD)


@task(optional=['prefix', 'ecr_repo', 'tag'])
def build(ctx, prefix=IMAGE_PREFIX, ecr_repo=None, tag='latest'):
    """ Run Docker image build for all of our container images. """
    print('Building docker images...')
    docker_args = EMPTY
    if ecr_repo:
        docker_args = DOCKER_BUILD_ARGS
    for svc in Settings.SERVICES:
        ctx.run(DOCKER_BUILD_CMD.format(
            prefix, svc, tag, docker_args))
        if ecr_repo and prefix:
            source_tag = f'{prefix}{svc}:{tag}'
            destination_tag = f'{ecr_repo}/{source_tag}'
            ctx.run(DOCKER_TAG_CMD.format(source_tag, destination_tag))


def run_docker_batch(ctx, list_command, action_command):
    all_containers = ctx.run(list_command).stdout.split('\n')
    for container in all_containers:
        if container.strip():
            ctx.run(action_command.format(container))


@task
def health(ctx, service):
    """ Check the health status of a specified container by service name. """
    try:
        container = ctx.run(DOCKER_GET_ID_BY_NAME.format(service), hide=True).stdout
        result = ctx.run(f'{DOCKER_HEALTH_CMD} {container}', hide=True).stdout
        json_result = json.loads(result)
        health_status = json_result.get('Status', Constants.EMPTY)
        print(f'{service}: {health_status}')
        return health_status == 'healthy'
    except Exception:  # pylint: disable=broad-except
        return False


@task
def ps(ctx):  # pylint: disable=invalid-name
    """ Run the docker ps command from within our invoke tasks. """
    ctx.run(DOCKER_PS_CMD)


@task
def psa(ctx):
    """ Run the docker ps -a command from within our invoke tasks. """
    ctx.run(DOCKER_PSA_CMD)


@task(optional=['all_containers'])
def stop(ctx, all_containers=False):
    """ Run the docker stop command from within our invoke tasks. """
    if all_containers:
        run_docker_batch(ctx, DOCKER_LIST_ALL_CMD, DOCKER_STOP_CMD)
        return
    run_docker_batch(ctx, DOCKER_LIST_ALL_CMD, DOCKER_STOP_CMD)


@task(optional=['all_containers'])
def rm(ctx, all_containers=False):  # pylint: disable=invalid-name
    """ Run the docker rm command from within our invoke tasks. """
    if all_containers:
        run_docker_batch(ctx, DOCKER_LIST_ALL_CMD, DOCKER_RM_CMD)
        return
    run_docker_batch(ctx, DOCKER_LIST_ALL_CMD, DOCKER_RM_CMD)


@task(optional=['all_images'])
def images(ctx, all_images=False):
    """ Run the docker images command from within our invoke tasks. """
    if all_images:
        ctx.run(DOCKER_IMAGES_CMD)
        return
    ctx.run(DOCKER_IMAGES_CMD)


@task(optional=['all_images'])
def rmi(ctx, all_images=False):
    """ Run the docker rmi command from within our invoke tasks. """
    if all_images:
        run_docker_batch(ctx, DOCKER_IMAGES_LIST_ALL_CMD, DOCKER_RMI_CMD)
        return
    run_docker_batch(ctx, DOCKER_IMAGES_LIST_CMD, DOCKER_RMI_CMD)


@task
def sh(ctx, service):  # pylint: disable=invalid-name
    """ Connects to a shell inside one of our service containers. """
    container_id = ctx.run(DOCKER_GET_ID_BY_NAME.format(service)).stdout.strip()
    if container_id:
        ctx.run(DOCKER_EXEC_CMD.format(container_id), pty=True)


@task
def prune(ctx):
    """ Prunes unused docker volumes and networks. """
    print('Pruning unused docker volumes...')
    ctx.run(DOCKER_VOLUME_PRUNE_CMD)
    print('Pruning unused docker networks...')
    ctx.run(DOCKER_NETWORK_PRUNE_CMD)


@task(post=[stop, rm, rmi, prune])
def purge(_):
    """ Purge all docker containers and images. """
    print("Purging docker containers and images...")


@task
def clear(ctx):
    """ Purge all docker containers and images. """
    print("Purging ALL docker containers and images...")
    stop(ctx, all_containers=True)
    rm(ctx, all_containers=True)
    rmi(ctx, all_images=True)


@task
def login(ctx):
    """ Login to the ECR repository in AWS. """
    result = ctx.run(DOCKER_ECR_LOGIN_CMD).stdout
    ctx.run(result)


@task(optional=['ecr_repo'], pre=[login])
def push(ctx, tag, ecr_repo=DEFAULT_ECR_REPO):
    """ Push the docker images to our ECR repository in AWS. """
    build(ctx, IMAGE_PREFIX, ecr_repo, tag)
    for svc in Settings.SERVICES:
        create_ecr_repository(ctx, svc)
        image = f'{ecr_repo}/{IMAGE_PREFIX}{svc}:{tag}'
        print(f'Pushing {image}...')
        print(DOCKER_PUSH_CMD.format(image))
        ctx.run(DOCKER_PUSH_CMD.format(image))


@task(pre=[login])
def pull_common(ctx):
    """ Pull the common container image from our ecr repository. """
    ctx.run(DOCKER_PULL_COMMON_CMD)
    ctx.run(DOCKER_TAG_COMMON_CMD)


@task
def build_common(ctx):
    """ Build the common container image from source. """
    ctx.run(DOCKER_BUILD_COMMON_CMD)


@task
def build_image(ctx, path, name):
    """ Build a docker container image from specified path with name. """
    ctx.run(DOCKER_BUILD_IMAGE_CMD.format(path, name))


@task(pre=[login])
def push_common(ctx):
    """ Push the common container image up to our ecr repository. """
    build_common(ctx)
    ctx.run(DOCKER_TAG_ECR_COMMON_CMD)
    ctx.run(DOCKER_TAG_ECR_COMMON_VERSION_CMD)
    ctx.run(DOCKER_PUSH_COMMON_CMD)
    ctx.run(DOCKER_PUSH_COMMON_VERSION_CMD)


@task
def create_ecr_repository(ctx, svc):
    """ Create a docker container registry in ecr for a specified service. """
    repo_name = f'{IMAGE_PREFIX}{svc}'
    repo_exists = check_repo_exists(ctx, repo_name)
    if not repo_exists:
        print(f'Creating ecr repo {repo_name}...')
        ctx.run(CREATE_ECR_REPO_CMD.format(repo_name=repo_name, region=DEFAULT_ECR_REGION))


def check_repo_exists(ctx, repo_name):
    # pylint: disable=broad-except
    try:
        ctx.run(ECR_EXISTS_CMD.format(repo_name=repo_name, region=DEFAULT_ECR_REGION), hide=True)
        print(f'{repo_name} already exists so skipping...')
        return True
    except Exception:
        return False


@task(pre=[build])
def up(ctx):  # pylint: disable=invalid-name
    """ Run Docker compose up which brings up the compose stack. """
    get_compose_environment()
    ctx.run(DOCKER_COMPOSE_UP_CMD)


@task()
def raw(ctx):
    """ Run Docker compose up which brings up the compose stack.
    RISKY AS NO BUILD FIRST SO USE AT RISK"""
    get_compose_environment()
    ctx.run(DOCKER_COMPOSE_UP_CMD)


@task
def down(ctx):
    """ Run Docker compose down to bring down the compose stack. """
    get_compose_environment()
    ctx.run(DOCKER_COMPOSE_DOWN_CMD)


@task(optional=['service'])
def logs(ctx, service):
    """ Run Docker compose logs with optional service name. """
    get_compose_environment()
    if service:
        ctx.run(DOCKER_COMPOSE_SERVICE_LOGS_CMD.format(command=DOCKER_COMPOSE_LOGS_CMD, service=service))
        return
    ctx.run(DOCKER_COMPOSE_LOGS_CMD)


@task(optional=['service'])
def tail(ctx, service=None):
    """ Run Docker compose logs with the -f follow or tail option. """
    get_compose_environment()
    if service:
        ctx.run(DOCKER_COMPOSE_SERVICE_LOGS_CMD.format(command=DOCKER_COMPOSE_LOGS_TAIL_CMD, service=service))
        return
    ctx.run(DOCKER_COMPOSE_LOGS_TAIL_CMD)


def register_ecs_task(ctx, service):
    task_definition = get_task_definition(service, 'dev', '123', '1')
    task_family = DEFAULT_ECS_FAMILY.format(service=service)
    command = ECS_REGISTER_TASK_CMD.format(
        service=service, family=task_family, task_def=task_definition, task_role=DEFAULT_TASK_ROLE_ARN)
    print(f'Creating ECS task definition for {service}...')
    result = ctx.run(command, hide=True).stdout
    result_json = json.loads(result)
    task_arn = result_json['taskDefinition']['taskDefinitionArn']
    print(f'ECS task for {service} registered. ARN: {task_arn}')
    return task_arn


def deploy_ecs_task(ctx, service, count=1, prod=False):
    cluster = get_cluster_details(get_env(prod))
    task_arn = register_ecs_task(ctx, service)
    command = ECS_RUN_TASK_CMD.format(
        cluster=cluster, count=count, task_def=task_arn)
    print(f'Running ECS task for {service}...')
    result = ctx.run(command, hide=True).stdout
    result_json = json.loads(result)
    print(result_json)
    print(f'ECS task for {service} started.')


def get_task_definition(service, environment, tag, build_number):
    with open(f'{service}/ecs/svc_{service}.json') as task_def:
        task_string = task_def.read().replace('${registry}', DEFAULT_ECR_REPO).replace(
            '${image_tag}', tag).replace('${environment}', environment).replace(
                '${aws_region}', DEFAULT_ECR_REGION).replace('${build_number}', build_number)
        json_def = json.loads(task_string)
        return json.dumps(json_def)


@task(optional=['service'])
def deploy(ctx, service):
    """ Deploy docker container(s) to our cluster. """
    if service:
        deploy_ecs_task(ctx, service)
        return
    for svc in Settings.COMPOSE_LIST:
        deploy_ecs_task(ctx, svc)


@task
def clean(ctx):
    """ Clean up unused docker resources such as
    dangling containers and volumes."""
    rmd(ctx)
    prune(ctx)
