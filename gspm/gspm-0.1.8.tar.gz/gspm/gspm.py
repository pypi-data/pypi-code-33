# Copyright (C) 2018 Paul Hocker <paul@spocker.net>
# See LICENSE file for License Information

""""Godot Stuff Project Manager"""

import logging
import gspm
import sys
import dotmap
import io 

import gspm.parser as parser
import gspm.project as project
import gspm.utils.path_utils as path_utils


def _get_logging_level():
    return logging.DEBUG


def init():
    '''
    Initialize the Environment

    Used to setup the Logging Environment and
    some other things for the runtime.
    '''
    #   setup some basic logging
    logging.basicConfig(
        filename="./gspm.log",
        level=_get_logging_level(),
        format='[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )

    #   add console logging
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    #   some diagnostic info
    logging.debug(sys.path)

    #   a little welcome message
    logging.log(99, gspm.__logo__)
    logging.log(99, gspm.__name__)
    logging.log(99, "Version {0}, {1}".format(get_version(), gspm.__copyright__))
    print()


def get_version():
    '''
    Return the Version
    '''
    return gspm.__version__
    

def run():
    '''
    Runs the Command
    '''
    try:
        init()
        args = parser.create_parser().parse_args()

        the_project = dotmap.DotMap()

        if not args.ignore_project:
            the_project.config = project.load(args.config)

        #   get home path (aka where am i running from?)
        path_utils.define_project_paths(the_project)

        #   store the args for later
        the_project.args = args

        #   execute
        args.func(the_project)

        #   good-bye
        sys.exit(0)

    except Exception as e:
        logging.error(e)
        logging.error("operation cancelled")
        sys.exit(1)
