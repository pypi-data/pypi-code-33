#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Delete a row in the sim.db.

One must either provide a list of ID's or a condition to delete sets of 
simulation parameters (rows) from the database.

Usage: python delete_sim.py --id 'ID'
       python delete_sim.py --where 'CONDITION'
"""
# Copyright (C) 2017-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

if __name__ == '__main__':
    import add_package_root_to_path

import sim_db.src_command_line_tool.commands.delete_results_dir as delete_results_dir
import sim_db.src_command_line_tool.commands.helpers as helpers
import sqlite3
import argparse
import sys
import os.path


def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="delete_sim"):
    parser = argparse.ArgumentParser(
            description='Delete simulations from sim.db.',
            prog="{0} {1}".format(name_command_line_tool, name_command))
    parser.add_argument(
            '--id',
            '-i',
            type=int,
            nargs='+',
            default=[],
            help="ID's of runs to delete.")
    parser.add_argument(
            '--where',
            '-w',
            type=str,
            default=None,
            help=
            ("Condition for which entries should be deleted. Must be a "
             "valid SQL (sqlite3) command when added after WHERE in a DELETE "
             "command."))
    parser.add_argument(
            '--all',
            action="store_true",
            help="Delete all simulation from database.")
    parser.add_argument(
            '--no_checks',
            action='store_true',
            help=("No questions are asked about wheter you really want to "
                  "delete simulation or the 'results_dir' of the simulation."))

    return parser


def delete_sim(name_command_line_tool="sim_db",
               name_command="delete_sim",
               argv=None):
    db = helpers.connect_sim_db()
    db_cursor = db.cursor()

    args = command_line_arguments_parser(name_command_line_tool,
                                         name_command).parse_args(argv)

    if args.all:
        args.where = "id > -1"

    answer = 'n'
    if len(args.id) == 0 and args.where == None:
        print("--id 'ID' or --where 'CONDITION' must be passed to the "
              "program.")
    elif len(args.id) > 0 and not args.no_checks:
        print("Do you really want to delete simulations with following ID's:")
        for delete_id in args.id:
            print(delete_id)
        answer = helpers.user_input("? (y/n)")
    elif args.where != None and not args.no_checks:
        print("Do you really want to delete simulations with following "
              "condition:")
        print(args.where)
        answer = helpers.user_input("? (y/n)")

    if (answer == 'y' or answer == 'Y' or answer == 'yes' or answer == 'Yes'
                or args.no_checks):
        if len(args.id) > 0:
            if args.no_checks:
                delete_results_dir_params = ['--no_checks', '--id']
            else:
                delete_results_dir_params = ['--id']
            for delete_id in args.id:
                delete_results_dir_params.append(str(delete_id))
            delete_results_dir.delete_results_dir(
                    argv=delete_results_dir_params)
            for delete_id in args.id:
                db_cursor.execute(
                        "DELETE FROM runs WHERE id = {0}".format(delete_id))
        elif args.where:
            if args.no_checks:
                delete_results_dir.delete_results_dir(
                        argv=["--no_checks", "--where", args.where])
            else:
                delete_results_dir.delete_results_dir(
                        argv=["--where", args.where])
            db_cursor.execute("DELETE FROM runs WHERE {0}".format(args.where))
    else:
        print("No simulations were deleted.")

    db.commit()
    db_cursor.close()
    db.close()


if __name__ == '__main__':
    delete_sim("", sys.argv[0], sys.argv[1:])
