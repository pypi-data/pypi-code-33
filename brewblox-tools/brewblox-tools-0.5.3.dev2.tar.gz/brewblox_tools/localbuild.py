#! /usr/bin/python3


from glob import glob as glob_
from os import getenv as getenv_
from os import remove as remove_
from subprocess import check_output as check_output_

from brewblox_tools import deploy_docker, distcopy
from dotenv import find_dotenv, load_dotenv

# Import various OS libraries as special name, to allow mocking them in unit tests
# Otherwise, pytest will break as it starts using mocked functions


def main():
    load_dotenv(find_dotenv(usecwd=True))

    name = getenv_('DOCKER_REPO')
    if not name:
        raise KeyError('Environment variable $DOCKER_REPO not found')

    context = getenv_('DOCKER_CONTEXT', 'docker')
    file = getenv_('DOCKER_FILE', 'amd/Dockerfile')
    branch = check_output_('git rev-parse --abbrev-ref HEAD'.split()).decode().rstrip()

    for f in glob_('dist/*'):
        remove_(f)

    sdist_result = check_output_('python setup.py sdist'.split()).decode()
    print(sdist_result)

    try:
        requirements = check_output_('pipenv lock --requirements'.split()).decode()
        with open(f'{context}/requirements.txt', 'w') as f:
            f.write(requirements)
    except Exception as ex:  # pragma: no cover
        print('Failed to copy Pipenv requirements: ', ex)

    distcopy.main('dist/ docker/dist/'.split())
    distcopy.main('config/ docker/config/'.split())
    deploy_docker.main([
        '--context', context,
        '--file', file,
        '--name', name,
        '--tags', branch,
        '--no-push'
    ])
