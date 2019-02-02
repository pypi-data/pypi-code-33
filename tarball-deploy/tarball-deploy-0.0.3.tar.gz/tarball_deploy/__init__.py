import argparse
import pkg_resources
import os
import sys

from tarball_deploy.workdir import Workdir


__version__ = pkg_resources.get_distribution(__name__).version


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("--workdir", required=True)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--from", dest="tar_file", type=argparse.FileType())
    action.add_argument("--rollback", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    workdir = Workdir(args.workdir)
    if args.rollback:
        workdir.rollback()
    else:
        workdir.deploy(args.tar_file)
