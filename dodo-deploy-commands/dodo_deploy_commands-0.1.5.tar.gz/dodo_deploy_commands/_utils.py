from dodo_commands.framework import Dodo
from plumbum.cmd import docker


def try_ssh(target_ip):
    Dodo.run([
        'ssh',
        'root@%s' % target_ip, '-oStrictHostKeyChecking=no',
        '-oUserKnownHostsFile=/dev/null', 'echo'
    ])


def run_ssh_server(ssh_public_key, target_docker_image):
    cleaned_docker_name = target_docker_image.replace(':', '_').replace(
        '/', '_')
    target_container_name = "sshd_on_%s" % cleaned_docker_name

    # start ssh service on a new container based on target_docker_image
    Dodo.run([
        'docker',
        'run',
        '-d',
        '--rm',
        '--publish=0.0.0.0:22:22',
        '--name=%s' % target_container_name,
        target_docker_image,
        '/usr/sbin/sshd',
        '-D',
    ])

    # copy public key to the docker container
    Dodo.run([
        'docker', 'cp', ssh_public_key,
        '%s:/root/.ssh/authorized_keys' % target_container_name
    ])

    # get the ip address
    target_ip = docker(
        'inspect', '-f',
        '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
        target_container_name)[:-1]

    return target_ip, target_container_name


def commit_ssh_server(target_container_name, target_docker_image):
    # commit the container
    Dodo.run(['docker', 'commit', target_container_name, target_docker_image])
    # stop the container
    Dodo.run(['docker', 'stop', target_container_name])
