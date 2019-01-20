"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function

import signal
import sys

from .version_check import check_sdk_version
from .__version__ import __version__ as jumper_current_version
from .common import VlabException
from .jemu_args_parser import JemuArgsParser
from .vlab_hci_device import VirtualHciDevice
from .vlab_runner import VlabRunner
from .login import login

vlab_runner = VlabRunner()


def signal_handler(signum, frame):
    vlab_runner.stop_run()


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGABRT, signal_handler)


def validate_traces_list(traces_list):
    traces_list = traces_list.split(',')
    for trace in traces_list:
        if trace not in ['regs', 'interrupts', 'functions']:
            raise VlabException('jumper run: error: unrecognized trace:' + trace, 1)


def run(args):
    return vlab_runner.start(args)


def hci(args):
    check_sdk_version(False)
    virtual_hci_device = VirtualHciDevice()
    
    virtual_hci_device.start(args)
    vlab_runner.wait_to_finish()

    virtual_hci_device.stop()


def command_run(args):
    if args.version:
        print("v" + jumper_current_version)
        return 0

    if not args.fw:
        print("jumper run: error: argument --bin/-b/--fw is required")
        return 1

    if args.traces_list:
        args.traces_list = args.traces_list.lower().replace(' ', '')
        validate_traces_list(args.traces_list)

    return run(args)


def main():
    jemu_parser = JemuArgsParser()
    jemu_parser.parse(sys.argv[1:])
    args = jemu_parser.get_args()
    if args.command == 'run':
        return command_run(args)

    elif args.command == 'ble':
        hci(args)
        return 0

    elif args.command == 'login':
        login()


if __name__ == '__main__':
    try:
        exit(main())
    except VlabException as e:
        print(e.message)
        exit(e.exit_code())
