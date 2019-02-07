import argparse
import logging
import os
import platform
import re
import sys
from subprocess import Popen, PIPE

logger = logging.getLogger()


class ExeNotFound(Exception):
    """ Custom exception for catching cases where an executable isn't found. """
    pass


class DeadlineDockerSubmitter(object):
    """ Simple class for use in submitting docker jobs to the deadline render manager. """

    def __init__(self):
        """
        Initializes an instance of this class.
        """
        logger.debug('instantiating DockerSubmitter instance')
        self._exe = r'${DEADLINE_PATH}\deadlinecommand.exe'
        self._command = None
        self._pool = 'docker'
        self._docker = r'C:\PROGRA~1\Docker Toolbox\docker.exe'

    @property
    def exe(self):
        """
        Attempts to return the path to the deadlinecommand.exe for use in submitting
        a command line job to the deadline render farm manager.

        Returns:
            full path to the deadlinecommand.exe

        Raises:
            ExeNotFound error if the deadlinecommand.exe doesn't exist
        """
        exe = os.path.expandvars(self._exe)

        if platform.system().lower() != 'windows':
            exe = exe.split('.')[0]

        if not os.path.exists(exe):
            raise ExeNotFound('{} not found!. unable to submit.'.format(exe))
        return exe

    def __call__(self, command, name=None, priority=50):
        """
        Submits the command to the farm using deadlinecommand.exe and returns a
        tuple containing the return code from the process and the jobid of the submission.

        Args:
            command (str): the docker command to actually execute
            name (str): optional name of the job, default: 'Docker-job'
            priority (str): the priority of the job, default: 50

        Returns (tuple):
            deadlinecommand.exe return code and the jobid of the submission
        """
        logger.debug('attempting deadline commandline submission')
        if not name:
            name = 'Docker-job'

        if not priority:
            priority = '50'

        p = Popen([self.exe, '-SubmitCommandlineJob', '-executable', self._docker, '-arguments', command, '-priority',
                   str(priority), '-name', name, '-pool', self._pool], stderr=PIPE, stdout=PIPE)

        out, err = p.communicate()

        if out:
            logger.info(out)

        if err:
            logger.error(err)

        result = re.search('JobID=(.*)\r', out)
        return p.returncode, result.group(1)


def parse_args(args):
    """

    Args:
        args(list): variable length list of arguments that must meet the requirements below.

    Returns:
        Namespace(command, name, priority, loglevel)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command', type=str, help='command to run with docker', required=True)
    parser.add_argument('-n', '--name', type=str, help='name of job')
    parser.add_argument('-p', '--priority', type=int, help='priority of the job', default=50)
    parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
    parser.add_argument('-v', '--verbose', action='store_const', dest='loglevel', const=logging.INFO)

    return parser.parse_args(args)


def main():
    """
    The main entry point of this particular program. Will attempt to submit a commandline job to
    the deadline render farm manager that will run the 'command' argument via docker on the
    worker nodes that exist in the 'docker' pool. It assumes there are nodes in the pool and that
    the docker daemon is installed and running on the worker.

    Returns:
        The return code of the deadlinecommand.exe

    """
    args = parse_args(sys.argv[1:])
    logging.basicConfig(level=args.loglevel)

    return DeadlineDockerSubmitter()(args.command, args.name, args.priority)[0]


if __name__ == '__main__':
    sys.exit(main())
