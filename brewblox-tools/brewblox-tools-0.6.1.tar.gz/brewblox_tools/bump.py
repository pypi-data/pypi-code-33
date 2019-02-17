#! /usr/bin/python3

import argparse
from distutils.util import strtobool
from distutils.version import StrictVersion
from subprocess import STDOUT, check_call, check_output


def parse_args(sys_args: list = None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument('bump_type',
                           help='Component of the version number to increment.',
                           choices=['major', 'minor', 'patch'])
    return argparser.parse_args(sys_args)


def user_yes_no_query(question: str) -> bool:
    print(f'{question} [Y/n]')
    while True:
        try:
            return strtobool(input().lower() or 'yes')
        except ValueError:
            print('Please respond with \'y\' or \'n\'.')


def bump(current_version: str, bump_type: str) -> str:
    major, minor, patch = StrictVersion(current_version).version

    return {
        'major': lambda: f'{major + 1}.{0}.{0}',
        'minor': lambda: f'{major}.{minor + 1}.{0}',
        'patch': lambda: f'{major}.{minor}.{patch + 1}',
    }[bump_type]()


def main(sys_args: list = None):
    args = parse_args(sys_args)
    print(vars(args))

    # Get all version-formatted tags, but use the latest
    current_version = check_output(
        r'git tag -l *.*.* --contains $(git rev-list --tags --max-count=1)',
        shell=True
    ).decode().rstrip().split('\n')[-1]

    new_version = bump(current_version, args.bump_type)

    print(f'Bumping "{args.bump_type}" version: {current_version} ==> {new_version}')

    if user_yes_no_query('Do you want to tag the current commit with that version?'):
        check_output(f'git tag -a {new_version} -m "Version {new_version}"', shell=True)

        print('Latest tags:')
        print(check_output('git tag -n1 | tail -n5', shell=True).decode().rstrip())

    else:
        print('Aborted. No tags were added!')
        return

    if user_yes_no_query('Do you want to push this tag?'):
        check_call('git push --tags', shell=True, stderr=STDOUT)


if __name__ == '__main__':
    main()
