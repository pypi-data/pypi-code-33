#!/usr/bin/env python3
import argparse
import os
import sys
from semvermanager import Version
from semvermanager.command import Command, CommandRunner


class BumpCommand(Command):

    def __call__(self, filename, label, separator, bump_field):
            if not os.path.isfile(filename):
                print(f"No such file:'{filename}' can't bump {bump_field} version")
                return filename, None
            v = Version.find(filename, label, separator)
            if v:
                print(f"Bumping '{bump_field}' value from {v.field(bump_field)} ", end="")
                v.bump(bump_field)
                print(f"to {v.field(bump_field)} in '{filename}'")
                Version.update(filename, v, label, separator)
                print(f"new version: {v}")
            else:
                print(f"Couldn't bump value in {filename}")
            return filename, v


class MakeCommand(Command):

    def __init__(self, overwrite):
        super().__init__()
        self._overwrite = overwrite

    def __call__(self, filename, version_label, separator):

        v = Version(lhs=version_label, separator=separator)
        if self._overwrite or not os.path.isfile(filename):
            f, v = v.write(filename)

        elif os.path.isfile(filename):
            answer = input(f"Overwrite file '{filename}' (Y/N [N]: ")
            if len(answer) > 0 and answer.strip().lower() == 'y':
                f, v = v.write(filename)
            else:
                f = filename
                v = None

        return f, v
    

def script_main():
    main(sys.argv)


def main(args=None):
    if not args:
        args = sys.argv

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--version",
        help="Specify a version in the form major.minor.patch-tag"
    )

    parser.add_argument(
        "--make",
        default=False,
        action="store_true",
        help="Make a new version file")

    parser.add_argument(
        "--bump",
        choices=Version.FIELDS,
        help="Bump a version field")

    parser.add_argument(
        "--getversion",
        default=False,
        action="store_true",
        help="Report the current version in the specified file")

    parser.add_argument(
        "--bareversion",
        default=False,
        action="store_true",
        help="Return the unquoted version strin with VERSION=")

    parser.add_argument(
        "--overwrite",
        default=False,
        action="store_true",
        help="overwrite files without checking [default: %(default)s]"
    )

    parser.add_argument(
        "--update",
        default=False,
        action="store_true",
        help="Update multiple version strings in file"
    )

    parser.add_argument(
        "--label",
        default="VERSION",
        help="field used to determine which line is the version line [default: %(default)s]"
    )

    parser.add_argument(
        "--separator",
        default="=",
        help="Character used to separate the version label from the version [default: %(default)s]"
    )

    parser.add_argument(
        "filenames",
        nargs='*',
        help="Files to use as version file"
    )

    args = parser.parse_args(args)

    if args.version:
        version = Version.parse_version("VERSION="+args.version, lhs=args.label)

    if args.make:
        cmd_runner = CommandRunner(MakeCommand(args.overwrite))
        for f, v in cmd_runner(args.filenames, args.label, args.separator):
            if v:
                print(f"Created version {v} in '{f}'")
            else:
                print(f"Failed to create version file '{f}'")

        # if args.overwrite or not os.path.isfile(args.filename):
        #     filename, version = Version.write(args.filename, Version(lhs=args.versionlabel, separator=args.versionseparator))
        #     print(f"Created {version} in '{args.filename}'")
        # elif os.path.isfile(args.filename):
        #     answer = input(f"Overwrite file '{args.filename}' (Y/N [N]: ")
        #     if len(answer) > 0 and answer.strip().lower() == 'y':
        #         filename, version = Version.write(args.filename, args.versionlabel)
        #         print(f"Overwrote {version} in '{args.filename}'")

    if args.getversion:
        if os.path.isfile(args.filename):
            v = Version.find(args.filename)
            print(v)
        else:
            print(f"No such version file: '{args.filename}'")

    if args.bareversion:
        if os.path.isfile(args.filename):
            v = Version.find(args.filename, args.label)
            print(v.bare_version())
        else:
            print(f"No such version file: '{args.filename}'")

    if args.bump:
        if args.bump in Version.FIELDS:
            cmd_runner = CommandRunner(BumpCommand())

            for filename, v in cmd_runner(args.filenames, args.label, args.separator,  args.bump):
                if v:
                    print(f"Processed version {v} in file : '{filename}'")
                else:
                    print(f"Couldn't process '{filename}'")

            # if not os.path.isfile(args.filename):
            #     print(f"No such file:'{args.filename}' can't bump {args.bump} version")
            #     sys.exit(1)
            # v = Version.find(args.filename, args.versionlabel)
            # print(f"Bumping '{args.bump}' value from {v.field(args.bump)} ", end="")
            # v.bump(args.bump)
            # print(f"to {v.field(args.bump)} in '{args.filename}'")
            # Version.update(args.filename, v, args.versionlabel)
            # print(f"new version: {v}")
        else:
            print(f"{args.bump} is not a valid version field, choose one of {Version.FIELDS}")
            sys.exit(1)

    if args.update:
        print(f"Updating '{args.filename}' with version '{version}'")
        Version.update(filename=args.filename, version=version, lhs=args.label)


if __name__ == "__main__":
    main(sys.argv[1:])  # clip off the program name
