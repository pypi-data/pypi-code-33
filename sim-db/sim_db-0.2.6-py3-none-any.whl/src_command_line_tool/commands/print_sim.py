#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Print parameters of simulations ran or running, i.e. content of database.

Print the content of database with a number of possible restrictions.
"""
# Copyright (C) 2017-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

if __name__ == '__main__':
    import add_package_root_to_path

import sim_db.src_command_line_tool.commands.helpers as helpers
import sqlite3
import argparse
import shlex
import sys
import os


def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="print_sim"):
    parser = argparse.ArgumentParser(
            description=("Print content in sim.db. The default configuration "
                "corresponding to the '-p default' option is applied first, as "
                "long as the '--columns'/'-c' option is not passed. It can can "
                "however be overwritten, as only the last occcurence of any "
                "flag is used."),
            prog="{0} {1}".format(name_command_line_tool, name_command))
    parser.add_argument(
            '--id', '-i', type=int, nargs='+', help="List of ID's.")
    parser.add_argument(
            '--not_id',
            type=int,
            nargs='+',
            help="List of ID's not to print. Takes president over '--id'.")
    parser.add_argument(
            '-n', type=int, help="Number of row printed from the bottom up.")
    parser.add_argument(
            '--columns',
            '-c',
            type=str,
            nargs='+',
            default=None,
            help="Name of the columns to print.")
    parser.add_argument(
            '--not_columns',
            type=str,
            nargs='+',
            default=None,
            help=("Name of the columns not to print. Takes presidents over "
                  "'--columns'."))
    parser.add_argument(
            '--col_by_num',
            type=int,
            nargs='+',
            default=None,
            help=("Number of the columns to print. All non empty columns are "
                  "printed by default."))
    parser.add_argument(
            '--where',
            '-w',
            default='id > -1',
            help=
            ("Add constraints to which columns to print. Must be a valid "
             "SQL (sqlite3) command when added after WHERE in a SELECT command."
             ))
    parser.add_argument(
            '--sort_by',
            default='id',
            help=
            ("What to sort the output by. Must be a valid SQL (sqlite3) "
             "command when added after ORDER BY in a SELECT search. Defalut is "
             "id."))
    parser.add_argument(
            '--column_names',
            action='store_true',
            help="Print name and type of all columns.")
    parser.add_argument(
            '--all_columns',
            action='store_true',
            help="Print all columns. Takes president over '--not_columns'.")
    parser.add_argument(
            '--empty_columns',
            action='store_true',
            help=("Print empty columns. Otherwise only non empty columns are "
                  "printed."))
    parser.add_argument(
            '--params',
            action='store_true',
            help=("Print the parameters added before the simulation run."))
    parser.add_argument(
            '--results',
            action='store_true',
            help=("Print results - the parameters added during the simulation, "
                  "excluding metadata."))
    parser.add_argument(
            '--metadata',
            action='store_true',
            help=("Print metadata. '--params', '--results' and '--metadata' "
                  "will together print all non empty columns."))
    parser.add_argument(
            '--no_headers',
            action='store_true',
            help="Print without any headers.")
    parser.add_argument(
            '--max_width',
            type=int,
            default=None,
            help=("Upper limit for the width of each column. Default is no "
                  "limit."))
    parser.add_argument(
            '--first_line',
            action='store_true',
            help="Print only the first line of any entry.")
    parser.add_argument(
            '--vertically',
            '-v',
            action='store_true',
            help="Print columns vertically.")
    parser.add_argument(
            '-p',
            type=str,
            default=None,
            help=
            ("Personal print configuration. Substituted with the print "
             "configuration in 'settings.txt' corresponding to the provided "
             "key string."))
    parser.add_argument(
            '--diff',
            '-d',
            action='store_true',
            help=
            ("Remove columns with the same value for all the "
             "simulations. This leaves only the parameters that are different "
             "between the simulations."))

    return parser


def get_personalized_print_config(key_string):
    settings = helpers.Settings()
    print_configs = settings.read('print_config')
    for line in print_configs:
        split_line = line.split(':')
        if len(split_line) > 1:
            if key_string.strip() == split_line[0].strip():
                return split_line[1].strip()
    return None

metadata_columns = ['status', 'add_to_job_script', 'max_walltime', 'n_tasks',
                    'job_id', 'time_submitted', 'time_started', 'used_walltime',
                    'cpu_info', 'git_hash', 'commit_message', 'git_diff',
                    'git_diff_stat', 'sha1_executables', 'initial_parameters']

def get_initial_parameters_columns(db_cursor, args):
    ids = []
    if args.where != None:
        try:
            db_cursor.execute("SELECT id FROM runs WHERE {0};".format(args.where))
        except sqlite3.OperationalError as e:
            if str(e) == "no such table: runs":
                print("There does NOT exist a database yet.\n"
                      "Try adding a simulation from a parameter file.")
                exit(1)
            else:
                raise e
        ids = [id_tuple[0] for id_tuple in db_cursor.fetchall()]
    if args.id != None:
        if len(ids) > 0:
            ids = [i for i in ids if i in args.id]
        else:
            ids = args.id
    all_initial_parameters = []
    for i in ids:
        db_cursor.execute("SELECT initial_parameters FROM runs WHERE id={0}"
                          .format(i))
        initial_parameters = db_cursor.fetchone()[0]
        if initial_parameters != None:
            initial_parameters, correct_type = (
                    helpers.convert_text_to_correct_type(
                            initial_parameters, 'string array'))
            all_initial_parameters = all_initial_parameters + initial_parameters
    all_initial_parameters = list(set(all_initial_parameters))

    return all_initial_parameters


def add_columns(new_columns, columns, column_names):
    for col in new_columns:
        if col not in column_names:
            column_names.append(col)
            columns += ", {0}".format(col)
    if len(columns) > 2 and columns[0:2] == ", ":
        columns = columns[2:]
    return (columns, column_names)


def select_command(name_command_line_tool, name_command, db_cursor, args,
                   all_column_names):
    columns = ""
    column_names = []

    if args.columns != None:
        columns, column_names = add_columns(args.columns, columns,
                                            column_names)
    if args.col_by_num != None:
        new_columns = [all_column_names[i] for i in args.col_by_num]
        columns, column_names = add_columns(new_columns, columns, column_names)
    if args.params:
        parameter_columns = get_initial_parameters_columns(db_cursor, args)
        columns, column_names = add_columns(parameter_columns, columns,
                                            column_names)
    if args.results:
        parameter_columns = get_initial_parameters_columns(db_cursor, args)
        result_columns = [
                c for c in all_column_names
                if (c not in parameter_columns and c not in metadata_columns)
        ]
        columns, column_names = add_columns(result_columns, columns,
                                            column_names)
    if args.metadata:
        columns, column_names = add_columns(metadata_columns, columns,
                                            column_names)
    if columns == "" or args.all_columns:
        columns = '*'
        column_names = all_column_names

    for col in column_names:
        if col not in all_column_names:
            print("ERROR: {0} is NOT a column in the database.\n"
                  "Run command '{1} {2} --column_names' to see all the columns "
                  "in the database.".format(col, name_command_line_tool,
                  name_command))
            exit(1)
    if args.id == None:
        try:
            db_cursor.execute("SELECT {0} FROM runs WHERE {1} ORDER BY {2};"
                              .format(columns, args.where, args.sort_by))
        except sqlite3.OperationalError as e:
            if str(e) == "no such table: runs":
                print("There do NOT exists a database yet.\n"
                      "Try adding a simulation from a parameter file.")
                exit(1)
            else:
                raise e
        selected_output = db_cursor.fetchall()
    else:
        selected_output = []
        for i in args.id:
            restrictions = args.where + " AND id = {0}".format(i)
            try:
                db_cursor.execute(
                        "SELECT {0} FROM runs WHERE {1} ORDER BY {2};".format(
                                columns, restrictions, args.sort_by))
            except sqlite3.OperationalError as e:
                if str(e) == "no such table: runs":
                    print("There do NOT exists a database yet.\n"
                          "Try adding a simulation from a parameter file.")
                    exit(1)
                else:
                    raise e
            output = db_cursor.fetchall()
            if len(output) == 0:
                if (len(restrictions) > 12
                            and restrictions[0:12] == 'id > -1 AND '):
                    restrictions = restrictions[12:]
                print("There exists no entries in the database with: {0}"
                      .format(restrictions))
                exit(1)
            selected_output.append(output[0])

    selected_output = [list(row) for row in selected_output]
    if (not args.all_columns and not args.empty_columns):
        selected_output, column_names = remove_empty_columns(
                selected_output, column_names, args)
    if (args.not_columns != None and not args.all_columns):
        selected_output, column_names = remove_columns_not_to_print(
                selected_output, column_names, args.not_columns)
    if args.not_id != None:
        selected_output = remove_rows_not_to_print(selected_output,
                                                   args.not_id)
    n = args.n
    if n == None:
        n = len(selected_output)
    selected_output = selected_output[-n:]

    return selected_output, column_names


def remove_empty_columns(selected_output, column_names, args):
    columns_not_to_remove = []
    if args.columns != None:
        columns_not_to_remove = args.columns
    if args.col_by_num != None:
        columns_by_num = [all_column_names[i] for i in args.col_by_num]
        columns_not_to_remove = columns_not_to_remove + columns_by_num
    if len(selected_output) == 0:
        return selected_output, column_names
    columns_to_remove = []
    for col in range(len(selected_output[0])):
        if (all(elem is None for elem in [row[col] for row in selected_output])
                and column_names[col] not in columns_not_to_remove):
            columns_to_remove.append(col)
    n_deleted = 0
    for col in columns_to_remove:
        for row in selected_output:
            del row[col - n_deleted]
        del column_names[col - n_deleted]
        n_deleted += 1

    return selected_output, column_names


def remove_columns_not_to_print(selected_output, column_names,
                                not_columns):
    if len(selected_output) == 0:
        return selected_output, column_names
    columns_to_remove = []
    for i, col_name in enumerate(column_names):
        for col_name_no_print in not_columns:
            if col_name == col_name_no_print:
                columns_to_remove.append(i)
    n_deleted = 0
    for col in columns_to_remove:
        for row in selected_output:
            del row[col - n_deleted]
        del column_names[col - n_deleted]
        n_deleted += 1
    return selected_output, column_names


def remove_rows_not_to_print(selected_output, not_id):
    rows_to_remove = []
    for j in range(len(selected_output)):
        for i in not_id:
            if selected_output[j][0] == i:
                rows_to_remove.append(j)
    n_deleted = 0
    for j in rows_to_remove:
        del selected_output[j - n_deleted]
        n_deleted += 0
    return selected_output


def get_max_widths(selected_output, column_names, no_headers, extra_space):
    if len(selected_output) == 0:
        return selected_output
    widths = []
    for col in range(len(selected_output[0])):
        if no_headers:
            max_width = 0
        else:
            max_width = len(column_names[col])
        for row in range(len(selected_output)):
            if max_width < len(str(selected_output[row][col]).split('\n')[0]):
                max_width = len(str(selected_output[row][col]).split('\n')[0])
        widths.append(max_width + extra_space)
    return widths


def remove_columns_with_only_same_values(selected_output, column_names):
    column_indices_to_remove = []
    for column_index in range(len(column_names)):
        remove_column = True
        for row_index in range(len(selected_output) - 1):
            if (selected_output[row_index][column_index] !=
                        selected_output[row_index + 1][column_index]):
                remove_column = False
                break
        if remove_column:
            column_indices_to_remove.append(column_index)
    for i in reversed(column_indices_to_remove):
        del column_names[i]
        for row in range(len(selected_output)):
            del selected_output[row][i]
    return selected_output, column_names


def print_selected_parameters(selected_output, column_names, no_headers,
                              max_width, first_line):
    extra_space = 2
    widths = get_max_widths(selected_output, column_names, no_headers,
                            extra_space)
    if not no_headers:
        headers = ""
        total_width = 0
        for w, col in zip(widths, column_names):
            column_header = col + (w - len(col)) * " "
            if max_width and w > max_width:
                column_header = column_header[:max_width] + extra_space * " "
                total_width += max_width + extra_space
            else:
                total_width += w
            headers += column_header
        print(headers)
        print(total_width * "=")
    for row in selected_output:
        line = ""
        for w, value in zip(widths, row):
            column_value = str(value) + (w - len(str(value))) * " "
            if first_line:
                column_value = column_value.split('\n')[0]
            if max_width and w > max_width:
                column_value = column_value[:max_width] + extra_space * " "
            line += column_value
        print(line)


def print_selected_parameters_vertically(selected_output, column_names,
                                         no_headers, max_width, first_line):
    extra_space = 2
    new_columns = []
    widths = []
    n_new_columns = len(selected_output)
    new_columns = [[] for i in range(n_new_columns)]
    widths = n_new_columns * [0]
    for i, row in enumerate(selected_output):
        for value in row:
            if first_line:
                value = str(value).split('\n')[0]
            new_columns[i].append(str(value))
            width = len(str(value))
            if max_width != None and width > max_width:
                width = max_width
            if widths[i] < width:
                widths[i] = width

    width_headers = 0
    for column_name in column_names:
        width = len(column_name)
        if max_width != None and width > max_width:
            width = max_width
        if width_headers < width:
            width_headers = width

    n_new_rows = 0
    if len(new_columns) > 0:
        n_new_rows = len(new_columns[0])
    for i in range(n_new_rows):
        if not no_headers:
            sys.stdout.write(
                    "{1:<{0}}".format(width_headers + extra_space,
                                      column_names[i][:width_headers]))
        for j in range(n_new_columns):
            sys.stdout.write("{1:<{0}}".format(widths[j] + extra_space,
                                               new_columns[j][i][:widths[j]]))
        sys.stdout.write("\n\n")
        sys.stdout.flush()


def replace_element_in_list(the_list, element, replacement):
    for i in the_list:
        if i == element:
            the_list.remove(element)
            the_list.append(replacement)
    return the_list


def print_sim(name_command_line_tool="sim_db",
              name_command="print_sim",
              argv=None):
    if argv == None:
        argv = ['-p', 'default']
    elif '--columns' not in argv and '-c' not in argv:
        if len(argv) > 0 and argv[0][0] != '-':
            # To print correct error message even though '-p default' is added.
            command_line_arguments_parser(name_command_line_tool,
                                          name_command).parse_args(argv)
        argv = ['-p', 'default'] + argv
    argv_p_replaced = []
    i = 0
    while i < len(argv):
        if argv[i] != '-p':
            argv_p_replaced.append(argv[i])
        else:
            while i + 1 < len(argv) and argv[i + 1][0] != '-':
                i += 1
                print_config_key = argv[i]
                print_config = get_personalized_print_config(print_config_key)
                if print_config == None:
                    print("No personalized print configuration with key string "
                          "'{0}' is found in settings.".format(
                          print_config_key))
                    exit(1)
                argv_p_replaced = argv_p_replaced + shlex.split(print_config)
        i += 1
    argv = argv_p_replaced
    args = command_line_arguments_parser(name_command_line_tool,
                                         name_command).parse_args(argv)

    db = helpers.connect_sim_db()
    db_cursor = db.cursor()

    column_names, column_types = helpers.get_db_column_names_and_types(
            db_cursor)
    type_dict = dict(zip(column_names, column_types))

    selected_output, column_names = select_command(name_command_line_tool,
        name_command, db_cursor, args, column_names)

    if args.diff:
        selected_output, column_names = remove_columns_with_only_same_values(
                selected_output, column_names)

    if not args.vertically:
        print_selected_parameters(selected_output, column_names,
                                  args.no_headers, args.max_width,
                                  args.first_line)
    else:
        print_selected_parameters_vertically(selected_output, column_names,
                                             args.no_headers, args.max_width,
                                             args.first_line)

    if args.column_names:
        print("")
        print("Column names and types in database:")
        for col_name in column_names:
            col_type = type_dict[col_name]
            print("{0}, {1}".format(col_name, col_type))

    db.commit()
    db_cursor.close()
    db.close()


if __name__ == '__main__':
    print_sim("", sys.argv[0], sys.argv[1:])
