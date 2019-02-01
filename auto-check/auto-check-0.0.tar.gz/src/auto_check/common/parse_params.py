#!/usr/local/bin/python3
import argparse
import sys

class params:
    pass

def parse():
    p = params()
    parser = argparse.ArgumentParser('auto_check', description='A script for checking in & out automatically, which is just for fun ^_^.',)

    # parser = argparse.ArgumentParser(
    #     prog='自动打卡签到',
    #     #usage='python3 __main__.py [OPTION]... URL...',
    #
    #     add_help=False,
    # )

    parser.add_argument(
        '-v', '--version', action='store_true',
        help='print version and exit'
    )

    run_grp = parser.add_argument_group(
        'Run options'
    )
    run_grp.add_argument(
        '-c', '--config_dir', action='store', default="./config/",
        help='the config files\' directory path'
    )
    run_grp.add_argument(
        '-s', '--suffix', action='store', default='',
        help='run the config ending with the specific suffix'
    )
    run_grp.add_argument(
        '-t', '--test', action='store_true',
        help='set to test mode, aka not perform checking in or out'
    )
    run_grp.add_argument(
        '-i', '--immediately', action='store_true',
        help='perform checking in or out with random delay'
    )
    args = parser.parse_args(sys.argv[1:], namespace=p)

    if args.version:
        print('Auto Checker v0.0.1')
        sys.exit()

    return p
