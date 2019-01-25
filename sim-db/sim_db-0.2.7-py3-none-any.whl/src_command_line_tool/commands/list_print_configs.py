#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Print a list of all the personalized print configurations.

These are the print configurations specified in 'settings.txt' and can be 
modified there. The name of each configuration will be printed followd by the
flags they are shortcuts for.

Usage: 'python print_sim.py -p NAME_PERSONALIZED_PRINT_CONFIGURATION'
"""
# Copyright (C) 2018-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

if __name__ == '__main__':
    import add_package_root_to_path

import sim_db.src_command_line_tool.commands.helpers as helpers
import argparse
import sys


def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="list_print_configs"):
    parser = argparse.ArgumentParser(
            description=
            "Print a list of all the personalized print configurations.",
            prog="{0} {1}".format(name_command_line_tool, name_command))

    return parser


def list_print_configs(name_command_line_tool="sim_db",
                       name_command="list_print_configs"):
    command_line_arguments_parser(name_command_line_tool, name_command)
    settings = helpers.Settings()
    print_configs = settings.read('print_config')
    for print_config in print_configs:
        print(print_config)


if __name__ == '__main__':
    list_print_configs("", sys.argv[0], sys.argv[1:])
