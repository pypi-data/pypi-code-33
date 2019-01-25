#!/usr/bin/env python
# -* coding: utf-8 -*-
"""Delete results in 'results_dir' of specified simulation in the sim.db.

One must either provide a list of ID's or a condition to delete the results in 
'results_dir' as well as the directory itself of the corresponding simulations i
from the database.

Usage: python delete_results_dir.py -id 'ID'
       python delete_results_dir.py -where 'CONDITION'
"""
# Copyright (C) 2018-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

if __name__ == '__main__':
    import add_package_root_to_path

import sim_db.src_command_line_tool.commands.helpers as helpers
import argparse
import sys
import os
import errno
import shutil


def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="delete_results_dir"):
    parser = argparse.ArgumentParser(
            description=
            "Delete results in 'results_dir' of specified simulations.",
            prog="{0} {1}".format(name_command_line_tool, name_command))
    parser.add_argument(
            '--id',
            '-i',
            type=int,
            nargs='+',
            default=[],
            help="ID's of simulation which 'results_dir' to deleted.")
    parser.add_argument(
            '--where',
            '-w',
            type=str,
            default=None,
            help=
            ("Condition for which simulation's 'results_dir' to deleted. "
             "Must be a valid SQL (sqlite3) command when added after WHERE in "
             "a SELECT command."))
    parser.add_argument(
            '--no_checks',
            action='store_true',
            help=("No questions are asked about wheather you really want to "
                  "delete the 'results_dir' of specified simulation."))
    parser.add_argument(
            '--not_in_db_but_in_dir',
            type=str,
            default=None,
            help=
            ("Delete every folder in the specified directory that is not "
             "a 'results_dir' in the ', so use with care. Both relative and "
             "absolute paths can be used."))

    return parser


def delete_results_dir(name_command_line_tool="sim_db",
                       name_command="delete_results_dir",
                       argv=None):
    db = helpers.connect_sim_db()
    db_cursor = db.cursor()

    args = command_line_arguments_parser(name_command_line_tool,
                                         name_command).parse_args(argv)
    if (len(args.id) == 0 and args.where == None
                and args.not_in_db_but_in_dir == None):
        print("No 'results_dir' was deleted. --id 'ID' or --where 'CONDITION' "
              + "must be passed to the program.")
        exit(0)

    results_dirs = []
    for delete_id in args.id:
        db_cursor.execute("SELECT results_dir FROM runs WHERE id = {0}"
                          .format(delete_id))
        results_dir = db_cursor.fetchone()
        if results_dir != None and results_dir[0] != None:
            results_dirs.append(results_dir[0])

    if args.where:
        db_cursor.execute("SELECT results_dir FROM runs WHERE {0}"
                          .format(args.where))
        for selected_output in db_cursor.fetchall():
            if selected_output[0] != None:
                results_dirs.append(selected_output[0])

    if args.not_in_db_but_in_dir != None:
        db_cursor.execute("SELECT results_dir FROM runs")
        results_dir = db_cursor.fetchone()
        while results_dir != None and results_dir[0] != None:
            results_dirs.append(results_dir[0])
            results_dir = db_cursor.fetchone()

    db.commit()
    db_cursor.close()
    db.close()

    if args.not_in_db_but_in_dir != None:
        if not os.path.isabs(args.not_in_db_but_in_dir):
            if args.not_in_db_but_in_dir[0] == '.':
                args.not_in_db_but_in_dir = args.not_in_db_but_in_dir[2:]
            if args.not_in_db_but_in_dir[-1] == '/':
                args.not_in_db_but_in_dir = args.not_in_db_but_in_dir[:-1]
            args.not_in_db_but_in_dir = os.path.join(os.getcwd(),
                                                     args.not_in_db_but_in_dir)
        for path in os.listdir(args.not_in_db_but_in_dir):
            path = os.path.join(args.not_in_db_but_in_dir, path)
            if os.path.isdir(path) and (path not in results_dirs):
                print("\nDo you really want to delete:")
                print(path)
                answer = helpers.user_input("? (y/n)")
                if (answer == 'y' or answer == 'Y' or answer == 'yes'
                            or answer == 'Yes' or args.no_checks):
                    shutil.rmtree(path)
                else:
                    print(path)
                    print("was NOT deleted.")
    elif len(results_dirs) > 0:
        answer = 'no'
        if not args.no_checks:
            print("Do you really want to delete the following directories and "
                  "everything in them:")
            for results_dir in results_dirs:
                print(results_dir)
            answer = helpers.user_input("? (y/n)")
        if (answer == 'y' or answer == 'Y' or answer == 'yes'
                    or answer == 'Yes' or args.no_checks):
            for results_dir in results_dirs:
                try:
                    shutil.rmtree(results_dir)
                except Exception as e:
                    if e.errno == errno.ENOENT:
                        print("Results directory NOT found: {0}"
                              .format(results_dir))
                    else:
                        raise e
        elif not args.no_checks:
            print("No results deleted.")
    elif not args.no_checks:
        print("No 'results_dir' to delete.")


if __name__ == '__main__':
    delete_results_dir("", sys.argv[0], sys.argv[1:])
