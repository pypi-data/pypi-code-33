#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Semversioner allows you to manage semantic versioning properly and simplifies changelog generation. 

This project was inspired by the way AWS manages their versioning for AWS-CLI: https://github.com/aws/aws-cli/

At any given time, the ``.changes/`` directory looks like:
    .changes
    |
    └── next-release
        ├── minor-20181227010225.json
        └── major-20181228010225.json
    ├── 1.1.0.json
    ├── 1.1.1.json
    ├── 1.1.2.json

This script takes everything in ``next-release`` and aggregates them all together in a single JSON file for that release (e.g ``1.12.0.json``).  This
JSON file is a list of all the individual JSON files from ``next-release``.

This is done to simplify changelog generation.

Usage
=====
::
    $ semversioner add-change --type major --description "This description will appear in the change log"
    $ semversioner release
    $ semversioner changelog > CHANGELOG.md
"""

import os
import json
import click
import datetime
from distutils.version import StrictVersion

ROOTDIR = os.getcwd()
INITIAL_VERSION = '0.0.0'


@click.group()
@click.option('--path', default=ROOTDIR)
@click.pass_context
def cli(ctx, path):
    changedir = os.path.join(path, '.changes')
    if not os.path.isdir(changedir):
        os.makedirs(changedir)
    dirname = os.path.join(changedir, 'next-release')
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    ctx.obj['CHANGELOG_DIR'] = changedir


@cli.command('release')
@click.pass_context
def cli_release(ctx):
    release(ctx.obj['CHANGELOG_DIR'])


@cli.command('changelog')
@click.pass_context
def cli_changelog(ctx):
    changedir = ctx.obj['CHANGELOG_DIR']
    click.echo(generate_changelog(changedir))


@cli.command('add-change')
@click.pass_context
@click.option('--type', type=click.Choice(['major', 'minor', 'patch']), required=True)
@click.option('--description', required=True)
def cli_add_change(ctx, type, description):
    changedir = ctx.obj['CHANGELOG_DIR']
    write_new_change(changedir, type, description)


@cli.command('current-version')
@click.pass_context
def cli_current_version(ctx):
    changedir = ctx.obj['CHANGELOG_DIR']
    click.echo(_get_current_version_number(changedir))


def write_new_change(dirname, type, description):

    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    # Assume that new changes go into the next release.
    dirname = os.path.join(dirname, 'next-release')
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    
    parsed_values = {
        'type': type,
        'description': description,
    }

    # Need to generate a unique filename for this change.
    # We'll try a couple things until we get a unique match.
    change_type = parsed_values['type']

    filename = None
    while (filename is None or os.path.isfile(os.path.join(dirname, filename))):
        filename = '{type_name}-{datetime}.json'.format(
            type_name=parsed_values['type'],
            datetime="{:%Y%m%d%H%M%S}".format(datetime.datetime.utcnow()))

    with open(os.path.join(dirname, filename), 'w') as f:
        f.write(json.dumps(parsed_values, indent=2) + "\n")


def generate_changelog(changedir):
    contents = [
        '# Changelog',
        'Note: version releases in the 0.x.y range may introduce breaking changes.',
        '',
    ]
    for release_identifier in _sorted_releases(changedir):
        with open(os.path.join(changedir, release_identifier + '.json')) as f:
            data = json.load(f)
        
        contents.append('## ' + release_identifier)
        contents.append('')
        data = sorted(data, key=lambda k: k['type'] + k['description'])
        for change in data:
            line = '- %s: %s' % (change['type'], change['description'])
            contents.append(line)
        contents.append('')
    return '\n'.join(contents)


def release(changedir):
    changes = []
    next_release_dir = os.path.join(changedir, 'next-release')
    for filename in os.listdir(next_release_dir):
        full_path = os.path.join(next_release_dir, filename)
        with open(full_path) as f:
            changes.append(json.load(f))

    if len(changes) == 0:
        print("No changes to release. Skipping release process.")
        return

    current_version_number = _get_current_version_number(changedir)
    next_version_number = _get_next_version_number(changes, current_version_number)
    print("Current release: %s" % current_version_number)
    print("Next release: %s\n" % next_version_number)
    
    release_json_filename = os.path.join(changedir, '%s.json' % next_version_number)

    print("Generated '" + release_json_filename + "' file")
    with open(release_json_filename, 'w') as f:
        f.write(json.dumps(changes, indent=2, sort_keys=True))

    print("Removing '" + next_release_dir + "' directory")
    for filename in os.listdir(next_release_dir):
        full_path = os.path.join(next_release_dir, filename)
        os.remove(full_path)
    os.rmdir(next_release_dir)


def _sorted_releases(changedir):
    files = [f for f in os.listdir(changedir) if os.path.isfile(os.path.join(changedir, f))]
    releases=list(map(lambda x: x[:-len('.json')], files))
    releases=sorted(releases, key=StrictVersion, reverse=True)
    return releases


def _get_current_version_number(changedir):
    releases = _sorted_releases(changedir)
    if len(releases) > 0:
        return releases[0]
    return INITIAL_VERSION


def _get_next_version_number(changes, current_version_number):
    release_type = sorted(list(map(lambda x: x['type'], changes)))[0]
    return increase_version(current_version_number, release_type)


def increase_version(current_version, release_type):
    """ 
    Returns a string like '1.0.0'.
    """
    # Convert to a list of ints: [1, 0, 0].
    version_parts = list(int(i) for i in current_version.split('.'))
    if release_type == 'patch':
        version_parts[2] += 1
    elif release_type == 'minor':
        version_parts[1] += 1
        version_parts[2] = 0
    elif release_type == 'major':
        version_parts[0] += 1
        version_parts[1] = 0
        version_parts[2] = 0
    return '.'.join(str(i) for i in version_parts)


def main():
    cli(obj={})


if __name__ == '__main__':
    main()