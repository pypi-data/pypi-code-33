#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Run a multiple simulations in series.

If no ID's or conditions of which simulations to run is passed as parameters,
the simulations with 'new' status is run.

Usage: 'python run_serial_sims.py --id ID_1 ID_2 ID_3'
"""
# Copyright (C) 2017-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

if __name__ == '__main__':
    import add_package_root_to_path

import sim_db.src_command_line_tool.commands.helpers as helpers
import sim_db.src_command_line_tool.commands.update_sim as update_sim
import argparse
import sqlite3
import subprocess
import sys


def command_line_arguments_parser(name_command_line_tool="sim_db",
                                  name_command="run_serial_sims"):
    parser = argparse.ArgumentParser(
            description=(
                    "Run multiple simulations in series. If no ID's or "
                    "conditions are given all the new simulations are run."),
            prog="{0} {1}".format(name_command_line_tool, name_command))
    parser.add_argument(
            '--id',
            '-i',
            type=int,
            nargs='+',
            default=[],
            help=("'IDs' of the simulation parameters in the 'sim.db' "
                  "database that should be used in the simulation."))
    parser.add_argument(
            '--where',
            '-w',
            type=str,
            nargs='+',
            default=[],
            help=("Conditions of the simulation parameters in the 'sim.db' "
                  "database that should be used in the simulation."))

    return parser


def run_serial_sims(name_command_line_tool="sim_db",
                    name_command="run_serial_sims",
                    argv=None):
    """Run multiple simulations in series."""
    args = command_line_arguments_parser(name_command_line_tool,
                                         name_command).parse_args(argv)

    db = helpers.connect_sim_db()
    db_cursor = db.cursor()
    if len(args.id) > 0:
        ids = args.id
    elif len(args.where) > 0:
        db_cursor.execute("SELECT id FROM runs WHERE status = '{0}';"
                          .format(args.where))
        ids = db_cursor.fetchall()
        ids = [i[0] for i in ids]
    else:
        db_cursor.execute("SELECT id FROM runs WHERE status = 'new';")
        ids = db_cursor.fetchall()
        ids = [i[0] for i in ids]

    db.commit()
    db_cursor.close()
    db.close()

    print("Running simulations with the following IDs one after another:")
    print(ids)
    for id_sim in ids:
        db = helpers.connect_sim_db()
        db_cursor = db.cursor()
        run_command = helpers.get_run_command(db_cursor, id_sim)
        db.commit()
        db_cursor.close()
        db.close()
        update_sim.update_sim(argv=[
                "--id",
                str(id_sim), "--columns", "cpu_info", "--values",
                helpers.get_cpu_and_mem_info()
        ])
        update_sim.update_sim(argv=[
                "--id",
                str(id_sim), "--columns", "status", "--values", "running"
        ])

        print("\nRunning simulation with ID: {0}".format(id_sim))

        for command in run_command.split(';'):
            process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True)
            if sys.version_info[0] < 3:
                for line in iter(process.stdout.readline, ''):
                    sys.stdout.write(line.decode('ascii', 'replace'))
                    sys.stdout.flush()
                for line in iter(process.stderr.readline, ''):
                    sys.stdout.write(line.decode('ascii', 'replace'))
                    sys.stdout.flush()
            else:
                for line in iter(process.stdout.readline, b''):
                    sys.stdout.write(line.decode('ascii', 'replace'))
                    sys.stdout.flush()
                for line in iter(process.stderr.readline, b''):
                    sys.stdout.write(line.decode('ascii', 'replace'))
                    sys.stdout.flush()

        update_sim.update_sim(argv=[
                "--id",
                str(id_sim), "--columns", "status", "--values", "finished"
        ])


if __name__ == '__main__':
    run_serial_sims("", sys.argv[0], sys.argv[1:])
