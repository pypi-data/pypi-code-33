#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Add simulation parameters to the database and submit it to job scheduler.

Name of the parameter file can be passed to the program, otherwise first match
with parameter file from 'settings.txt' is used.

The format of the parameter file is for each parameter as following:
parameter_name (type): parameter_value
'type' can be int, float, string, bool or int/float/string/bool array.
Lines without any colon is ignored.

The database used is the one which path given in 'settings.txt', closest 
matches the currect directory.

Usage: 'python add_and_submit.py' 
    or 'python add_and_submit.py -filename name_param_file.txt
"""
# Copyright (C) 2017-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

if __name__ == '__main__':
    import add_package_root_to_path

import sim_db.src_command_line_tool.commands.add_sim as add_sim
import sim_db.src_command_line_tool.commands.submit_sim as submit_sim
import argparse
import sys


def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="add_and_submit"):
    parser = argparse.ArgumentParser(
            description='Add simulation and submit it.',
            prog="{0} {1}".format(name_command_line_tool, name_command))
    parser.add_argument(
            '--filename',
            '-f',
            type=str,
            default=None,
            help="Name of parameter file added and submitted.")
    parser.add_argument(
            '--max_walltime',
            type=str,
            default=None,
            help=("Maximum walltime the simulation can use, given in "
                  "'hh:mm:ss' format."))
    parser.add_argument(
            '--n_tasks',
            type=int,
            default=None,
            help=
            ("Number of tasks to run the simulation with. A warning is "
             "given if it is not a multiple of the number of logical cores on "
             "a node."))
    parser.add_argument(
            '--n_nodes',
            type=int,
            default=None,
            help="Number of nodes to run the simulation on.")
    parser.add_argument(
            '--additional_lines',
            type=str,
            default=None,
            help="Additional lines added to the job script.")
    parser.add_argument(
            '--notify_all',
            action='store_true',
            help=("Set notification for when simulation begins and ends or if "
                  "it fails."))
    parser.add_argument(
            '--notify_fail',
            action='store_true',
            help="Set notification for if simulation fails.")
    parser.add_argument(
            '--notify_end',
            action='store_true',
            help="Set notification for when simulation ends or if it fails.")
    parser.add_argument(
            '--no_confirmation',
            action='store_true',
            help=("Does not ask for confirmation about submitting all "
                  "simulations "
                  "with status 'new'"))
    parser.add_argument(
            '--do_not_submit_job_script',
            action='store_true',
            help="Makes the job script, but does not submit it.")

    return parser


def add_and_submit(name_command_line_tool="sim_db",
                   name_command="add_and_submit",
                   argv=None):
    args = command_line_arguments_parser(name_command_line_tool,
                                         name_command).parse_args(argv)

    if args.filename == None:
        added_id = add_sim.add_sim()
    else:
        added_id = add_sim.add_sim(argv=['--filename', args.filename])

    submit_parameters = ["--id", str(added_id)]
    if args.max_walltime != None:
        submit_parameters.append("--max_walltime")
        submit_parameters.append(args.max_walltime)
    if args.n_tasks != None:
        submit_parameters.append("--n_tasks")
        submit_parameters.append(str(args.n_tasks))
    if args.n_nodes != None:
        submit_parameters.append("--n_nodes")
        submit_parameters.append(str(args.n_nodes))
    if args.additional_lines != None:
        submit_parameters.append("--additional_lines")
        submit_parameters.append(args.additional_lines)
    if args.notify_all:
        submit_parameters.append("--notify_all")
    if args.notify_fail:
        submit_parameters.append("--notify_fail")
    if args.notify_end:
        submit_parameters.append("--notify_end")
    if args.no_confirmation:
        submit_parameters.append("--no_confirmation")
    if args.do_not_submit_job_script:
        submit_parameters.append("--do_not_submit_job_script")

    name_job_script, job_id = submit_sim.submit_sim(argv=submit_parameters)

    return (added_id, name_job_script, job_id)


if __name__ == '__main__':
    add_and_submit("", sys.argv[0], sys.argv[1:])
