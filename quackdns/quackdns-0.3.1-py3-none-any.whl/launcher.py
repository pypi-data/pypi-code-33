#!/usr/bin/env python3
import argparse
import os
import platform
import psutil
import signal
import subprocess
import sys
import time
import warnings

__APP_PATH__ = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
sys.path.insert(0, __APP_PATH__)  # Add module to sys path

import quackdns.config as config
import quackdns.cli as cli

__DEFAULT_UPDATE_INTERVAL__ = config.__DEFAULT_UPDATE_INTERVAL__
__DEFAULT_CONFIG_PATH__ = config.__DEFAULT_CONFIG_PATH__
__DAEMON_PID_LOCK_PATH__ = config.__DAEMON_PID_LOCK_PATH__

# https://stackoverflow.com/questions/13243807/popen-waiting-for-child-process-even-when-the-immediate-child-has-terminated/13256908#13256908
def detaching_kwargs():
    kwargs = {}
    if platform.system() == 'Windows':
        # from msdn [1]
        CREATE_NEW_PROCESS_GROUP = 0x00000200  # note: could get it from subprocess
        DETACHED_PROCESS = 0x00000008  # 0x8 | 0x200 == 0x208
        kwargs.update(creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
    elif sys.version_info < (3, 2):  # assume posix
        kwargs.update(preexec_fn=os.setsid)
    else:  # Python 3.2+ and Unix
        kwargs.update(start_new_session=True)
    return kwargs


def check_running():
    if os.path.exists(__DAEMON_PID_LOCK_PATH__):
        with open(__DAEMON_PID_LOCK_PATH__) as daemon_pid_lock_file:
            pid = int(daemon_pid_lock_file.read())
        # A daemon lock was found but not its process
        if not psutil.pid_exists(pid):
            raise SingleInstanceError(path=__DAEMON_PID_LOCK_PATH__, pid=pid)
        else:
            return True
    else:
        return False


def start(args):
    # Check if a configuration file exist and load it
    if os.path.exists(args["config"]):
        settings = config.Settings()
        try:
            settings.load(args["config"])

        # Create a new configuration when the file is not readable
        except config.InvalidSettingsError as error:
            warnings.warn(str(error))
            print("A new configuration is required.")
            settings = cli.configure_dns_parameters()
            settings.save(args["config"])

    # Else create a new configuration
    else:
        print("No configuration file found. Beginning configuration.")
        settings = cli.configure_dns_parameters()
        settings.save(args["config"])

    # Check if a daemon lock exists
    if os.path.exists(__DAEMON_PID_LOCK_PATH__):
        with open(__DAEMON_PID_LOCK_PATH__) as daemon_pid_lock_file:
            pid = int(daemon_pid_lock_file.read())

        # A daemon lock was found but not its process
        if not psutil.pid_exists(pid):
            raise SingleInstanceError(path=__DAEMON_PID_LOCK_PATH__, pid=pid)
        else:
            print("Daemon is already running with pid: {}".format(pid))
    else:
        print("Starting..")
        # Run the updater as a separate process
        command_list = [
            # sys.executable,
                        os.path.join(__APP_PATH__, "quackdns", "daemon.py"),
                        "--config", args["config"],
                        "--interval", str(args["interval"]),
                        ]
        command_str = " ".join(command_list)
        # print(command_str)
        pid = subprocess.Popen(command_list,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               **(detaching_kwargs())).pid
        print("Started: daemon running with pid: {}".format(pid))

def stop(args):
    # Check if lock exists and read the process pid
    if os.path.exists(__DAEMON_PID_LOCK_PATH__):
        with open(__DAEMON_PID_LOCK_PATH__) as daemon_pid_lock_file:
            pid = int(daemon_pid_lock_file.read())

        print("Stopping.", end="")
        # Send a signal to daemon for stopping
        os.kill(pid, signal.SIGALRM)

        # Waits for the process to finish for 10 seconds
        for i in range(10):
            if not psutil.pid_exists(pid):
                print("\nStopped!")
                return
            else:
                print(".", end="")
            time.sleep(1)

        warnings.warn("Process did not terminate..")

    else:
        warnings.warn("No daemon found.")

def restart(args):
    stop(args)
    time.sleep(1)
    start(args)


# Main function
def main():
    args = vars(cli.parse_arguments(sys.argv))
    config.create_resources_folder()

    if args["action"] == 'start':
        start(args)
    elif args["action"] =='stop':
        stop(args)
    elif args["action"] == 'restart':
        restart(args)
    else:
        raise ValueError("Could not recognise argument: {}".format(args["action"]))


# Defines an error for lock existing when process doesn't
class SingleInstanceError(Exception):
    def __init__(self, path: str, pid: int):
        self.msg = "Application lock found at {} indicating that a" \
                   " daemon should be already running with pid: {}.".format(path, pid)

    def __str__(self):
        return repr(self.msg)


# Run the main function
if __name__ == "__main__":
    main()