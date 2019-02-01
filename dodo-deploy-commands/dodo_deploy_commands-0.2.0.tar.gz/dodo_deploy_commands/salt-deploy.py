from argparse import ArgumentParser
from dodo_commands.framework import Dodo, DecoratorScope, ConfigArg
import os
import uuid
from ._utils import (run_ssh_server, commit_ssh_server)


def _args():  # noqa
    parser = ArgumentParser(
        description=('Deploys a salt script to a ssh server'))
    parser.add_argument(
        "--debug", action="store_true", help='Only apply the debug.sls state')
    parser.add_argument(
        "--verbose",
        action="store_true",
        help='Print the generated Salt master and roster file to the screen')
    parser.add_argument(
        "--bash",
        action="store_true",
        help='Drop into a bash shell instead of calling salt')

    args = Dodo.parse_args(
        parser,
        config_args=[
            ConfigArg(
                '/SALT/src_dir',
                'salt_src_dir',
                help='Root directory of the salt script'),
            ConfigArg(
                '/SALT/target_docker_image',
                'target_docker_image',
                default=None,
                help='Name of the Docker image that is the deploy target'),
            ConfigArg(
                '/SALT/host_name',
                'host_name',
                help='Name of the targeted server in the Salt script'),
            ConfigArg(
                '/SALT/top_dir',
                '--top-dir',
                default='.',
                help='Root directory of the salt script'),
            ConfigArg(
                '/SSH/key_name',
                '--ssh-key-name',
                help='Name of the ssh key that Salt must use for deploying'),
        ])

    args.salt_top_dir = os.path.join(args.salt_src_dir, args.top_dir)
    if args.target_docker_image:
        args.ssh_public_key = os.path.expandvars(
            '$HOME/.ssh/%s.pub' % args.ssh_key_name)

    return args


def _srv_salt_src_dir():
    return '/srv/salt-deploy/src'


def _write_roster_file(target_ip, target_container_name, salt_top_dir,
                       host_name):
    roster_filename = os.path.join(salt_top_dir,
                                   '.roster.%s' % target_container_name)
    with open(roster_filename, 'w') as ofs:
        ofs.write("%s:\n" % host_name)
        ofs.write("    host: %s\n" % target_ip)
        ofs.write("    priv: agent-forwarding\n")
    return roster_filename


salt_master_template = """
file_roots:
  base:
    - {srv_salt_top_dir}

pillar_roots:
  base:
    - {srv_salt_top_dir}/pillar
"""


def _write_salt_master_file(salt_top_dir, srv_salt_top_dir):
    salt_master_filename = os.path.join(salt_top_dir,
                                        '.master.%s' % uuid.uuid4().hex)
    with open(salt_master_filename, 'w') as ofs:
        ofs.write(
            salt_master_template.format(srv_salt_top_dir=srv_salt_top_dir))
    return salt_master_filename


def _create_docker_options(salt_src_dir, salt_master_filename):
    docker_options = Dodo.get_config().setdefault('DOCKER', {}).setdefault(
        'options', {})

    if Dodo.command_name not in docker_options:
        docker_options[Dodo.command_name] = dict(
            volume_map={salt_src_dir: '/srv/salt-deploy/src'},
            variable_map={'SSH_AUTH_SOCK': '/.ssh-agent/socket'},
            volumes_from_list=['ssh-agent'],
            image='deploy-tools:base')

    docker_options[Dodo.command_name].setdefault(
        'volume_map', {})[salt_master_filename] = '/etc/salt/master'


if Dodo.is_main(__name__):
    args = _args()

    if args.target_docker_image:
        target_ip, target_container_name = run_ssh_server(
            args.ssh_public_key, args.target_docker_image)
        salt_master_container_name = (
            'salt_master_deploying_to_%s' % target_container_name)
        roster_filename = _write_roster_file(target_ip, target_container_name,
                                             args.salt_top_dir, args.host_name)

        if args.verbose:
            with open(roster_filename) as ifs:
                print(
                    '\nI have created the following temporary Salt roster file:\n'
                )
                print(ifs.read())
    else:
        salt_master_container_name = 'salt_master_deploying_to_%s' % args.host_name
        roster_filename = "roster"

    salt_master_filename = _write_salt_master_file(
        args.salt_top_dir, os.path.join(_srv_salt_src_dir(), args.top_dir))

    if args.verbose:
        with open(salt_master_filename) as ifs:
            print('I have created the following temporary Salt master file:\n')
            print(ifs.read())

    if args.bash:
        cmd = ['/bin/bash']
    else:
        cmd = ([
            'salt-ssh',  # '-l', 'debug',
            '-i',
            '--roster-file=./%s' % os.path.basename(roster_filename),
            args.host_name
        ] + (['state.sls', 'debug'] if args.debug else ['state.apply']))

    _create_docker_options(args.salt_src_dir, salt_master_filename)
    with DecoratorScope('docker'):
        Dodo.run(cmd, cwd=os.path.join(_srv_salt_src_dir(), args.top_dir))

    os.unlink(salt_master_filename)
    if args.target_docker_image:
        commit_ssh_server(target_container_name, args.target_docker_image)
        os.unlink(roster_filename)
