import argparse

import muscle.view.options
from muscle.controller.controller import Controller


def parse_args(args):
    """
    Generates CLI using argparse module.

    :param args: command line arguments passed from sys.argv[1:]
    :return: a dict of user input in this format {option:argument...}
    """
    parameters = {"prog": "muscle",
                  "description": "Muscle is a weight lifting tracking app.",
                  "usage": "%(prog)s [option] [<argument>]"}
    parser = argparse.ArgumentParser(**parameters)

    options = parser.add_mutually_exclusive_group()

    options.add_argument('--show-history',
                         action='store_true',
                         help="Show workout history")
    options.add_argument('--record',
                         action='store_true',
                         help="Record today's workout")
    options.add_argument('--delete-record',
                         nargs='?',
                         const=True,
                         metavar='<date>',
                         help="Delete the record on a specific date")
    options.add_argument('--list-routine',
                         action='store_true',
                         help='List all routines')
    options.add_argument('--add-routine',
                         action='store_true',
                         help='Add a new routine')
    options.add_argument('--delete-routine',
                         nargs='?',
                         const=True,
                         metavar='<routine name>',
                         help='Delete a routine')
    options.add_argument('--import-db',
                         metavar='<path>',
                         help='Import a database')
    options.add_argument('--export-db',
                         metavar='<path>',
                         help='Export a database')
    options.add_argument('--gui',
                         action='store_true',
                         help='Start muscle GUI (not implemented yet)')

    if not args:
        parser.print_help()

    return vars(parser.parse_args(args))


def cli(args):
    """Invoke a command line interface."""
    controller = Controller()
    options = parse_args(args)
    for option, argument in options.items():
        function_name = option.replace('-', '_')
        if argument is True:
            getattr(muscle.view.options, function_name)(controller)
        elif argument:
            getattr(muscle.view.options, function_name)(controller, argument)

    controller.terminate()
