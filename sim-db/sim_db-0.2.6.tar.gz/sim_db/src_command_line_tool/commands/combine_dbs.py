#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Combine two databases into one.

Combine two SQLite3 simulation databases after simulation have been run 
differnt places.

Usage:
    python combine_dbs.py 'sim_database_1.db' 'sim_database_2.db' 'new_name.db'
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
                                  name_command="combine_dbs"):
    parser = argparse.ArgumentParser(
            description='Combine two databases into a new one.',
            prog="{0} {1}".format(name_command_line_tool, name_command))
    parser.add_argument(
            'path_db_1', type=str, help="<Required> Path to ' database 1.")
    parser.add_argument(
            'path_db_2', type=str, help="<Required> Path to ' database 2.")
    parser.add_argument(
            'name_new_db',
            type=str,
            help="<Required> Name of the new database.")

    return parser


def combine_dbs(name_command_line_tool="sim_db",
                name_command="combine_dbs",
                argv=None):
    args = command_line_arguments_parser(name_command_line_tool,
                                         name_command).parse_args(argv)

    db_1 = helpers.connect_sim_db(args.path_db_1)
    db_1_cursor = db_1.cursor()
    db_2 = helpers.connect_sim_db(args.path_db_2)
    db_2_cursor = db_2.cursor()

    (columns_db_1,
     types_db_1) = helpers.get_db_column_names_and_types(db_1_cursor)
    (columns_db_2,
     types_db_2) = helpers.get_db_column_names_and_types(db_2_cursor)
    column_type_dict = OrderedDict(
            [(col, typ) for col, typ in zip(columns_db_1, types_db_1)] +
            [(col, typ) for col, typ in zip(columns_db_2, types_db_2)])

    new_db = helpers.connect_sim_db(args.name_new_db)
    new_db_cursor = new_db.cursor()
    new_db_columns_string = ""
    for col in column_type_dict:
        new_db_columns_string += col + " " + column_type_dict[col] + ", "
    new_db_columns_string = new_db_columns_string[:-2]
    new_db_columns_string = new_db_columns_string.replace(
            "id INTEGER", "id INTEGER PRIMARY KEY", 1)
    new_db_cursor.execute(
            "CREATE TABLE runs ({0});".format(new_db_columns_string))

    db_1_cursor.execute("SELECT * FROM runs")
    for row in db_1_cursor.fetchall():
        column_tuple = ()
        value_tuple = ()
        for column, value in zip(columns_db_1, row):
            column = helpers.if_unicode_convert_to_str(column)
            value = helpers.if_unicode_convert_to_str(value)
            if value != None and column != 'id':
                column_tuple += (column, )
                value_tuple += (value, )
        new_db_cursor.execute("INSERT INTO runs {0} VALUES {1}".format(
                column_tuple, value_tuple))

    db_2_cursor.execute("SELECT * FROM runs")
    for row in db_2_cursor.fetchall():
        column_tuple = ()
        value_tuple = ()
        for column, value in zip(columns_db_2, row):
            column = helpers.if_unicode_convert_to_str(column)
            value = helpers.if_unicode_convert_to_str(value)
            if value != None and column != 'id':
                column_tuple += (column, )
                value_tuple += (value, )
        new_db_cursor.execute("INSERT INTO runs {0} VALUES {1}".format(
                column_tuple, value_tuple))

    db_1.commit()
    db_2.commit()
    new_db.commit()
    db_1_cursor.close()
    db_2_cursor.close()
    new_db_cursor.close()
    db_1.close()
    db_2.close()
    new_db.close()


if __name__ == '__main__':
    combine_dbs("", sys.argv[0], sys.argv[1:])
