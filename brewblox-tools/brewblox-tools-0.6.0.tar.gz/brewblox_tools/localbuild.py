#! /usr/bin/python3


import argparse
import re
from glob import glob
from os import getenv, remove
from subprocess import STDOUT, check_call, check_output

from dotenv import find_dotenv, load_dotenv

from brewblox_tools import distcopy

# Import various OS libraries as special name, to allow mocking them in unit tests
# Otherwise, pytest will break as it starts using mocked functions


def parse_args(sys_args: list = None):
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--arch',
                        help='Build these architectures. [%(default)s]',
                        default=['amd'],
                        nargs='+',
                        choices=['amd', 'arm'])
    parser.add_argument('-r', '--repo',
                        help='Docker repository name. [%(default)s]',
                        default=getenv('DOCKER_REPO'))
    parser.add_argument('-c', '--context',
                        help='Build context. [%(default)s]',
                        default='docker')
    parser.add_argument('-f', '--file',
                        help='Filename inside context. [%(default)s]',
                        default='Dockerfile')
    parser.add_argument('-t', '--tags',
                        help='Additional tags. The "local" tag is always built.',
                        nargs='+',
                        default=[])
    parser.add_argument('--branch-tag',
                        help='Use sanitized branch name as tag. ' +
                        'ARM automatically gets the "rpi-" prefix. [%(default)s]',
                        action='store_true')
    parser.add_argument('--pull',
                        help='Pull base images. [%(default)s]',
                        action='store_true')
    parser.add_argument('--push',
                        help='Push all tags except "local" to Docker Hub. [%(default)s]',
                        action='store_true')

    return parser.parse_args(sys_args)


def run(cmd: str):
    print(cmd)
    check_call(cmd, shell=True, stderr=STDOUT)


def main(sys_args: list = None):
    load_dotenv(find_dotenv(usecwd=True))
    args = parse_args(sys_args)
    tags = args.tags.copy()

    if args.branch_tag:
        tags.append(getenv('TRAVIS_BRANCH')
                    or check_output('git rev-parse --abbrev-ref HEAD'.split()).decode().rstrip())

    tags = [re.sub('[/_:]', '-', tag) for tag in tags]

    for f in glob('dist/*'):
        remove(f)

    run('python setup.py sdist')
    run(f'pipenv lock --requirements > {args.context}/requirements.txt')
    distcopy.main(f'dist/ {args.context}/dist/'.split())
    distcopy.main(f'config/ {args.context}/config/'.split())

    for arch in args.arch:
        prefix = ''
        commands = []
        build_args = []
        build_tags = [
            'local',
            *tags
        ]

        if arch == 'arm':
            prefix = 'rpi-'
            commands += [
                'docker run --rm --privileged multiarch/qemu-user-static:register --reset',
            ]

        if args.pull:
            build_args.append('--pull')

        build_args += [
            '--no-cache',
            ' '.join([f'--tag {args.repo}:{prefix}{t}' for t in build_tags]),
            f'--file {args.context}/{arch}/{args.file}',
            args.context,
        ]

        commands.append(f'docker build {" ".join(build_args)}')
        run(' && '.join(commands))

        if args.push:
            # We're skipping the local tag
            [run(f'docker push {args.repo}:{prefix}{t}') for t in tags]


if __name__ == '__main__':
    main()
