import socket
import platform
import os
import sys

from os import path
from cpbox.tool import template

def get_os_name():
    os_name = platform.system()
    map = {
            'Linux': 'linux',
            'Darwin': 'mac',
            'CYGWIN': 'cygwin',
            'MINGW': 'MinGw',
            }
    for name, sys in map.iteritems():
        if os_name.startswith(name):
            return sys
    return 'unknown'

def fg_mode():
    return '-it' if sys.stdout.isatty() else '-i'

def base_docker_args(env=None, container_name=None, volumes=None, ports=None, current_user=False, envs=None, working_dir=None, auto_hostname=True, hostname=None):
    host_hostname = socket.gethostname()
    host_hostname_short = host_hostname.split('.')[0]
    args = '--name ' + container_name
    if auto_hostname:
        args += ' -h %s.docker.%s' % (container_name, host_hostname_short)
    else:
        if hostname:
            args += ' -h %s' % (hostname)
        else:
            args += ' -h %s' % (host_hostname)

    args += ' -e PUPPY_HOSTNAME=' + host_hostname
    args += ' -e PUPPY_CONTAINER_NAME=' + container_name
    for key, value in os.environ.items():
        if key.startswith('PUPPY_'):
            args += ' -e %s="%s"' % (key, value)
    if env:
        args += ' -e PUPPY_ENV=' + env

    if working_dir:
        args += ' -w ' + working_dir

    if current_user:
        args += ' -u %s:%s' % (os.getuid(), os.getgid())

    if volumes:
        if isinstance(volumes, dict):
            args += ' ' + ' '.join(('-v ' + from_ + ':' + to_ for from_, to_ in volumes.iteritems()))
        else:
            args += ' ' + ' '.join(('-v ' + item for item in volumes))
    if ports:
        if isinstance(ports, dict):
            args += ' ' + ' '.join(('-p ' + str(from_) + ':' + str(to_) for from_, to_ in ports.iteritems()))
        else:
            args += ' ' + ' '.join(('-p ' + str(item) for item in ports))
    if envs:
        args += ' ' + ' '.join(('-e ' + item for item in envs))

    os_name = get_os_name()
    if os_name != 'mac':
        args += ' -v /etc/localtime:/etc/localtime'
    if path.isfile('/etc/devops'):
        args += ' -v /etc/devops/:/etc/devops/:ro'

    return args
