#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Add simulation parameters to a sqlite3 database from a text file.

Name of the parameter file can be passed to the program, otherwise first match
with parameter file from 'settings.txt' is used.

The format of the parameter file is for each parameter as following:
parameter_name (type): parameter_value
'type' can be int, float, string, bool or int/float/string/bool array.
Lines without any colon is ignored.
Aliases can also be defined as:
string_to_replace (alias): string_to_replace with

The database used is the one which path given in 'settings.txt', closest 
matches the currect directory.

Usage: 'python add_sim.py' or 'python add_sim.py -filename name_param_file.txt'
"""
# Copyright (C) 2017-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

if __name__ == '__main__':
    import add_package_root_to_path

import sim_db.src_command_line_tool.commands.helpers as helpers
import sqlite3
import argparse
import sys
import os
import subprocess


def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="add_sim"):
    parser = argparse.ArgumentParser(
            description='Add simulation to database.',
            prog="{0} {1}".format(name_command_line_tool, name_command))
    parser.add_argument(
            '--filename',
            '-f',
            type=str,
            default=None,
            help="Name of parameter file added and submitted.")

    return parser


def split_parameter_line(line, i):
    line_split = line.split(':', 1)
    try:
        value = line_split[1].strip()
        param_name, param_type = line_split[0].split('(')
        param_name = param_name.strip()
        param_type = param_type.split(')')[0].strip()
    except ValueError:
        print("Parameter on line no. {0} in the parameter file has INCORRECT "
              "format of type and parentheses.".format(i))
        exit(1)
    return param_name, param_type, value


def add_new_column(db_cursor, i, param_type, param_name, value, column_names,
                   column_types):
    if param_type == 'int':
        db_cursor.execute("ALTER TABLE runs ADD COLUMN {0} INTEGER"
                          .format(param_name))
        column_names.append(param_name)
        column_types.append("INTEGER")
    elif param_type == 'float':
        db_cursor.execute("ALTER TABLE runs ADD COLUMN {0} REAL"
                          .format(param_name))
        column_names.append(param_name)
        column_types.append("REAL")
    elif param_type == 'string':
        db_cursor.execute("ALTER TABLE runs ADD COLUMN {0} TEXT"
                          .format(param_name))
        column_names.append(param_name)
        column_types.append("TEXT")
    elif param_type == 'bool':
        db_cursor.execute("ALTER TABLE runs ADD COLUMN {0} TEXT"
                          .format(param_name))
        column_names.append(param_name)
        column_types.append("TEXT")
    elif len(param_type) > 5 and param_type[-5:] == 'array':
        db_cursor.execute("ALTER TABLE runs ADD COLUMN {0} TEXT"
                          .format(param_name))
        array_type = param_type[:-5].strip()
        if (array_type != 'int' and array_type != 'float'
                and array_type != 'string' and array_type != 'bool'):
            print("Parameter on line no. {0} in parameter file has INVALID "
                  "type of array.".format(i))
        if len(value) > 0 and (value[0] != '[' or value[-1] != ']'):
            print("Parameter on line no. {0} in the parameter file has "
                  "INCORRECT format for arrays. Square brackets missing."
                  .format(i))
            exit(1)
        column_names.append(param_name)
        column_types.append("TEXT")
    else:
        print("Parameter on line no. {0} in the parameter file has an "
              "INVALID type.".format(i))
        exit(1)


def check_type_matches(param_type, column_type, value, i):
    correct_type = False
    if column_type == 'INTEGER' and (param_type == 'int'
                                     or param_type == 'bool'):
        correct_type = True
    elif column_type == 'REAL' and param_type == 'float':
        correct_type = True
    elif column_type == 'TEXT':
        if param_type == 'string':
            correct_type = True
        elif param_type == 'bool':
            correct_type = True
        elif len(param_type) > 5 and param_type[-5:] == 'array':
            array_type = param_type[:-5].strip()
            if (array_type == 'int' or array_type == 'float'
                    or array_type == 'string' or array_type == 'bool'):
                correct_type = True
            if len(value) > 0 and (value[0] != '[' or value[-1] != ']'):
                print("Parameter on line no. {0} in the parameter file has "
                      "INCORRECT format for arrays. Square brackets missing."
                      .format(i))
                exit(1)
    if not correct_type:
        print("Parameter on line no. {0} in the parameter file has an "
              "INVALID type.".format(i))
        exit(1)


def standardize_value(value, param_type):
    if param_type == 'bool':
        if value == "False" or value == "false" or value == "FALSE" or value == 0:
            value = "False"
        else:
            value = "True"
    type_split = param_type.split()
    if len(type_split
           ) > 1 and type_split[0] == 'bool' and type_split[1] == 'array':
        array = value[1:-1].split(',')
        new_array = "["
        for i in array:
            i = i.strip()
            if i == "False" or i == "false" or i == "FALSE" or i == "0":
                new_array += "False, "
            else:
                new_array += "True, "
        new_array = new_array[:-2]
        new_array += ']'
        value = new_array
    if (param_type == 'string array'):
        strings = value[1:-1].split(',')
        value = "["
        for i in range(len(strings)):
            string = strings[i]
            while (string.strip()[0] == '"' and string.strip()[-1] != '"'):
                i += 1
                string += string[i]
            while (string.strip()[0] == "'" and string.strip()[-1] != "'"):
                i += 1
                string += string[i]
            string = string.strip()
            if ((string[0] == '"' and string[-1] == '"')
                or (string[0] == "'" and string[-1] == "'")):
                string = string[1:-1]
            value += string + ', '
        if len(strings) > 0:
            value = value[:-2] + ']'
    if len(type_split) > 1 and type_split[1] == 'array' and len(value) > 0:
        value = type_split[0] + value
    if (param_type == 'string' or param_type == 'bool'
            or (len(param_type) > 5 and param_type[-5:] == 'array')):
        if len(value) > 0:
            if not ((value[0] == "'" and value[-1] == "'") or
                    (value[0] == '"' and value[-1] == '"')):
                value = "'" + value + "'"

    return value


def insert_value(db_cursor, param_name, last_row_id, value):
    if last_row_id:
        db_cursor.execute("UPDATE runs SET {0} = {1} WHERE id = {2};"
                          .format(param_name, value, last_row_id))
    else:
        db_cursor.execute("INSERT INTO runs (status, {0}) VALUES ('new', {1});"
                          .format(param_name, value))
        last_row_id = db_cursor.lastrowid
    return last_row_id


def make_path_relative_to_root(run_command, sim_params_filename):
    """Make all paths starting with './' relative to projects root directory."""
    sim_params_filename = os.path.join(os.getcwd(), sim_params_filename)
    split_sim_params_dir = os.path.split(os.path.dirname(sim_params_filename))
    split_dot_dir = os.path.split(helpers.get_dot_sim_db_dir_path())
    i = 0
    while (i < len(split_sim_params_dir) and i < len(split_dot_dir)
           and split_sim_params_dir[i] == split_dot_dir[i]):
        i += 1
    rel_path = ""
    for j in range(len(split_dot_dir) - i - 1):
        rel_path = os.path.join(rel_path, os.pardir)
    for dir_name in split_sim_params_dir[i:]:
        rel_path += dir_name + os.sep

    run_command = run_command.replace(' ./', ' root/' + rel_path)
    return run_command


def search_for_parameter_file_matching_settings():
    files_in_current_dir = os.listdir('.')
    for parameter_filename in helpers.Settings().read('parameter_files'):
        if parameter_filename in files_in_current_dir:
            return parameter_filename
    return None


def get_line_number_of_first_included_parameter_file(sim_params_file_lines):
    for i, line in enumerate(sim_params_file_lines):
        line_split = line.split(':', 1)
        if (
                len(line_split) > 1
                and (line_split[0].strip() == "include_parameter_file"
                     or line_split[0].strip() == "include parameter file")):
            return i
    return None


def add_included_parameter_files(sim_params_file_lines):
    i = get_line_number_of_first_included_parameter_file(sim_params_file_lines)
    while i != None:
        filename = sim_params_file_lines[i].split(':', 1)[1].strip()
        if (len(filename) > 5 and filename[0:5] == 'root/'):
            proj_root_dir = os.path.abspath(
                    os.path.join(helpers.get_dot_sim_db_dir_path(), os.pardir))
            filename = os.path.join(proj_root_dir, filename[5:])
        try:
            included_sim_params_file = open(filename, 'r')
        except:
            print("Could NOT open {0}.".format(filename))
            exit(1)
        included_sim_params_file_lines = included_sim_params_file.readlines()
        included_sim_params_file.close()
        del sim_params_file_lines[i]
        for line in included_sim_params_file_lines:
            sim_params_file_lines.insert(i, line)
            i += 1
        i = get_line_number_of_first_included_parameter_file(
                sim_params_file_lines)
    return sim_params_file_lines


def add_if_alias(line, aliases, i):
    line_have_type = True
    if ':' in line:
        string_to_replace, param_type, replacement_string = (
            split_parameter_line(line, i))
    else:
        return False
    if param_type == 'alias':
        if (len(string_to_replace) < 2
            or string_to_replace[0] != '{' or string_to_replace[-1] != '}'):
            print("ERROR: Alias name on line no. {0} in the parameter file "
                  "MUST start and end with curly brackets.".format(i))
            print("E.g.: '{string_to_replace} (alias): replacement_string'")
            exit(1)
        if ((replacement_string[0] == '"' and replacement_string[-1] == '"')
             or (replacement_string[0] == "'"
                 and replacement_string[-1] == "'")):
            replacement_string = replacement_string[1:-1]
        for alias, replacement in aliases:
            replacement_string = replacement_string.replace(alias, replacement)
        aliases.append((string_to_replace, replacement_string))
        return True
    else:
        return False


def replace_aliases(sim_params_file_lines):
    aliases = []
    new_sim_params_file_lines = []
    for i, line in enumerate(sim_params_file_lines):
        if not add_if_alias(line, aliases, i):
            for alias, replacement in aliases:
                line = line.replace(alias, replacement)
            new_sim_params_file_lines.append(line)
    return new_sim_params_file_lines


def add_sim(name_command_line_tool="sim_db", name_command="add", argv=None):
    db = helpers.connect_sim_db()

    args = command_line_arguments_parser(name_command_line_tool,
                                         name_command).parse_args(argv)
    sim_params_filename = args.filename
    if sim_params_filename == None:
        sim_params_filename = search_for_parameter_file_matching_settings()
        if sim_params_filename == None:
            print("No parameter files in the current directory matches the "
                  "ones under 'Parameter filenames'\nin settings.txt.\n"
                  "\nAdd the '--filename' flag to specify the filename of "
                  "the parameter file.")
            exit(1)
    elif (sim_params_filename[0:5] == 'root/'):
        sim_params_filename = os.path.join(
                os.path.join(helpers.get_dot_sim_db_dir_path(), os.pardir),
                sim_params_filename[5:])
    elif (sim_params_filename[0:6] == '"root/'):
        sim_params_filename = '"' + os.path.join(
                os.path.join(helpers.get_dot_sim_db_dir_path(), os.pardir),
                sim_params_filename[6:])

    try:
        sim_params_file = open(sim_params_filename, 'r')
    except:
        print("Could NOT open {0}.".format(sim_params_filename))
        exit(1)

    sim_params_file_lines = sim_params_file.readlines()
    sim_params_file.close()

    sim_params_file_lines = add_included_parameter_files(sim_params_file_lines)
    sim_params_file_lines = replace_aliases(sim_params_file_lines)

    db_cursor = db.cursor()
    default_db_columns = ""
    for key in helpers.default_db_columns:
        default_db_columns += key + " " + str(
                helpers.default_db_columns[key]) + ", "
    default_db_columns = default_db_columns[:-2]
    db_cursor.execute("CREATE TABLE IF NOT EXISTS runs ({0});".format(
            default_db_columns))

    column_names, column_types = helpers.get_db_column_names_and_types(
            db_cursor)

    initial_parameters = []

    last_row_id = None
    for i, line in enumerate(sim_params_file_lines):
        if len(line.split(':')) > 1:
            param_name, param_type, value = split_parameter_line(line, i)
            initial_parameters.append(param_name)

            if param_name == 'run_command':
                value = make_path_relative_to_root(value, sim_params_filename)

            try:
                row_index = column_names.index(param_name)
            except ValueError:
                row_index = None

            if row_index is None:
                add_new_column(db_cursor, i, param_type, param_name, value,
                               column_names, column_types)
            else:
                check_type_matches(param_type, column_types[row_index], value,
                                   i)

            value = standardize_value(value, param_type)
            if len(value) > 0:
                last_row_id = insert_value(db_cursor, param_name, last_row_id,
                                           value)
    initial_parameters = standardize_value(str(initial_parameters), "string array")
    last_row_id = insert_value(db_cursor, 'initial_parameters', last_row_id,
                               initial_parameters)

    db.commit()
    db_cursor.close()
    db.close()

    return last_row_id


if __name__ == '__main__':
    last_id = add_sim("", sys.argv[0], sys.argv[1:])
    print("ID of last added: {0}".format(last_id))
