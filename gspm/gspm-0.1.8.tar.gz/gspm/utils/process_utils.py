
import logging
import subprocess


def run_process(cmd, with_shell=False):
    '''
    run a process and wait for it to complete
    '''
    try:
        proc = subprocess.Popen(cmd, shell=with_shell)
        proc.communicate()
    except Exception as e:
        logging.error(e)
        raise Exception("Could not run Command [{0}]".format(cmd))

