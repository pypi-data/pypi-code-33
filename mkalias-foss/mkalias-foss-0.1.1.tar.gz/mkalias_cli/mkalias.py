#!/usr/bin/env python3
"""
    mkalias.py - CLI app to create finder aliases./mk

"""

import argparse
import os

import osascript
from setuptools_scm import get_version

version = get_version()


def parse_args():
    parser = argparse.ArgumentParser(prog='mkalias',
                                     description='Application to create Finder aliases from the command line')

    parser.add_argument('source', help='Source to create alias from')
    parser.add_argument('destination', help='Destination directory of alias')
    parser.add_argument('-n', dest='alias_name', metavar="Name", help='Set the name of the new alias')
    parser.add_argument('--version', action='version', version='%(prog)s v{}'.format(version),
                        help='Display version info')

    return parser.parse_args()


def check_path(source, destination):
    path_exists = True
    source = os.path.abspath(source)
    destination_head, destination_tail = os.path.split(destination)

    def print_not_found_error(location):
        print("Error '{}' not found!".format(location))

        if not os.path.isdir(source):
            print_not_found_error(source)
            path_exists = False
        elif not os.path.isdir(destination_head):
            print_not_found_error(destination_head)
            path_exists = False
        if not os.path.isfile(source):
            print_not_found_error(source)
            path_exists = False
        elif not os.path.isdir(destination_head):
            print_not_found_error(destination_head)
            path_exists = False

    if path_exists:
        print("Source Dir - '{}'".format(source))
        print("Destination Dir - '{}'".format(destination))

    return path_exists


def create_alias(source, destination):
    command_string = 'tell application "Finder" to make alias file to POSIX file "{}" at POSIX file "{}"' \
        .format(source, destination)

    code, out, error = osascript.run(command_string)

    print(command_string)
    print(code)
    print(out)
    print(error)


def rename_alias(source, destination, name):
    """
    Rename the new alias to a custom name instead of "example alias"

    :param source: Name of the source file/dir for the alias
    :param destination: destination for the alias
    :return: none
    """

    source_head, source_tail = os.path.split(source)

    alias_name = source_tail + " alias"
    alias_path = destination + "/" + alias_name
    new_name_path = destination + "/" + name

    os.rename(alias_path, new_name_path)
    print(new_name_path)


def main():
    args = parse_args()

    source = os.path.abspath(args.source)
    destination = os.path.abspath(args.destination)

    check_path(source, destination)

    create_alias(source, destination)

    if args.alias_name:
        rename_alias(source, destination, args.alias_name)


if __name__ == "__main__":
    main()
