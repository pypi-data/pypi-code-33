#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Print and change the settings.

Pass either 'print', 'add', 'remove' or 'reset_to_default' as commands.

usage: python settings <command> <args>
"""
# Copyright (C) 2017-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

if __name__ == '__main__':
    import add_package_root_to_path

import sim_db.src_command_line_tool.commands.helpers as helpers
import argparse
import shutil
import sys
import os

def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="settings"):
    parser = argparse.ArgumentParser(
            description=("Print and change settings. The settings can also "
                         "be changed be editing the '.settings.txt' file."),
            prog="{0} {1}".format(name_command_line_tool, name_command))
    parser.add_argument('command', type=str, help="'print', 'add', 'remove' "
                        "or 'reset_to_default'")

    return parser


def parser_for_print(name_command_line_tool="sim_db", name_command="settings"):
    parser = argparse.ArgumentParser(
            description="Print the current settings.",
            usage="{0} {1} print".format(name_command_line_tool, name_command))
    parser.add_argument(
            '--setting',
            '-s',
            type=str,
            default=None,
            help=
            "Which setting to print. If no setting is specified, the entire setting file is printed."
    )

    return parser


def parser_for_add(name_command_line_tool="sim_db", name_command="settings"):
    parser = argparse.ArgumentParser(
            description="Add a line to the settings.",
            usage="{0} {1} add".format(name_command_line_tool, name_command))
    parser.add_argument(
            '--line',
            '-l',
            type=str,
            required=True,
            help="<Required> Line added to 'setting' in the settings.")
    parser.add_argument(
            '--setting',
            '-s',
            type=str,
            required=True,
            help="<Required> Which setting to add a line to.")

    return parser


def parser_for_remove(name_command_line_tool="sim_db",
                      name_command="settings"):
    parser = argparse.ArgumentParser(
        description="Remove a line from the settings.",
        usage="{0} {1} remove".format(name_command_line_tool, name_command))
    parser.add_argument('--line', '-l', type=str, required=True, help="<Required> Line to remove from 'setting' in the settings.")
    parser.add_argument('--setting', '-s', type=str, required=True, help="<Required> Which setting to remove a line from.")

    return parser


def parser_for_reset_to_default(name_command_line_tool="sim_db",
                      name_command="settings"):
    parser = argparse.ArgumentParser(
        description="Resets settings to default.",
        usage="{0} {1} reset_to_default".format(name_command_line_tool, name_command))

    return parser


def settings(name_command_line_tool="sim_db",
             name_command="settings",
             argv=None):
    args = command_line_arguments_parser(name_command_line_tool,
                                         name_command).parse_args(argv[0:1])
    command = args.command
    if command == 'print':
        args = parser_for_print(name_command_line_tool,
                                name_command).parse_args(argv[1:])
        if args.setting == None:
            settings_file = open(
                    os.path.join(helpers.get_dot_sim_db_dir_path(),
                                 'settings.txt'), 'r')
            for line in settings_file.readlines():
                print(line)
            settings_file.close()
        else:
            settings = helpers.Settings()
            if args.setting not in settings.settings_dict:
                print("{0} is NOT a valid setting.".format(args.setting))
                print("\nChoose on of the following settings:")
                for setting_key in settings.settings_dict.keys():
                    print(setting_key)
                exit(1)
            for line in settings.read(args.setting):
                print(line)
    elif command == 'add':
        args = parser_for_add(name_command_line_tool,
                              name_command).parse_args(argv[1:])
        settings = helpers.Settings()
        if args.setting not in settings.settings_dict:
            print("{0} is NOT a valid setting.".format(args.setting))
            print("\nChoose on of the following settings:")
            for setting_key in settings.settings_dict.keys():
                print(setting_key)
            exit(1)
        settings.add(args.setting, args.line)
    elif command == 'remove':
        args = parser_for_remove(name_command_line_tool,
                                 name_command).parse_args(argv[1:])
        settings = helpers.Settings()
        if args.setting not in settings.settings_dict:
            print("{0} is NOT a valid setting.".format(args.setting))
            print("\nChoose on of the following settings:")
            for setting_key in settings.settings_dict.keys():
                print(setting_key)
            exit(1)
        is_removed = settings.remove(args.setting, args.line)
        if not is_removed:
            print("'{0}' was NOT found under the '{1}' settings.\nIt was "
                  "therefor NOT removed from the settings.".format(
                          args.line, args.setting))
    elif command == 'reset_to_default':
        args = parser_for_reset_to_default(name_command_line_tool,
                                 name_command).parse_args(argv[1:])
        path_settings = os.path.join(helpers.get_dot_sim_db_dir_path(), 
                                     "settings.txt")
        os.remove(path_settings)
        path_default_settings = os.path.abspath(os.path.join(
                        os.path.dirname(os.path.abspath(__file__)),
                        'default_settings.txt'))
        shutil.copyfile(path_default_settings, path_settings)
        print("Settings reset to default.")
    else:
        print("'{0}' is not a valid command. 'print', 'add', 'remove' or "
              "'reset_to_default' are the valid commands.".format(command))


if __name__ == '__main__':
    settings("", sys.argv[0], sys.argv[1:])
