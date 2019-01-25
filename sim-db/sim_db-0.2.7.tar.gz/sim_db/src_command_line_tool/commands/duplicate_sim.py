#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Duplicate a set of simulation parameters found in s database.

The 'ID' of a set of simulation parameters if passed to 'duplicate_sim.py' and
a new set of almost identically simulation parameters will be created. The only
parameters that are NOT identical is the 'id', which will be unique, and 
'status', which will be set to 'new'.

Usage: 'python duplicate_sim.py --id ID' or 'python add_sim.py -i ID'
"""
# Copyright (C) 2018-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

if __name__ == '__main__':
    import add_package_root_to_path

import sim_db.src_command_line_tool.commands.helpers as helpers
import sqlite3
import argparse
import sys


def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="duplicate_sim"):
    parser = argparse.ArgumentParser(
            description=
            ("Duplicate simulation in database. All parameters "
             "(including possible results) of specified simulation is "
             "duplicated with the exception of 'id' and 'status', which is "
             "kept unique and set to 'new' respectfully."),
            prog="{0} {1} ".format(name_command_line_tool, name_command))
    parser.add_argument(
            '--id',
            '-i',
            type=int,
            required=True,
            help=("<Required> 'ID' of the simulation parameters in the "
                  "'sim.db' database that should be duplicated."))

    return parser


def duplicate_sim(name_command_line_tool="sim_db",
                  name_command="duplicate_sim",
                  argv=None):
    args = command_line_arguments_parser(name_command_line_tool,
                                         name_command).parse_args(argv)

    db = helpers.connect_sim_db()
    db_cursor = db.cursor()

    db_cursor.execute("CREATE TEMPORARY TABLE tmp AS SELECT * FROM runs WHERE "
                      "id = {0};".format(args.id))
    db_cursor.execute("UPDATE tmp SET id = NULL;")
    db_cursor.execute("UPDATE tmp SET status = 'new';")
    db_cursor.execute("INSERT INTO runs SELECT * FROM tmp;")
    db_id = db_cursor.lastrowid
    db_cursor.execute("DROP TABLE tmp")

    db.commit()
    db_cursor.close()
    db.close()

    return db_id


if __name__ == '__main__':
    db_id = duplicate_sim("", sys.argv[0], sys.argv[1:])
    print("ID of new simulation: {0}".format(db_id))
