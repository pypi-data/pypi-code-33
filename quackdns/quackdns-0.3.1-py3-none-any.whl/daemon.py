#!/usr/bin/python3
import logging
import argparse
import sys
import os


__APP_PATH__ = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
sys.path.insert(0, __APP_PATH__)  # Add module to sys path

import quackdns.config as config
import quackdns.updater as updater

# Log configuration
config.create_resources_folder()
logging.basicConfig(filename=config.__LOG_PATH__,
                    level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

__DAEMON_PID_LOCK_PATH__ = config.__DAEMON_PID_LOCK_PATH__


# Pseudo-logger class for stdout/stderr redirection to log
# https://www.electricmonk.nl/log/2011/08/14/redirect-stdout-and-stderr-to-a-logger-in-python/
class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

def remove_lock():
    if os.path.exists(__DAEMON_PID_LOCK_PATH__):
        os.remove(__DAEMON_PID_LOCK_PATH__)
    else:
        raise MissingLockError(__DAEMON_PID_LOCK_PATH__)



# Main function
def main(mode: str = 'cli'):
    #  Redirect output to logger
    stdout_logger = logging.getLogger('STDOUT')
    sys.stdout = StreamToLogger(stdout_logger, logging.INFO)

    stderr_logger = logging.getLogger('STDERR')
    sys.stderr = StreamToLogger(stderr_logger, logging.ERROR)

    print("Daemon started")
    try:
        # Create daemon lock
        app_pid = os.getpid()
        print("Started daemon with pid: {}".format(app_pid))
        with open(__DAEMON_PID_LOCK_PATH__, "w") as demon_pid_file:
            demon_pid_file.write(str(app_pid))

        # print(os.getpid())

        # Parse arguments
        parser = argparse.ArgumentParser(description='Quack DNS daemon.')
        parser.add_argument('-c', '--config', type=str, required=True,
                            help='Configuration file.')
        parser.add_argument('-i', '--interval', type=str, required=True,
                            help='Interval (seconds) between updates')
        args = parser.parse_args(sys.argv[1:])

        settings = config.Settings()
        settings.load(args.config)

        my_updater = updater.Updater(settings.get_domain(),
                                     settings.get_token())

        my_updater.loop_update(sleep_seconds=int(args.interval))
        os.remove(__DAEMON_PID_LOCK_PATH__)
        exit()
    except SystemExit as e:
        print(str(e))
        # Remove lock before exiting
        remove_lock()
        exit()

    except Exception as e:
        # Remove lock before exiting
        remove_lock()
        raise e
        exit()

if __name__ == "__main__":
    main()

# Defines an error for not finding a system lock
class MissingLockError(Exception):
    def __init__(self, path: str):
        self.msg = "Application lock not found at {}.".format(path)

    def __str__(self):
        return repr(self.msg)
