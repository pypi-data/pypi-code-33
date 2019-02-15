"""
Like kubectl apply except for hipsters with bare ssh and dedicated machines.
"""

import cli2
import copy
import dsnparse
import json
import os
import pathlib
import re
import requests
import shlex
import subprocess
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


@cli2.command(color=cli2.RED)
def write_ssh_private_key():
    """Write $SSH_PRIVATE_KEY to ~/.ssh/id_ed25519."""
    if 'SSH_PRIVATE_KEY' not in os.environ:
        return 'Could not get $SSH_PRIVATE_KEY'

    path = pathlib.Path(os.getenv('HOME')) / '.ssh'
    if not os.path.exists(path):
        os.makedirs(path)
    target = path / 'id_ed25519'
    content = os.getenv('SSH_PRIVATE_KEY')
    with open(target, 'w+') as fh:
        fh.write(content.strip() + '\n')
        print('Wrote', target)
    os.chown(target, os.getuid(), -1)
    os.chmod(target, 0o700)
    return target


@cli2.command(name='apply')
def playbook():
    """Apply docker-compose file on the given dsn."""
    if ('v' in console_script.parser.dashargs
        or 'vv' in console_script.parser.dashargs):
        os.environ['ANSIBLE_STDOUT_CALLBACK'] = 'debug'

    services = dict()
    prefix = os.getenv('ansible_compose_prefix')
    composes_new = []
    for num, compose_src in enumerate(console_script.composes):
        name_src = compose_src.split('/')[-1]
        name_new = 'ansible-compose.' + str(num) + '.' + name_src
        if compose_src.startswith('http'):
            content_src = requests.get(compose).content
        else:
            with open(compose_src, 'r') as fh:
                content_src = fh.read()

        content_new = compose_generate(content_src, os.environ, prefix)

        # consolidate a list of services to feed the playbook with
        for service, data in content_new.get('services', {}).items():
            if service not in services:
                services[service] = data

        with open(name_new, 'w+') as fh:
            fh.write(yaml.dump(content_new))
            print('Wrote', name_new)
        path_new = os.path.join(os.getcwd(), name_new)
        composes_new.append((path_new, name_src))

    argv = console_script.ansible_argv
    argv += ['--extra-vars', json.dumps(dict(
        composes=composes_new, services=services
    ))]

    argv.append(f'--inventory={console_script.host},')
    if console_script.host == 'localhost':
        argv += ['-c', 'local']
    else:
        write_ssh_private_key()

    argv += ['-e', f'path={console_script.path}']

    if console_script.dsn.username:
        argv.append(f'--user={console_script.dsn.username}')

    argv.append(os.path.join(os.path.dirname(__file__), 'playbook.yml'))
    print(' '.join(['ansible-playbook'] + argv))
    os.execvpe('ansible-playbook', ['ansible-playbook'] + argv, os.environ)


def compose(command='up'):
    argv = ' '.join(console_script.parser.argv_all)

    if console_script.host == 'localhost':
        subprocess.call(
            f"bash -xc 'pushd {console_script.path}; docker-compose {argv}; popd'",
            shell=True,
        )
    else:
        write_ssh_private_key()
        args = [
            'ssh',
            '@'.join([console_script.user, console_script.host]),
            f"bash -euxc 'cd {console_script.path}; docker-compose {argv}'"
        ]
        print('Running', ' '.join(args))
        os.execvpe('ssh', args, os.environ)



class ConsoleScript(cli2.ConsoleScript):
    compose_commands = dict(
        build   = 'Build or rebuild services',
        bundle  = 'Generate a Docker bundle from the Compose file',
        config  = 'Validate and view the Compose file',
        create  = 'Create services',
        down    = 'Stop and remove containers, networks, images, and volumes',
        events  = 'Receive real time events from containers',
        exec    = 'Execute a command in a running container',
        images  = 'List images',
        kill    = 'Kill containers',
        logs    = 'View output from containers',
        pause   = 'Pause services',
        port    = 'Print the public port for a port binding',
        ps      = 'List containers',
        pull    = 'Pull service images',
        push    = 'Push service images',
        restart = 'Restart services',
        rm      = 'Remove stopped containers',
        run     = 'Run a one-off command',
        scale   = 'Set number of containers for a service',
        start   = 'Start services',
        stop    = 'Stop services',
        top     = 'Display the running processes',
        unpause = 'Unpause services',
        up      = 'Create and start containers',
        version = 'Show the Docker-Compose version information',
    )

    def __init__(self, *args, **kwargs):
        self.add_commands(playbook)
        self.compose_commands_add()
        super().__init__(*args, **kwargs)

    def compose_commands_add(self):
        commands = []
        def _cmd(name, doc):
            @cli2.command(name=name)
            def cmd(dsn=None):
                compose(cmd.__name__)
            cmd.__doc__ = doc
            cmd.__name__ = name
            return cmd

        for name, doc in self.compose_commands.items():
            cmd = _cmd(name, doc)
            commands.append(cmd)
        self.add_commands(*commands)

        self.add_commands(write_ssh_private_key)

    def call(self, command):
        self.dsn = dsnparse.ParseResult('ssh://' + os.getenv('dsn', 'localhost'))
        self.host = self.dsn.hostname
        self.path = self.dsn.path or os.getcwd()
        self.user = self.dsn.username or os.getenv('USER')

        self.composes = []
        pops = []
        self.ansible_argv = copy.copy(console_script.parser.argv)
        for num, arg in enumerate(self.ansible_argv):
            if arg == '-f':
                self.composes.append(self.ansible_argv[num + 1])
                pops += [num, num + 1]

            elif arg.startswith('--file'):
                if '=' in arg:
                    self.composes.append(arg.split('=')[1])
                    pops += [num]
                else:
                    self.composes.append(self.ansible_argv[num + 1])
                    pops += [num, num + 1]

        for num in reversed(pops):
            self.ansible_argv.pop(num)

        return super().call(command)

console_script = ConsoleScript(
    __doc__,
    default_command='help'
)
