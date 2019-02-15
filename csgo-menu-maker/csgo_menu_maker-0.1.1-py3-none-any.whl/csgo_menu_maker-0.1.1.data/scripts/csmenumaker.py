#!/usr/bin/env python3

import argparse
import sys

import csgomenumaker


parser = argparse.ArgumentParser(
    description='Generate a console menu for CSGO.'
)

parser.add_argument(
    'file'
)

args = parser.parse_args(sys.argv[1:])

csgomenumaker.Component.ConfigLoader(args.file)