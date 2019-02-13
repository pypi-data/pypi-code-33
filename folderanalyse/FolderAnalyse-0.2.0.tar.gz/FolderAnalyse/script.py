"""
Ryan Pepper (2018)

script.py

This script contains the main entrypoint to the folder-analyse application.

"""

import argparse
import os
import sys
import FolderAnalyse
from FolderAnalyse.process import process_dir, process_file


def _get_parser():
    """
    _get_parser()

    Construct a parser using argparse to collect user supplied
    arguments. This is designed to be called from the entrypoint
    specified in setup.py
    """

    parser = argparse.ArgumentParser(
            description="%(prog)s  [options]\n"
                        "Produce word statistics for files in a directory."
                         )

    parser.add_argument('path', type=str,
                        help="path to a directory or a file.")

    parser.add_argument('-t', '--type', type=str, default='txt',
                        help="if path is to a directory, file extension of\n"
                             "files that to be processed.")

    parser.add_argument('-c', '--case', action='store_false',
                        help="by default, processing is not case sensitive.\n"
                             "Add this flag to make it case sensitive")

    parser.add_argument('-N', '--number', type=int, default=10,
                        help="show the top N frequencies for the file(s) and\n"
                             "directory.")

    parser.add_argument('-s', '--save', type=str,
                        help="save the statistics report to the filename.")

    parser.add_argument('-r', '--runtests', action='store_true',
                        help="Ignore all other options and run the tests for"
                             "the module")
    return parser


def _exit(message, parser):
    """
    exit(error, parser)

    Quits the running application and prints the parser help, before printing
    the specified error message.
    """

    parser.print_help()
    print(f"\n\nError: {message}. See above for help.")
    sys.exit()


def main():
    """
    main()

    Main function which is the entrypoint to the application.

    Gets parsed arguments, and constructs a report which is printed to the
    screen based on them. To see how the arguments affect the output, look at
    :func:`FolderAnalyse.script.get_parser`
    """
    parser = _get_parser()
    args = parser.parse_args()

    if args.runtests:
        FolderAnalyse.runtests()
        sys.exit()

    path = args.path
    extension = args.type
    case = args.case

    N = args.number

    directory = os.path.isdir(path)
    file = os.path.isfile(path)

    if file:
        try:
            stats_text, _, _ = process_file(path, N, case)

        except FileNotFoundError:
            _exit(f"File {path} not found.", parser)

        except UnicodeError as e:
            _exit(f"Could not open file {e.args[0]} as encoding could not be "
                  "detected.")

    elif directory:
        try:
            stats_text, _, _, _, _ = process_dir(path, extension, N, case)

        except FileNotFoundError:
            _exit(f"No files with extension {extension} found in directory",
                  parser)
        except UnicodeError as e:
            _exit(f"Could not open file {e.args[0]} as encoding could not be "
                  "detected and could not be processed.")

    else:
        _exit("File or directory does not exist", parser)

    print(stats_text)

    if args.save:
        f = open(args.save, 'w')
        f.write(stats_text)
        f.close()
        print(f"\nSaved report to \"{args.save}.\"")


if __name__ == '__main__':
    main()
