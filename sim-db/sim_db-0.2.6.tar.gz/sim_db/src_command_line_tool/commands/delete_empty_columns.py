#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Delete all empty columns in the sim.db, except the default ones.

Usage: python delete_empty_columns.py
"""
# Copyright (C) 2018-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

if __name__ == '__main__':
    import add_package_root_to_path

import sim_db.src_command_line_tool.commands.helpers as helpers
import sqlite3
import argparse
import sys
from collections import OrderedDict


def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="delete_empty_columns"):
    parser = argparse.ArgumentParser(
            description=
            "Delete all empty columns in the sim.db, except the default ones.",
            prog="{0} {1}".format(name_command_line_tool, name_command))

    return parser


def delete_empty_columns(name_command_line_tool="sim_db",
                         name_command="delete_empty_columns",
                         argv=None):
    command_line_arguments_parser(name_command_line_tool,
                                  name_command).parse_args(argv)

    db = helpers.connect_sim_db()
    db_cursor = db.cursor()

    column_names, column_types = helpers.get_db_column_names_and_types(
            db_cursor)
    new_table_dict = OrderedDict()
    for column_name, column_type in zip(column_names, column_types):
        db_cursor.execute("SELECT {0} FROM runs;".format(column_name))
        values = db_cursor.fetchall()
        is_empty = True
        for value in values:
            if value != (None, ):
                is_empty = False
                break
        if not is_empty or (column_name in helpers.default_db_columns):
            new_table_dict[column_name] = column_type

    new_columns_and_types = ""
    new_columns = ""
    for column_name in new_table_dict:
        new_columns_and_types += column_name + " " + new_table_dict[column_name] + ", "
        new_columns += column_name + ", "
    new_columns_and_types = new_columns_and_types[:-2]
    new_columns = new_columns[:-2]

    assert new_columns_and_types[0:2] == 'id', (
            "Name of first column in database is not 'id'.")
    new_columns_and_types = new_columns_and_types[0:10] + " PRIMARY KEY" \
            +new_columns_and_types[10:] # Correct id type

    db_cursor.execute("CREATE TABLE IF NOT EXISTS new_runs ({0});".format(
            new_columns_and_types))

    db_cursor.execute(
            "INSERT INTO new_runs SELECT {0} FROM runs;".format(new_columns))

    db_cursor.execute("DROP TABLE runs;")
    db_cursor.execute("ALTER TABLE new_runs RENAME TO runs;")

    db.commit()
    db_cursor.close()
    db.close()


if __name__ == '__main__':
    delete_empty_columns("", sys.argv[0], sys.argv[1:])
