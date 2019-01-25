#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Make job script and submit it to the job scheduler.

Job scripts are added for either the list of ID's provided if provided, or all
runs with status 'new'. A confirmation question is asked if no ID's are 
provided.
"""
# Copyright (C) 2017-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

if __name__ == '__main__':
    import add_package_root_to_path

import sim_db.src_command_line_tool.commands.helpers as helpers
import sqlite3
import argparse
import time
import subprocess
import sys
import os
import math


def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="submit_sim"):
    parser = argparse.ArgumentParser(
            description='Submit job',
            prog="{0} {1}".format(name_command_line_tool, name_command))
    parser.add_argument(
            '--id',
            '-i',
            type=int,
            default=None,
            nargs='+',
            help="ID of simulations to submit.")
    parser.add_argument(
            '--allow_reruns',
            action="store_true",
            help="Allow simulations with non 'new' status to be submitted.")
    parser.add_argument(
            '--max_walltime',
            type=str,
            default=None,
            nargs='+',
            help=("Maximum walltime the simulation can use, given in "
                  "'hh:mm:ss' format."))
    parser.add_argument(
            '--n_tasks',
            type=int,
            default=None,
            nargs='+',
            help=
            ("Number of tasks to run the simulation with. A warning is "
             "given if it is not a multiple of the number of logical cores on "
             "a node."))
    parser.add_argument(
            '--n_nodes',
            type=int,
            default=None,
            nargs='+',
            help="Number of nodes to run the simulation on.")
    parser.add_argument(
            '--additional_lines',
            type=str,
            default=[],
            nargs='+',
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
                  "simulations with status 'new'"))
    parser.add_argument(
            '--do_not_submit_job_script',
            action='store_true',
            help="Makes the job script, but does not submit it.")

    return parser


def make_job_script(db_cursor, i, args, id_submit):
    try:
        db_cursor.execute("SELECT name, max_walltime, n_tasks FROM runs WHERE "
                "id={0}".format(id_submit))
    except:
        raise ValueError("ID {0} in the database is missing neccessary "
                         "parameters to submit job script.".format(id_submit))
    job_script_variables = db_cursor.fetchall()[0]
    settings = helpers.Settings()
    which_job_scheduler = settings.read('which_job_scheduler')[0]
    if which_job_scheduler != 'SLURM' and which_job_scheduler != 'PBS':
        print("'Which job scheduler' in .sim_db/settings.txt is NOT one of the "
              "valid values: 'SLURM' or 'PBS'. Change with: '$ sim_db settings "
              "<args>'")
        exit(1)

    name = job_script_variables[0]
    if name != None:
        job_script_name = 'job_script_' + time.strftime("%Y-%b-%d_%H-%M-%S") \
                        + '_' + name + '_' + str(id_submit) + ".sh"
    else:
        job_script_name = 'job_script_' + time.strftime("%Y-%b-%d_%H-%M-%S") \
                        + '_' + str(id_submit) + ".sh"
    job_script_file = open(job_script_name, 'w')
    job_script_file.write("#!/bin/bash\n")

    if name != None:
        if which_job_scheduler == 'SLURM':
            job_script_file.write("#SBATCH --job-name={0}\n".format(name))
        elif which_job_scheduler == 'PBS':
            job_script_file.write("#PBS -N {0}\n".format(name))

    max_walltime = job_script_variables[1]
    if args.max_walltime != None:
        max_walltime = args.max_walltime[i]
    if max_walltime == None:
        print("Job script can NOT be submitted without either 'max_walltime' " \
            "being set in simulation parameters file or " \
            "'--max_walltime HH:MM:SS' being passed as flags to 'sim_db "
            "submit_sim'.")
        job_script_file.close()
        os.remove(job_script_name)
        exit(1)
    db_cursor.execute("UPDATE runs SET max_walltime = '{0}' WHERE id = {1}"
                      .format(max_walltime, id_submit))
    if which_job_scheduler == 'SLURM':
        job_script_file.write("#SBATCH --time={0}\n".format(max_walltime))
    elif which_job_scheduler == 'PBS':
        job_script_file.write("#PBS -l walltime={0}\n".format(max_walltime))

    n_cpus_per_node = settings.read('n_cpus_per_node')
    if len(n_cpus_per_node) > 0:
        n_cpus_per_node = int(n_cpus_per_node[0])
    else:
        n_cpus_per_node = None

    n_tasks = job_script_variables[2]
    if args.n_tasks != None or args.n_nodes != None:
        if args.n_tasks != None:
            n_tasks = args.n_tasks[i]
        else:
            if (n_cpus_per_node == None):
                print("'Number of logical cpus per node' is NOT set in "
                      ".sim_db/settings.txt and it must be when '--n_nodes N' "
                      "is passed to 'sim_db submit_sim' command.")
                job_script_file.close()
                os.remove(job_script_name)
                exit(1)
            n_tasks = args.n_nodes[i] * n_cpus_per_node
        db_cursor.execute("UPDATE runs SET n_tasks = {0} WHERE id = {1}" \
                .format(n_tasks, id_submit))
    if n_tasks == None:
        print("Job script can NOT be submitted without either 'n_tasks' " \
              +"being set in simulation parameters file or '--n_tasks N' or " \
              +"'--n_nodes M' being passed as flags to 'sim_db submit_sim'.")
        job_script_file.close()
        os.remove(job_script_name)
        exit(1)

    if n_cpus_per_node != None:
        if n_tasks % n_cpus_per_node != 0:
            print("WARNING: Number of tasks (processes) is NOT a multiple of " \
                 +"the number of logical cpus per node.")

    if which_job_scheduler == 'SLURM':
        job_script_file.write("#SBATCH --ntasks={0}\n".format(n_tasks))
    elif which_job_scheduler == 'PBS':
        n_nodes = int(math.ceil(n_tasks / float(n_cpus_per_node)))
        job_script_file.write("#PBS -l nodes={0}:ppn={1}\n".format(
                n_nodes, n_cpus_per_node))

    memory_per_node = settings.read('memory_per_node')
    if len(memory_per_node) > 0:
        memory_per_cpu = float(memory_per_node[0]) / float(n_cpus_per_node)
        if which_job_scheduler == 'SLURM':
            job_script_file.write("#SBATCH --mem-per-cpu={0}M\n".format(
                    int(memory_per_cpu * 1000)))
        elif which_job_scheduler == 'PBS':
            job_script_file.write("#PBS --mem={0}GB\n".format(
                    memory_per_node[0]))

    account = settings.read('account')
    if len(account) > 0:
        account = account[0]
        if which_job_scheduler == 'SLURM':
            job_script_file.write("#SBATCH --account={0}\n".format(account))
        elif which_job_scheduler == 'PBS':
            job_script_file.write("#PBS -A {0}\n".format(account))

    if args.notify_all or args.notify_fail or args.notify_fail:
        if which_job_scheduler == 'SLURM':
            job_script_file.write("#SBATCH --mail-user={0}\n".format(
                    settings.read('email')))
            if args.notify_all:
                job_script_file.write("#SBATCH --mail-type=ALL\n")
            if args.notify_fail:
                job_script_file.write("#SBATCH --mail-type=FAIL\n")
            if args.notify_end:
                job_script_file.write("#SBATCH --mail-type=END\n")
        elif which_job_scheduler == 'PBS':
            job_script_file.write("#PBS -M {0}\n".format(
                    settings.read('email')))
            if args.notify_all:
                job_script_file.write("#PBS -m abe\n")
            if args.notify_fail:
                job_script_file.write("#PBS -m a\n")
            if args.notify_end:
                job_script_file.write("#PBS -m e\n")

    for line in args.additional_lines:
        job_script_file.write(line + '\n')

    for line in settings.read('add_to_job_script'):
        job_script_file.write(line)

    run_command = helpers.get_run_command(db_cursor, id_submit,
                                          job_script_variables[2])
    job_script_file.write('\n')
    for command in run_command.split(';'):
        job_script_file.write("{0}\n".format(command))

    job_script_file.close()

    return job_script_name


def submit_sim(name_command_line_tool="sim_db",
               name_command="submit_sim",
               argv=None):
    args = command_line_arguments_parser(name_command_line_tool,
                                         name_command).parse_args(argv)
    ids = args.id

    db = helpers.connect_sim_db()
    db_cursor = db.cursor()

    job_script_name = None
    job_id = None

    if ids == None:
        db_cursor.execute("SELECT id FROM runs WHERE status = 'new';")
        ids = db_cursor.fetchall()
        ids = [i[0] for i in ids]
        answer = None
        while (not args.no_confirmation and answer != 'y' and answer != 'Y'
               and answer != 'yes' and answer != 'Yes'):
            answer = helpers.user_input(
                    "Would you like to submit simulations "
                    "with the following ID's: {0}? (y/n) ".format(ids))
            if (answer == 'n' or answer == 'N' or answer == 'no'
                        or answer == 'No'):
                db.commit()
                db_cursor.close()
                db.close()
                return (job_script_name, job_id)
    elif not args.allow_reruns:
        for i in ids:
            db_cursor.execute("SELECT status FROM runs WHERE id = {0};"
                              .format(i))
            status = db_cursor.fetchone()[0]
            if status != "new":
                print("No simulations was submitted.\nStatus of simulation "
                      "with 'ID' = {0} is {1}.\nEither:\n- Add "
                      "'--allow_reruns' flag to allow it to run.\n- Update "
                      "status to 'new'.".format(args.id, 
                      status))
                exit()

    which_job_scheduler = helpers.Settings().read('which_job_scheduler')[0]
    for i, id_submit in enumerate(ids):
        job_script_name = make_job_script(db_cursor, i, args, id_submit)
        if not args.do_not_submit_job_script:
            if which_job_scheduler == 'SLURM':
                p = subprocess.Popen(
                        ["sbatch", job_script_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                (job_id, err) = p.communicate()
                print(err)
                job_id = job_id.split()[-1]
            elif which_job_scheduler == 'PBS':
                p = subprocess.Popen(
                        ["qsub", job_script_name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                (job_id, err) = p.communicate()
                print(err)
                job_id = job_id.split()[-1]
            db_cursor.execute("UPDATE runs SET status='submitted' WHERE id={0}" \
                              .format(id_submit))
            db_cursor.execute("UPDATE runs SET job_id={0} WHERE id={1}" \
                              .format(job_id, id_submit))

    db.commit()
    db_cursor.close()
    db.close()

    print("Job ID: {0}".format(job_id))
    return (job_script_name, job_id)


if __name__ == '__main__':
    submit_sim("", sys.argv[0], sys.argv[1:])
