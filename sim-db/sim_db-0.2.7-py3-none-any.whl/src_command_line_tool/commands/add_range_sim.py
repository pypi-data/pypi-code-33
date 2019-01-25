#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Add a range of simulation to the database.

Work as 'add_sim' and add a simulation to the database with parameters in 
specified or dedused file, but does also add a simulation for each of the other
parameter values in specified range. 

The range is given by a list of specified column names ('--columns'/'-c'), the start value
from the parameter file, either a linear step ('--lin_steps') or
a exponential step ('--exp_steps') and either a end value ('--end_values') or a 
number of steps ('--n_steps'). 

The type of column MUST be a 'int' or a 'float'.

For '--lin_steps STEP' the next value is PREV_VALUE + STEP and for '--exp_steps'
the next value is PREV_VALUE * STEP.

Usage: 'python add_and_run.py --filename NAME_PARAM_FILE.TXT --lin_steps STEP
            --n_steps N'
"""
# Copyright (C) 2018-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

if __name__ == '__main__':
    import add_package_root_to_path

import sim_db.src_command_line_tool.commands.add_sim as add_sim
import sim_db.src_command_line_tool.commands.update_sim as update_sim
import sim_db.src_command_line_tool.commands.helpers as helpers
import sqlite3
import argparse
import sys


def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="add_range_sim"):
    parser = argparse.ArgumentParser(
            description='Add a range of simulations to the database.',
            prog="{0} {1} ".format(name_command_line_tool, name_command))
    parser.add_argument(
            '--filename',
            '-f',
            type=str,
            default=None,
            help="Name of parameter file added as the first in the range.")
    parser.add_argument(
            '--columns',
            '-c',
            type=str,
            nargs='+',
            required=True,
            default=[],
            help=
            ("<Required> Names of the column for which the range varies. "
             "The cartisian products of the varing columns are added to the "
             "database. The column type MUST be a integer or a float."))
    parser.add_argument(
            '--lin_steps',
            type=float,
            nargs='+',
            default=[],
            help=("Linear step distance. NEXT_STEP = PREV_STEP + LIN_STEP. If "
                  "columns have both linear and exponential steps, both will be "
                  "used. NEXT_STEP = LIN_STEP + PREV_STEP * EXP_STEP"))
    parser.add_argument(
            '--exp_steps',
            type=float,
            nargs='+',
            default=[],
            help=
            ("Exponential step distance. NEXT_STEP = PREV_STEP * EXP_STEP. "
             "If columns have both linear and exponential steps, both will be "
             "used. NEXT_STEP = LIN_STEP + PREV_STEP * EXP_STEP"))
    parser.add_argument(
            '--end_steps',
            type=float,
            nargs='+',
            default=[],
            help=
            ("End step of range. The range includes the end, but not "
             "anything past it. If both 'end_steps' and 'n_steps' are used, "
             "both endpoint need to be reached."))
    parser.add_argument(
            '--n_steps',
            type=int,
            nargs='+',
            default=[],
            help=
            ("Number of steps in the range. That means one step gives to "
             "simulations added. If both 'end_steps' and 'n_steps' are used, "
             "both endpoint need to be reached."))

    return parser


def add_range_sim(name_command_line_tool="sim_db",
                  name_command="add_range_sim",
                  argv=None):
    args = command_line_arguments_parser(name_command_line_tool,
                                         name_command).parse_args(argv)

    # Check command line arguments
    n_cols = len(args.columns)
    if ((len(args.lin_steps) != n_cols or len(args.exp_steps) != 0)
                and (len(args.lin_steps) != 0 or len(args.exp_steps) != n_cols)
                and
        (len(args.lin_steps) != n_cols or len(args.exp_steps) != n_cols)):
        print("ERROR: Either '--lin_steps', '--exp_steps' or both have to be provided "
              "and they have to be same length as '--columns'.")
        exit()
    elif ((len(args.end_steps) != n_cols or len(args.n_steps) != 0)
          and (len(args.end_steps) != 0 or len(args.n_steps) != n_cols)
          and (len(args.end_steps) != n_cols or len(args.n_steps) != n_cols)):
        print("ERROR: Either '--end_steps', '--n_steps' or both have to be provided "
              "and they have to be same length as '--columns'.")
        exit()

    ids_added = []
    if args.filename == None:
        ids_added.append(add_sim.add_sim())
    else:
        ids_added.append(add_sim.add_sim(argv=['--filename', args.filename]))

    # Get start value of each column that varies.
    db = helpers.connect_sim_db()
    db_cursor = db.cursor()

    start_values = []
    for column in args.columns:
        db_cursor.execute("SELECT {0} FROM runs WHERE id = {1}".format(
                column, ids_added[0]))
        start_values.append(db_cursor.fetchone()[0])

    db.commit()
    db_cursor.close()
    db.close()

    # Make table of the cartisian product.
    if len(args.lin_steps) == 0:
        args.lin_steps = [0 for i in range(n_cols)]
    if len(args.exp_steps) == 0:
        args.exp_steps = [1 for i in range(n_cols)]
    column_range = [[] for i in range(n_cols)]
    for i in range(n_cols):
        column_range[i].append(start_values[i])
        if len(args.end_steps) == 0:
            for j in range(args.n_steps[i]):
                column_range[i].append(column_range[i][-1] *
                                       args.exp_steps[i] + args.lin_steps[i])
        elif len(args.lin_steps) == 0:
            j = 0
            while (start_values[i] != args.end_steps[i]
                   and (start_values[i] < args.end_steps[i]) == (
                           column_range[i][j] < args.end_steps[i])):
                column_range[i].append(column_range[i][-1] *
                                       args.exp_steps[i] + args.lin_steps[i])
                j += 1
        else:
            j = 0
            while (j < args.n_steps[i]
                   or (start_values[i] != args.end_steps[i] and
                       (start_values[i] < args.end_steps[i]) ==
                       (column_range[i][j] < args.end_steps[i]))):
                column_range[i].append(column_range[i][-1] *
                                       args.exp_steps[i] + args.lin_steps[i])
                j += 1
    cartisian_product = [[] for i in range(n_cols)]
    for i in range(n_cols - 1, -1, -1):
        cartisian_product = add_new_column_in_cartisian_product(
                cartisian_product, column_range[i], i)

    # Add all simulations.
    for i in range(1, len(cartisian_product[0])):
        if args.filename == None:
            ids_added.append(add_sim.add_sim())
        else:
            ids_added.append(
                    add_sim.add_sim(argv=['--filename', args.filename]))
        update_params = ['--id', str(ids_added[-1]), '--columns']
        update_params.extend(args.columns)
        update_params.append('--values')
        for j in range(n_cols):
            update_params.append(str(cartisian_product[j][i]))
        update_sim.update_sim(argv=update_params)

    return ids_added


def add_new_column_in_cartisian_product(car_prod_table, new_col, col_no):
    prev_car_prod_table = list(car_prod_table)
    for i in range(col_no, len(car_prod_table)):
        car_prod_table[i] = []
    for val in new_col:
        if col_no < len(car_prod_table) - 1:
            car_prod_table[col_no].extend(
                    [val for i in range(len(prev_car_prod_table[col_no + 1]))])
            for i in range(col_no + 1, len(car_prod_table)):
                car_prod_table[i].extend(prev_car_prod_table[i])
        else:
            car_prod_table[col_no].append(val)
    return car_prod_table


if __name__ == '__main__':
    ids_added = add_range_sim("", sys.argv[0], sys.argv[1:])
    print("Added simulations with following ID's:")
    print(ids_added)
