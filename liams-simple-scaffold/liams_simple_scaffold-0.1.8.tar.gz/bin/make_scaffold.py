#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import liams_simple_scaffold_pkg.prefil.prefil_files as fil

def parse_args(args):

    parser = argparse.ArgumentParser(
            description="Make a simple python package scaffold.")
    required = parser.add_argument_group(
            'Required',
            'Project name')
    required.add_argument(
            "-n",
            "--name",
            type=str,
            help="Name of python project. Check that its not in PyPI if you want to use pip")
    required.add_argument(
            "-a",
            "--author",
            type=str,
            help="Name of author",
            default = "Liam McIntyre")
    required.add_argument(
             "-e",
             "--email",
             type=str,
             help="Authors email",
             default = "shimbalama@gmail.com")

    optional = parser.add_argument_group(
            'Optional parameters',
            'All have defaults')
    optional.add_argument(
            "-m",
            "--modules",
            type=str,
            help="Modules (comma,separated,list)",
            default = None)

    return parser.parse_args(args)

def main():

    '''
    Make a simple python package scaffold
    '''

    args = parse_args(sys.argv[1:])
    fil.main(args)


if __name__ == "__main__":
    main()


