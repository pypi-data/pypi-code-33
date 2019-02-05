# -*- coding: utf-8 -*-
#
# Copyright 2018 Barry Muldrey
#
# This file is part of xanity.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import argparse

from .constants import COMMANDS, INVOCATION


def print_help():
    print("""
xanity initialize|init [--with-examples] [new-dir]     
    Create a bare-bones xanity project directory tree.

xanity setup [proj-dir]
    Create or update the conda environment associated with the project.

xanity status [proj-dir]
    Print the status of the current xanity project.

xanity run [experiment_names] [-a analyses[...]]
    Run all (or the specified) experiments and optionally, analyses.

xanity anal[yze|yse|ysis] [-a analyses] [run_data_path]
    Run all (or the specified) analyses on the most recent (or specified) data.
    
xanity ses[h|s|sion]
    Drops you into a new bash shell inside your project's environment.
""")


def parser(xanity, clargs=None):
    if clargs:
        list_to_parse = clargs.split(' ') if isinstance(clargs, str) else list(clargs)
    else:
        list_to_parse = None

    parser = argparse.ArgumentParser(prog='xanity')
    parser.add_argument('action', nargs='?', help='available actions include: {}'.format(COMMANDS))
    action_arg, remaining_args = parser.parse_known_args(list_to_parse) if list_to_parse else parser.parse_known_args()

    if not action_arg.action in COMMANDS and xanity.invocation == INVOCATION.HOOK:
        # a hook call should have clargs !
        raise NotImplementedError
        # hook_action = xanity._resolve_action_from_hook()
        # action_arg.action = hook_action
    else:
        hook_action = False

    if action_arg.action in COMMANDS.RUN:
        # 'run' command parser
        parser.add_argument('experiments', nargs='*',
                            help='specify the experiments to run')
        parser.add_argument('-a', '--and-analyze', nargs='*',
                            help="request that data be analyzed upon completion of experiment")
        parser.add_argument('--debug', action='store_true',
                            help='run experiment in debugging mode; experiment code may print additional output'
                                 ' or behave differently')
        parser.add_argument('--logging', action='store_true',
                            help='request experiment perform additional logging')
        parser.add_argument('--loadcp', action='store_true',
                            help='request experiment look for and load stored checkpoints from src/include/persistent'
                                 ' rather than start from scratch')
        parser.add_argument('--savecp', action='store_true',
                            help='request experiment try to save checkpoints to src/include/persistent'
                                 ' (will NOT overwrite)')
        parser.add_argument('--checkpoints', action='store_true')
        parser.add_argument('--profile', action='store_true',
                            help='run cProfile attatched to your experiment')

    elif action_arg.action in COMMANDS.ANAL:
        # 'analyze' command parser
        parser.add_argument('runid', nargs='*',
                            help='specify the data-path to analyze')
        parser.add_argument('-a', '--analyses', nargs='*',
                            help="""list of explicit analyses to run""")
        parser.add_argument('--debug', action='store_true',
                            help='run experiment in debugging mode; experiment code may print additional output'
                                 ' or behave differently')
        parser.add_argument('--logging', action='store_true',
                            help='request experiment perform additional logging')
        parser.add_argument('--profile', action='store_true',
                            help='run cProfile attatched to your experiment')

    elif action_arg.action in COMMANDS.INIT:
        # 'initialize' command parser
        parser.add_argument('directory', nargs='?', help='path to location of new or existing xanity project')
        parser.add_argument('--examples', '--with-examples', action='store_true',
                            help='include example experiments and analyses')

    elif action_arg.action in COMMANDS.SETUP:
        parser.add_argument('directory', nargs='?', help='path to location of an existing xanity project')

    elif action_arg.action in COMMANDS.ENV:
        parser.add_argument('env_action', help='manipulate the internal conda env')

    elif action_arg.action in dir(xanity):
        pass

    elif 'help' in action_arg.action:
        print_help()
        raise SystemExit(0)

    else:
        print('didn\'t recognize that command. Use \'xanity help\' for help.')
        raise SystemExit(1)

    args, unknownargs = parser.parse_known_args(list_to_parse) if list_to_parse else parser.parse_known_args()
    args.action = action_arg.action if not hook_action else hook_action

    return args, unknownargs
