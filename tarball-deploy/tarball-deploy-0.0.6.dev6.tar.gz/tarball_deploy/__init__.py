import argparse
import pkg_resources

from tarball_deploy.workdir import WorkdirType


__version__ = pkg_resources.get_distribution(__name__).version


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("--workdir", required=True, type=WorkdirType())
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--from", dest="tar_file", type=argparse.FileType())
    action.add_argument("--rollback", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.rollback:
        args.workdir.rollback()
    else:
        args.workdir.deploy(args.tar_file)
