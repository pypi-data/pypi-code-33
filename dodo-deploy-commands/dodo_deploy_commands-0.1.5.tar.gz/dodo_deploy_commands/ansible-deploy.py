from argparse import ArgumentParser
from dodo_commands.framework import Dodo, CommandError, DecoratorScope
import os
from ._utils import run_ssh_server, commit_ssh_server


def _args():  # noqa
    parser = ArgumentParser(
        description=('Deploys a ansible script to a ssh server'))
    parser.add_argument(
        "--bash",
        action="store_true",
        help='Drop into a bash shell instead of calling ansible')

    args = Dodo.parse_args(parser)
    args.playbook = Dodo.get_config('/ANSIBLE/playbook')
    args.ansible_src_dir = Dodo.get_config('/ANSIBLE/src_dir')
    args.target_docker_image = Dodo.get_config('/ANSIBLE/target_docker_image',
                                               None)
    args.host_name = Dodo.get_config('/ANSIBLE/host_name', None)

    if args.host_name and args.target_docker_image:
        raise CommandError('Both host_name and target_docker_image supplied')

    if args.target_docker_image:
        args.ssh_public_key = os.path.expandvars(
            '$HOME/.ssh/%s.pub' % Dodo.get_config('/SSH/key_name'))

    return args


def _srv_ansible_src_dir():
    return '/srv/ansible-deploy/src'


def _write_inventory_file(ansible_src_dir, target_ip):
    inventory_filename = os.path.join(ansible_src_dir,
                                      '.inventory.%s' % target_container_name)
    with open(inventory_filename, 'w') as ofs:
        ofs.write("[webservers]\n")
        ofs.write("%s ansible_host=%s is_docker_host=True" %
                  (target_container_name, target_ip))
    return 'target', inventory_filename


if Dodo.is_main(__name__):
    args = _args()

    if args.target_docker_image:
        target_ip, target_container_name = run_ssh_server(
            args.ssh_public_key, args.target_docker_image)
        target, inventory_filename = _write_inventory_file(
            args.ansible_src_dir, target_ip)
    else:
        target = args.host_name

    if args.bash:
        print(target_ip)
        cmd = ['/bin/bash']
    else:
        # yapf: disable
        cmd = [
            'ansible-playbook', args.playbook,
            '--ssh-extra-args=\'-o StrictHostKeyChecking=no\'',
            '-i', os.path.basename(inventory_filename),
            '-l', target_container_name,
            '-u', 'root'
        ]
        # yapf: enable

    with DecoratorScope('docker'):
        Dodo.run(cmd, cwd=_srv_ansible_src_dir())

    if args.target_docker_image:
        commit_ssh_server(target_container_name, args.target_docker_image)
        os.unlink(inventory_filename)
