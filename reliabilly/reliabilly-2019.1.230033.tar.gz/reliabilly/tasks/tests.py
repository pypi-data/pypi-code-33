import os
from time import sleep
from invoke import task
from reliabilly.tasks.build import INVALID_SERVICE_MESSAGE
from reliabilly.tasks import docker, data
from reliabilly.components.integration.testing import run_service_integration_tests
from reliabilly.settings import Constants, Settings
from reliabilly.components.web.http_requestor import HttpRequestor

WAIT_TIME_SECONDS = 5
NAMEKO_RUN_CMD = 'nameko run {0}.service'
COMMON_TEST_CMD = 'pytest --ignore=reliabilly/tasks {flags} {service} --cov={service}'
DOCKER_PRINT_STATUS_CMD = 'docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}"'
DEFAULT_INT_TARGET = 'http://localhost:8080'


def test_service(ctx, service_name, times):
    os.environ[Constants.SERVICE_NAME_ENV] = service_name
    flags = ''
    if times:
        flags = '--durations=0'
    ctx.run(COMMON_TEST_CMD.format(service=service_name, flags=flags))


@task(optional=['service'])
def start(ctx, service):
    """ Run the app locally by service. """
    service_list = Settings.SERVICES
    if service not in service_list:
        print(INVALID_SERVICE_MESSAGE.format(service))
        return
    print(f'Setting service name to {service}...')
    os.environ[Constants.SERVICE_NAME_ENV] = service
    ctx.run(NAMEKO_RUN_CMD.format(service))


@task
def test(ctx, service=None, run_skipped=False, times=False):
    """ Run all unit tests """
    if run_skipped:
        os.environ[Constants.RUN_SKIPPED_ENV] = str(run_skipped)
    print(f"Running tests (skipped = {run_skipped})...")
    if service:
        test_service(ctx, service, times)
        return
    for service_test in Settings.TEST_MODULES:
        test_service(ctx, service_test, times)


def wait_for_service_health(ctx, service, sleep_time=10, retries=3):
    call_count = 1
    print(f'Waiting for {service} to be healthy...')
    healthy = docker.health(ctx, service)
    while not healthy:
        sleep(sleep_time)
        call_count += 1
        healthy = docker.health(ctx, service)
        if call_count > retries:
            return


def wait_for_local_service_ping(target, service, sleep_time=10, retries=3):
    call_count = 1
    requestor = HttpRequestor()
    print(f'Waiting for {service} ping to succeed...')
    ping_url = f'{target}/{service}/ping/'
    healthy = requestor.get(ping_url).status_code == Constants.SUCCESS_RESPONSE_CODE
    while not healthy:
        sleep(sleep_time)
        call_count += 1
        healthy = requestor.get(ping_url).status_code == Constants.SUCCESS_RESPONSE_CODE
        if call_count > retries:
            return


# noinspection PyBroadException
@task(optional=['target'])
def int_test(ctx, target=DEFAULT_INT_TARGET):
    """ Runs our integration tests. This assumes a running container stack. """
    print(f'Waiting for services to be ready...')
    sleep(WAIT_TIME_SECONDS)
    for service_name in Settings.SERVICES:
        try:
            if target == DEFAULT_INT_TARGET:
                wait_for_service_health(ctx, service_name)
                wait_for_local_service_ping(target, service_name)
                ctx.run(DOCKER_PRINT_STATUS_CMD)
            run_service_integration_tests(
                target, f'{service_name}/integration/')
        except Exception:  # pylint: disable=broad-except
            print(f'Tests failed for {service_name}')
            if target == DEFAULT_INT_TARGET:
                ctx.run(DOCKER_PRINT_STATUS_CMD)
            exit(1)


@task(optional=['target'], aliases=['int'])
def integration(ctx, target=DEFAULT_INT_TARGET):
    """ Bring up a fresh containerized environment and run the integration tests. """
    if target == DEFAULT_INT_TARGET:
        os.environ[Constants.AUTH_TOKEN] = Constants.DEV
        os.environ[Constants.VERSION_ENV] = Constants.DEV
        docker.down(ctx)
        docker.build(ctx)
        docker.up(ctx)
        data.load_test_data(ctx)
    int_test(ctx, target)
