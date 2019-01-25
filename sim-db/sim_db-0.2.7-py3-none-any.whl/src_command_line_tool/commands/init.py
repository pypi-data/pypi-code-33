#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialise '.

Must be called before using '.

This commands should be called from the top directory of your project or with
the path to the top directory as an argument.

The command will create a hidden directory called .and copy the default
settings into this directory.
"""
# Copyright (C) 2018-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

import os
import argparse
import sys
import shutil


def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="init"):
    parser = argparse.ArgumentParser(
            description=("Initialise ' and must be called before using '. "
                         "Will create a '.' directory."),
            prog="{0} {1}".format(name_command_line_tool, name_command))
    parser.add_argument(
            '--path',
            type=str,
            default=None,
            help=
            ("Path to the top directory of project. If not passed as an "
             "argument, the current working directory is assumed to be the top "
             "directory."))

    return parser


def init(name_command_line_tool="sim_db", name_command="init", argv=None):
    args = command_line_arguments_parser(name_command_line_tool,
                                         name_command).parse_args(argv)
    if args.path == None:
        args.path = os.getcwd()
    elif args.path[-1] == '/':
        args.path = args.path[:-1]

    path_dot_sim_db_dir = os.path.join(args.path, '.sim_db')

    if os.path.exists(path_dot_sim_db_dir):
        if os.path.isdir(path_dot_sim_db_dir):
            if os.path.exists(
                    os.path.join(path_dot_sim_db_dir, "settings.txt")):
                print("sim_db is already initialized in {0}/".format(
                        path_dot_sim_db_dir))
                exit()

    os.mkdir(path_dot_sim_db_dir)
    path_default_settings = os.path.abspath(os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'default_settings.txt'))
    shutil.copyfile(
            path_default_settings,
            os.path.join(os.path.join(args.path, '.sim_db'), 'settings.txt'))
    print("Initialized sim_db directory.")


if __name__ == '__main__':
    init("", sys.argv[0], sys.argv[1:])
