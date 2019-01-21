"""
coy.py - A program to control the behavior of process dynamically.

Coy monitors various kinds of resources ("watch") and affects the behavior of
the specified process ("control"). A 'some_task' process is controlled by coy
in the following example:

    $ python coy.py ./some_task

[For developer] The diagram below illustrates the control flow of the coy
program. Watcher.py and controller.py provide several watcher classes and
controller classes respectively each of which has its own features of how to
achieve watching/controlling.

          coy
           |
           +--> (fork process) --+
           |                     |
           v                     |
    +--> watcher                 |
    |      |                     |
    |      v                     |
    |    (detect state change)   |
    |      |                     |
    |      v                     |
    |    controller -----------> @ (effect on process)
    |      |                     |
    +----- @ (loop while         |
           |  process is alive)  |
           |                     |
           v                     |
           +<--------------------+
           |
           v
          end

Copyright 2018 coronocoya.net <nshou@coronocoya.net>
This code can be distributed under the terms of MIT License. Please see the
file COPYING for the license description.

"""

__version__ = '0.0.1'


import argparse
import sys
import subprocess
from . import watcher
from . import controller


def _print_error(message):
    """
    Prints out message prepended with a tag to stderr.

    Args:
      message (str): A string to be printed.

    """
    print('[coy] %s' % message, file=sys.stderr)


def _parse_command():
    """
    Parses command line. This function may exit and never return.

    Returns:
      argparse.Namespace: Parsed results.

    """
    parser = argparse.ArgumentParser(description='A program to control the behavior of process dynamically.', add_help=False)
    parser.add_argument('-w', '--watcher', help='A watcher to be used. Default is CPUUsageWatcher.', default='CPUUsageWatcher')
    parser.add_argument('-o', '--watcher-option', help='Options for watcher.')
    parser.add_argument('-c', '--controller', help='A controller to be used. Default is StopContController.', default='StopContController')
    parser.add_argument('-p', '--controller-option', help='Options for controller.')
    parser.add_argument('-h', '--help', help='Print this message or help message for watcher/controller specified by NAME, then exit.', nargs='?', const='self', metavar='NAME')
    parser.add_argument('-l', '--list', help='Print available watchers/controllers and exit.', action='store_true')
    parser.add_argument('-v', '--version', action='version', version=__version__)
    parser.add_argument('command', nargs=argparse.REMAINDER, metavar='COMMAND [OPTIONS ...]')
    res = parser.parse_args()

    if res.help is not None:
        if res.help == 'self':
            parser.print_help()
            sys.exit(0)
        else:
            # TODO: print_help(res.help)
            sys.exit(0)

    if res.list:
        # TODO: print_list()
        sys.exit(0)

    if not res.command:
        parser.print_help()
        sys.exit(1)

    return res


def prepare_watcher(watcher_name):
    """
    Instantiates and returns watcher object specified by name.

    Args:
      watcher_name (str): Name of watcher class to be instantiated.

    Returns:
      watcher.Watcher: A watcher object if successful, None otherwise.

    """
    watcher_obj = None

    if watcher_name not in dir(watcher):
        _print_error('%s is not defined as a watcher.' % watcher_name)
    elif watcher_name not in watcher.ALL:
        _print_error('%s is not activated.' % watcher_name)
    else:
        try:
            watcher_obj = getattr(watcher, watcher_name)()
        except Exception as err:
            _print_error('Failed to instantiate %s: %s' % (watcher_name, err))

    return watcher_obj


def prepare_controller(controller_name):
    """
    Instantiates and returns controller object specified by name.

    Args:
      controller_name (str): Name of controller class to be instantiated.

    Returns:
      controller.Controller: A controller object if successful, None otherwise.

    """
    controller_obj = None

    if controller_name not in dir(controller):
        _print_error('%s is not defined as a controller.' % controller_name)
    elif controller_name not in controller.ALL:
        _print_error('%s is not activated.' % controller_name)
    else:
        try:
            controller_obj = getattr(controller, controller_name)()
        except Exception as err:
            _print_error('Failed to instantiate %s: %s' % (controller_name, err))

    return controller_obj


def start_process(args):
    """
    Forks and starts a process and returns it as subprocess.Popen object.

    Args:
      args (list): Argument list of the process (ex. ['ls', '-l'].)

    Returns:
      subprocess.Popen: Popen object if successful, None otherwise.

    """
    proc = None

    try:
        proc = subprocess.Popen(args)
    except (OSError, ValueError, subprocess.SubprocessError) as err:
        _print_error('Failed to start process: %s' % err)

    return proc


def coy_work(args, watcher_name, controller_name):
    """
    Starts the main routine of the coy program.

    It immediately returns when it fails to {fork process | make watcher object
    | make controller object}. It also returns when the forked process
    terminates.

    Args:
      args (list): Argument for 'start_process()'.
      watcher_name (str): Argument for 'prepare_watcher()'.
      controller_name (str): Argument for 'prepare_controller()'.

    """
    watcher_obj = prepare_watcher(watcher_name)
    if watcher_obj is None:
        return

    controller_obj = prepare_controller(controller_name)
    if controller_obj is None:
        return

    proc = start_process(args)
    if proc is None:
        return

    watcher_obj.set_proc(proc)
    controller_obj.set_proc(proc)

    while proc.poll() is None:
        state = watcher_obj.watch()
        controller_obj.control(state)


def main():
    """Called when coy is run as a command line script."""
    args = _parse_command()
    coy_work(args.command, args.watcher, args.controller)


if __name__ == '__main__':
    main()
