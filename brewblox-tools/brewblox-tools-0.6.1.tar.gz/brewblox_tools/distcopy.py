#! /usr/bin/python3

import argparse
import glob
import os
import pathlib
import shutil


def parse_args(sys_args: list = None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument('source', help='Source directory')
    argparser.add_argument('destinations', nargs='+', help='Destination directories.')
    return argparser.parse_args(sys_args)


def main(sys_args: list = None):
    args = parse_args(sys_args)
    print(vars(args))

    for dest in args.destinations:
        pathlib.Path(dest).mkdir(parents=True, exist_ok=True)

        for f in glob.glob(dest + '/*'):
            os.remove(f)

        for f in glob.glob(args.source + '/*'):
            shutil.copy(f, dest + '/')
            print(f'{f} ==> {dest}')


if __name__ == '__main__':
    main()
