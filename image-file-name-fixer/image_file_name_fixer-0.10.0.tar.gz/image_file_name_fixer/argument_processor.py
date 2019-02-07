import argparse
from .app_config import AppConfig

"""
This module handles command line argument processing.
"""


class ArgumentProcessor:
    """
    This class handles command line argument processing.
    """
    def __init__(self):
        self.arg_parser = argparse.ArgumentParser()

    def process_args(self):
        """
        Process command line args, and construct an AppConfig object.
        :returns:  An instance of AppConfig.  This object describes the application's configuration based on
                   command line arguments.
        """
        self.arg_parser.add_argument('-i',
                                     '--input',
                                     type=str,
                                     dest='paths',
                                     help='paths to files or directories to be processed.',
                                     nargs='*')
        self.arg_parser.add_argument('--version',
                                     action='store_true',
                                     dest='version',
                                     help='Output the version of this software and exit.')
        self.arg_parser.add_argument('-o',
                                     '--output',
                                     type=str,
                                     dest='output_dir',
                                     help='Write output to specified directory.  Overrides --in-place')
        self.arg_parser.add_argument('--dry-run',
                                     action='store_true',
                                     dest='dry_run',
                                     help='Run normally, but don\'t write anything to disk')
        self.arg_parser.add_argument('-R', '--recursive',
                                     action='store_true',
                                     dest='recursive',
                                     help='Recursively process image files in a directory.\
                                     Ignored when input is a file')
        self.arg_parser.add_argument('-m', '--move',
                                     action='store_true',
                                     dest='should_move_file',
                                     help='Move the file, rather than copying it.')
        self.arg_parser.add_argument('-v', '--verbose',
                                     action='store_true',
                                     dest='verbose',
                                     help='Increase output detail.')

        args = self.arg_parser.parse_args()
        return AppConfig(args)
