#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of the pycalver project
# https://gitlab.com/mbarkhau/pycalver
#
# Copyright (c) 2019 Manuel Barkhau (mbarkhau@gmail.com) - MIT License
# SPDX-License-Identifier: MIT
"""
CLI module for PyCalVer.

Provided subcommands: show, test, init, bump
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
import click
import logging
import typing as typ
from . import vcs
from . import config
from . import version
from . import rewrite
_VERBOSE = 0
try:
    import backtrace
    backtrace.hook(align=True, strip_path=True, enable_on_envvar_only=True)
except ImportError:
    pass
click.disable_unicode_literals_warning = True
VALID_RELEASE_VALUES = 'alpha', 'beta', 'dev', 'rc', 'post', 'final'
log = logging.getLogger('pycalver.cli')


def _init_logging(verbose=0):
    if verbose >= 2:
        log_format = (
            '%(asctime)s.%(msecs)03d %(levelname)-7s %(name)-15s - %(message)s'
            )
        log_level = logging.DEBUG
    elif verbose == 1:
        log_format = '%(levelname)-7s - %(message)s'
        log_level = logging.INFO
    else:
        log_format = '%(levelname)-7s - %(message)s'
        log_level = logging.INFO
    logging.basicConfig(level=log_level, format=log_format, datefmt=
        '%Y-%m-%dT%H:%M:%S')
    log.debug('Logging initialized.')


def _validate_release_tag(release):
    if release in VALID_RELEASE_VALUES:
        return
    log.error('Invalid argument --release={0}'.format(release))
    log.error('Valid arguments are: {0}'.format(', '.join(
        VALID_RELEASE_VALUES)))
    sys.exit(1)


@click.group()
@click.version_option(version='v201902.0020')
@click.help_option()
@click.option('-v', '--verbose', count=True, help=
    'Control log level. -vv for debug level.')
def cli(verbose=0):
    """Automatically update PyCalVer version strings on python projects."""
    global _VERBOSE
    _VERBOSE = verbose


@cli.command()
@click.argument('old_version')
@click.argument('pattern', default='{pycalver}')
@click.option('-v', '--verbose', count=True, help=
    'Control log level. -vv for debug level.')
@click.option('--release', default=None, metavar='<name>', help=
    'Override release name of current_version')
@click.option('--major', is_flag=True, default=False, help=
    'Increment major component.')
@click.option('--minor', is_flag=True, default=False, help=
    'Increment minor component.')
@click.option('--patch', is_flag=True, default=False, help=
    'Increment patch component.')
def test(old_version, pattern='{pycalver}', verbose=0, release=None, major=
    False, minor=False, patch=False):
    """Increment a version number for demo purposes."""
    _init_logging(verbose=max(_VERBOSE, verbose))
    if release:
        _validate_release_tag(release)
    new_version = version.incr(old_version, pattern=pattern, release=
        release, major=major, minor=minor, patch=patch)
    if new_version is None:
        log.error("Invalid version '{0}' and/or pattern '{1}'.".format(
            old_version, pattern))
        sys.exit(1)
    pep440_version = version.to_pep440(new_version)
    print('New Version:', new_version)
    print('PEP440     :', pep440_version)


def _update_cfg_from_vcs(cfg, fetch):
    try:
        _vcs = vcs.get_vcs()
        log.debug('vcs found: {0}'.format(_vcs.name))
        if fetch:
            log.info(
                'fetching tags from remote (to turn off use: -n / --no-fetch)'
                .format())
            _vcs.fetch()
        version_tags = [tag for tag in _vcs.ls_tags() if version.is_valid(
            tag, cfg.version_pattern)]
        if version_tags:
            version_tags.sort(reverse=True)
            log.debug('found {0} tags: {1}'.format(len(version_tags),
                version_tags[:2]))
            latest_version_tag = version_tags[0]
            latest_version_pep440 = version.to_pep440(latest_version_tag)
            if latest_version_tag > cfg.current_version:
                log.info('Working dir version        : {0}'.format(cfg.
                    current_version))
                log.info('Latest version from {0:>3} tag: {1}'.format(_vcs.
                    name, latest_version_tag))
                cfg = cfg._replace(current_version=latest_version_tag,
                    pep440_version=latest_version_pep440)
        else:
            log.debug('no vcs tags found')
    except OSError:
        log.debug('No vcs found')
    return cfg


@cli.command()
@click.option('-v', '--verbose', count=True, help=
    'Control log level. -vv for debug level.')
@click.option('-f/-n', '--fetch/--no-fetch', is_flag=True, default=True,
    help='Sync tags from remote origin.')
def show(verbose=0, fetch=True):
    """Show current version."""
    _init_logging(verbose=max(_VERBOSE, verbose))
    ctx = config.init_project_ctx(project_path='.')
    cfg = config.parse(ctx)
    if cfg is None:
        log.error("Could not parse configuration. Perhaps try 'pycalver init'."
            )
        sys.exit(1)
    cfg = _update_cfg_from_vcs(cfg, fetch=fetch)
    print('Current Version: {0}'.format(cfg.current_version))
    print('PEP440         : {0}'.format(cfg.pep440_version))


@cli.command()
@click.option('-v', '--verbose', count=True, help=
    'Control log level. -vv for debug level.')
@click.option('--dry', default=False, is_flag=True, help=
    "Display diff of changes, don't rewrite files.")
def init(verbose=0, dry=False):
    """Initialize [pycalver] configuration."""
    _init_logging(verbose=max(_VERBOSE, verbose))
    ctx = config.init_project_ctx(project_path='.')
    cfg = config.parse(ctx)
    if cfg:
        log.error('Configuration already initialized in {0}'.format(ctx.
            config_filepath))
        sys.exit(1)
    if dry:
        print("Exiting because of '--dry'. Would have written to {0}:".
            format(ctx.config_filepath))
        cfg_text = config.default_config(ctx)
        print('\n    ' + '\n    '.join(cfg_text.splitlines()))
        sys.exit(0)
    config.write_content(ctx)


def _assert_not_dirty(vcs, filepaths, allow_dirty):
    dirty_files = vcs.status()
    if dirty_files:
        log.warning('{0} working directory is not clean:'.format(vcs.name))
        for dirty_file in dirty_files:
            log.warning('    ' + dirty_file)
    if not allow_dirty and dirty_files:
        sys.exit(1)
    dirty_pattern_files = set(dirty_files) & filepaths
    if dirty_pattern_files:
        log.error('Not commiting when pattern files are dirty:')
        for dirty_file in dirty_pattern_files:
            log.warning('    ' + dirty_file)
        sys.exit(1)


def _bump(cfg, new_version, allow_dirty=False):
    _vcs = None
    try:
        _vcs = vcs.get_vcs()
    except OSError:
        log.warning('Version Control System not found, aborting commit.')
        _vcs = None
    filepaths = set(cfg.file_patterns.keys())
    if _vcs:
        _assert_not_dirty(_vcs, filepaths, allow_dirty)
    rewrite.rewrite(new_version, cfg.file_patterns)
    if _vcs is None or not cfg.commit:
        return
    for filepath in filepaths:
        _vcs.add(filepath)
    _vcs.commit('bump version to {0}'.format(new_version))
    if cfg.commit and cfg.tag:
        _vcs.tag(new_version)
    if cfg.commit and cfg.tag and cfg.push:
        _vcs.push(new_version)


@cli.command()
@click.option('-v', '--verbose', count=True, help=
    'Control log level. -vv for debug level.')
@click.option('-f/-n', '--fetch/--no-fetch', is_flag=True, default=True,
    help='Sync tags from remote origin.')
@click.option('--dry', default=False, is_flag=True, help=
    "Display diff of changes, don't rewrite files.")
@click.option('--release', default=None, metavar='<name>', help=
    'Override release name of current_version. Valid options are: {0}.'.
    format(', '.join(VALID_RELEASE_VALUES)))
@click.option('--allow-dirty', default=False, is_flag=True, help=
    'Commit even when working directory is has uncomitted changes. (WARNING: The commit will still be aborted if there are uncomitted to files with version strings.'
    )
@click.option('--major', is_flag=True, default=False, help=
    'Increment major component.')
@click.option('--minor', is_flag=True, default=False, help=
    'Increment minor component.')
@click.option('--patch', is_flag=True, default=False, help=
    'Increment patch component.')
def bump(release=None, verbose=0, dry=False, allow_dirty=False, fetch=True,
    major=False, minor=False, patch=False):
    """Increment the current version string and update project files."""
    verbose = max(_VERBOSE, verbose)
    _init_logging(verbose)
    if release:
        _validate_release_tag(release)
    ctx = config.init_project_ctx(project_path='.')
    cfg = config.parse(ctx)
    if cfg is None:
        log.error("Could not parse configuration. Perhaps try 'pycalver init'."
            )
        sys.exit(1)
    cfg = _update_cfg_from_vcs(cfg, fetch=fetch)
    old_version = cfg.current_version
    new_version = version.incr(old_version, pattern=cfg.version_pattern,
        release=release, major=major, minor=minor, patch=patch)
    if new_version is None:
        log.error("Invalid version '{0}' and/or pattern '{1}'.".format(
            old_version, cfg.version_pattern))
        sys.exit(1)
    log.info('Old Version: {0}'.format(old_version))
    log.info('New Version: {0}'.format(new_version))
    if dry or verbose >= 2:
        print(rewrite.diff(new_version, cfg.file_patterns))
    if dry:
        return
    _bump(cfg, new_version, allow_dirty)
