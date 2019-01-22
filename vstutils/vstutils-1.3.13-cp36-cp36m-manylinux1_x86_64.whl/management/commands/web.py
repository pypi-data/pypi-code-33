from __future__ import unicode_literals
import os
import sys
import time
from subprocess import CalledProcessError
import subprocess
import signal
import six
from django.conf import settings
from ._base import BaseCommand


def wait(proc, timeout=None, delay=0.1):
    while proc.poll() is None and (timeout or timeout is None):
        time.sleep(delay)
        if timeout is not None:
            timeout -= delay
    return proc.poll()


class Command(BaseCommand):
    help = "Backend web-server."
    _uwsgi_default_path = "{}/uwsgi".format(os.path.dirname(sys.executable))

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            'args',
            metavar='uwsgi_arg=value', nargs='*',
            help='Args "name=value" uwsgi server.',
        )
        parser.add_argument(
            '--uwsgi-path', '-s',
            default=self._uwsgi_default_path, dest='script',
            help='Specifies the uwsgi script.',
        )
        parser.add_argument(
            '--uwsgi-config', '-c',
            default='{}/web.ini'.format(settings.VST_PROJECT_DIR),
            dest='config', help='Specifies the uwsgi script.',
        )

    def _get_uwsgi_arg(self, arg):
        return arg if isinstance(arg, six.string_types) else None

    def _get_uwsgi_args(self, *uwsgi_args):
        return [self._get_uwsgi_arg(arg) for arg in uwsgi_args]

    def _get_worker_options(self):
        cmd = []
        if not settings.RUN_WORKER:
            return cmd
        worker_options = settings.WORKER_OPTIONS
        options = ''
        for key, value in worker_options.items():
            is_boolean = isinstance(value, bool)
            if (is_boolean and value) or value:
                options += ' --{}'.format(key)
            if is_boolean:
                continue
            options += "={}".format(value.replace(',', r'\,'))
        cmd += ['--attach-daemon2']
        run = 'stopsignal=15,reloadsignal=1,'
        run += 'exec={} -m celery worker'.format(settings.PYTHON_INTERPRETER)
        run += options
        cmd += [run]
        return cmd

    def handle(self, *uwsgi_args, **opts):
        super(Command, self).handle(*uwsgi_args, **opts)
        cmd = [opts['script'], '--enable-threads', '--master']
        cmd += [
            '--{}'.format(arg) for arg in self._get_uwsgi_args(*uwsgi_args)
            if arg is not None
        ]
        if not os.path.exists(opts['config']):
            raise self.CommandError("Doesn't exists: {}.".format(opts['config']))
        cmd += [opts['config']]
        if settings.VST_PROJECT_DIR != settings.BASE_DIR:
            cmd += ['--static-map', "/static={}/static".format(settings.VST_PROJECT_DIR)]
        if settings.VSTUTILS_DIR != settings.BASE_DIR:
            cmd += ['--static-map', "/static={}/static".format(settings.BASE_DIR)]
        cmd += ['--static-map', "/static={}/static".format(settings.VSTUTILS_DIR)]
        cmd += self._get_worker_options()
        try:
            self._print('Execute: ' + ' '.join(cmd))
            proc = subprocess.Popen(cmd)
            try:
                wait(proc)
            except:
                proc.send_signal(signal.SIGTERM)
                wait(proc, 10)
                proc.kill()
                wait(proc)
                raise
        except KeyboardInterrupt:
            self._print('Exit by user...', 'WARNING')
        except CalledProcessError as err:
            raise self.CommandError(str(err))
        except BaseException as err:
            self._print(str(err), 'ERROR')
            raise
