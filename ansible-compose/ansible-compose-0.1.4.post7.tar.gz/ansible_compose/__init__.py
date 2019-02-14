"""
Like kubectl apply except for hipsters with bare ssh and dedicated machines.
"""

import cli2
import dsnparse
import json
import os
import pathlib
import re
import requests
import shlex
import yaml


def compose_generate(src, patches, prefix=None):
    if isinstance(src, (str, bytes)):
        src = yaml.load(src)

    for service, options in src['services'].items():
        if 'build' in options:
            options.pop('build')

    def name_set(services, match, value):
        services[match.group('service')].setdefault(match.group('key'), dict())
        services[match.group('service')][match.group('key')][match.group('name')] = value

    def key_set(services, match, value):
        services[match.group('service')][match.group('key')] = value

    def service_drop(services, match, value):
        del services[match.group('service')]

    def key_drop(services, match, value):
        del services[match.group('service')][match.group('key')]

    def name_drop(services, match, value):
        del services[match.group('service')][match.group('key')][match.group('name')]

    accepted_keys = ['env_file', 'environment', 'volumes', 'image']
    pattern_service = f'(?P<service>{"|".join(src.get("services", dict()).keys())})'
    pattern_key = f'(?P<key>{"|".join(accepted_keys)})'
    pattern_name = '(?P<name>.*)'

    patterns = {
        '_'.join([
            pattern_service,
            pattern_key,
            pattern_name,
        ]): name_set,
        '_'.join([
            pattern_service,
            pattern_key,
        ]): key_set,
        '_'.join([
            'drop',
            pattern_service,
            pattern_key,
            pattern_name,
        ]): name_drop,
        '_'.join([
            'drop',
            pattern_service,
            pattern_key,
        ]): key_drop,
        '_'.join([
            'drop',
            pattern_service,
        ]): service_drop,
    }

    for name, value in patches.items():
        for pattern, cb in patterns.items():
            match = re.match(f'{prefix}_{pattern}' if prefix else pattern, name)
            if not match:
                continue

            cb(src['services'], match, value)
            break

    return src


@cli2.option('update', help='Skip setup task (for CI)', alias='u')
def apply(dsn, compose):
    if compose.startswith('http'):
        compose = requests.get(compose).content
    else:
        with open(compose, 'r') as fh:
            compose = fh.read()

    prefix = os.getenv('ansible_compose_prefix')
    final = compose_generate(compose, os.environ, prefix)

    with open('ansible-compose.yml', 'w+') as fh:
        fh.write(yaml.dump(final))

    dsn = dsnparse.ParseResult('ssh://' + dsn)
    args = console_script.parser.extraargs

    if 'SSH_PRIVATE_KEY' in os.environ:
        path = pathlib.Path(os.getenv('HOME')) / '.ssh'
        if not os.path.exists(path):
            os.makedirs(path)
        target = path / 'id_ed25519'
        with open(target, 'w+') as fh:
            fh.write(os.getenv('SSH_PRIVATE_KEY'))
        os.chown(target, os.getuid(), -1)
        os.chmod(target, 0o700)
        args.append('--private-key=' + str(target))


    if 'v' in console_script.parser.dashargs or 'vv' in console_script.parser.dashargs:
        os.environ['ANSIBLE_STDOUT_CALLBACK'] = 'debug'
    args.append(f'--inventory={dsn.hostname},')
    if dsn.path:
        args += [f'-e', 'path={dsn.path}']
    if dsn.username:
        args.append(f'--user={dsn.username}')
    args += ['-e', 'services=' + shlex.quote(json.dumps(final['services']))]
    args += ['-e', f'compose={os.getcwd()}/ansible-compose.yml']
    args += ['-e', 'ansible_python_interpreter=/usr/bin/python3']
    args.append(os.path.join(os.path.dirname(__file__), 'playbook.yml'))
    print(' '.join(['ansible-playbook'] + args))
    os.execvpe('ansible-playbook', ['ansible-playbook'] + args, os.environ)


def run(dsn, command_or_compose):
    if command_or_compose.endswith('.yml'):
        apply(dsn, command_or_compose)
    else:
        dsn = dsnparse.ParseResult('ssh://' + dsn)
        args = [
            'ssh',
            '@'.join([dsn.username, dsn.host]),
            f"bash -euxc 'cd {dsn.path}; docker-compose {command_or_compose}'"
        ]
        print('Running', ' '.join(args))
        os.execvpe('ssh', args, os.environ)


console_script = cli2.ConsoleScript(
    __doc__,
    default_command='run'
).add_commands(run, apply, cli2.help)
